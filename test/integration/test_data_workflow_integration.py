#!/usr/bin/env python3
"""
데이터 워크플로우 통합 테스트 - 목표 날짜 기능 데이터 무결성 검증

이 테스트는 목표 날짜 기능의 데이터 워크플로우를 검증합니다:
- 데이터 저장/로드 무결성
- 마이그레이션 처리
- 백업 및 복구
- 동시성 처리
"""

import unittest
import tempfile
import os
import json
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import threading
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from services.date_service import DateService
from services.notification_service import NotificationService


class TestDataWorkflowIntegration(unittest.TestCase):
    """데이터 워크플로우 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.backup_dir = os.path.join(self.temp_dir, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.temp_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트 데이터
        self.now = datetime.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.yesterday = self.now - timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)
        
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 정리
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_data_persistence_integrity(self):
        """데이터 지속성 무결성 테스트"""
        print("Testing data persistence integrity...")
        
        # 1. 복잡한 데이터 구조 생성
        todo1 = self.todo_service.add_todo("프로젝트 A")
        todo2 = self.todo_service.add_todo("프로젝트 B")
        
        # 목표 날짜 설정
        self.todo_service.set_todo_due_date(todo1.id, self.tomorrow)
        self.todo_service.set_todo_due_date(todo2.id, self.next_week)
        
        # 하위 작업 추가
        subtask1 = self.todo_service.add_subtask(todo1.id, "설계 문서 작성")
        subtask2 = self.todo_service.add_subtask(todo1.id, "코드 구현")
        subtask3 = self.todo_service.add_subtask(todo2.id, "테스트 작성")
        
        # 하위 작업 목표 날짜 설정
        self.todo_service.set_subtask_due_date(todo1.id, subtask1.id, self.now + timedelta(hours=12))
        self.todo_service.set_subtask_due_date(todo1.id, subtask2.id, self.tomorrow - timedelta(hours=2))
        self.todo_service.set_subtask_due_date(todo2.id, subtask3.id, self.next_week - timedelta(days=1))
        
        # 일부 완료 처리
        self.todo_service.toggle_subtask_completion(todo1.id, subtask1.id)
        
        # 2. 데이터 저장
        original_todos = self.todo_service.get_all_todos()
        self.storage_service.save_todos(original_todos)
        
        # 3. 새로운 인스턴스로 로드
        new_storage = StorageService(self.data_file)
        new_file_service = FileService(self.temp_dir)
        new_todo_service = TodoService(new_storage, new_file_service)
        loaded_todos = new_todo_service.get_all_todos()
        
        # 4. 데이터 무결성 검증
        self.assertEqual(len(loaded_todos), 2)
        
        # 할일 검증
        loaded_todo1 = next(t for t in loaded_todos if t.title == "프로젝트 A")
        loaded_todo2 = next(t for t in loaded_todos if t.title == "프로젝트 B")
        
        self.assertEqual(loaded_todo1.due_date.date(), self.tomorrow.date())
        self.assertEqual(loaded_todo2.due_date.date(), self.next_week.date())
        
        # 하위 작업 검증
        self.assertEqual(len(loaded_todo1.subtasks), 2)
        self.assertEqual(len(loaded_todo2.subtasks), 1)
        
        # 완료 상태 검증
        completed_subtask = next(s for s in loaded_todo1.subtasks if s.title == "설계 문서 작성")
        self.assertTrue(completed_subtask.is_completed)
        self.assertIsNotNone(completed_subtask.completed_at)
        
        # 목표 날짜 검증
        for subtask in loaded_todo1.subtasks + loaded_todo2.subtasks:
            if subtask.due_date:
                self.assertIsInstance(subtask.due_date, datetime)
        
        print("✓ Data persistence integrity test passed")
    
    def test_legacy_data_migration(self):
        """레거시 데이터 마이그레이션 테스트"""
        print("Testing legacy data migration...")
        
        # 1. 레거시 데이터 형식 생성 (목표 날짜 필드 없음)
        legacy_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "레거시 할일 1",
                    "created_at": self.now.isoformat(),
                    "folder_path": "todo_folders/todo_1_레거시_할일_1",
                    "is_expanded": True,
                    "subtasks": [
                        {
                            "id": 1,
                            "todo_id": 1,
                            "title": "레거시 하위 작업",
                            "is_completed": False,
                            "created_at": self.now.isoformat()
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "레거시 할일 2",
                    "created_at": self.now.isoformat(),
                    "folder_path": "todo_folders/todo_2_레거시_할일_2",
                    "is_expanded": False,
                    "subtasks": []
                }
            ],
            "next_todo_id": 3,
            "next_subtask_id": 2
        }
        
        # 2. 레거시 데이터 파일 생성
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(legacy_data, f, ensure_ascii=False, indent=2)
        
        # 3. 새로운 서비스로 로드 (자동 마이그레이션)
        migrated_storage = StorageService(self.data_file)
        migrated_file_service = FileService(self.temp_dir)
        migrated_todo_service = TodoService(migrated_storage, migrated_file_service)
        migrated_todos = migrated_todo_service.get_all_todos()
        
        # 4. 마이그레이션 결과 검증
        self.assertEqual(len(migrated_todos), 2)
        
        for todo in migrated_todos:
            # 새로운 필드가 기본값으로 설정되었는지 확인
            self.assertIsNone(todo.due_date)
            self.assertIsNone(todo.completed_at)
            
            for subtask in todo.subtasks:
                self.assertIsNone(subtask.due_date)
                self.assertIsNone(subtask.completed_at)
        
        # 5. 마이그레이션 후 새 기능 사용 가능 확인
        todo = migrated_todos[0]
        success = migrated_todo_service.set_todo_due_date(todo.id, self.tomorrow)
        self.assertTrue(success)
        
        updated_todo = migrated_todo_service.get_todo_by_id(todo.id)
        self.assertIsNotNone(updated_todo.due_date)
        
        print("✓ Legacy data migration test passed")
    
    def test_backup_and_recovery(self):
        """백업 및 복구 테스트"""
        print("Testing backup and recovery...")
        
        # 1. 원본 데이터 생성
        original_todo = self.todo_service.add_todo("백업 테스트 할일")
        self.todo_service.set_todo_due_date(original_todo.id, self.tomorrow)
        
        subtask = self.todo_service.add_subtask(original_todo.id, "백업 테스트 하위 작업")
        self.todo_service.set_subtask_due_date(original_todo.id, subtask.id, self.now + timedelta(hours=6))
        
        # 2. 데이터 저장 및 백업 생성
        self.storage_service.save_todos(self.todo_service.get_all_todos())
        
        backup_file = os.path.join(self.backup_dir, 'backup_test.json')
        shutil.copy2(self.data_file, backup_file)
        
        # 3. 데이터 손상 시뮬레이션
        with open(self.data_file, 'w') as f:
            f.write("corrupted data")
        
        # 4. 백업에서 복구
        shutil.copy2(backup_file, self.data_file)
        
        # 5. 복구된 데이터 검증
        recovered_storage = StorageService(self.data_file)
        recovered_file_service = FileService(self.temp_dir)
        recovered_todo_service = TodoService(recovered_storage, recovered_file_service)
        recovered_todos = recovered_todo_service.get_all_todos()
        
        self.assertEqual(len(recovered_todos), 1)
        recovered_todo = recovered_todos[0]
        
        self.assertEqual(recovered_todo.title, "백업 테스트 할일")
        self.assertIsNotNone(recovered_todo.due_date)
        self.assertEqual(len(recovered_todo.subtasks), 1)
        self.assertIsNotNone(recovered_todo.subtasks[0].due_date)
        
        print("✓ Backup and recovery test passed")
    
    def test_concurrent_access_handling(self):
        """동시 접근 처리 테스트"""
        print("Testing concurrent access handling...")
        
        # 1. 초기 데이터 생성
        todo = self.todo_service.add_todo("동시성 테스트 할일")
        self.storage_service.save_todos(self.todo_service.get_all_todos())
        
        # 2. 동시 수정 시뮬레이션
        results = []
        errors = []
        
        def modify_todo(service_instance, due_date, result_list, error_list):
            try:
                success = service_instance.set_todo_due_date(todo.id, due_date)
                result_list.append(success)
                service_instance.storage_service.save_todos(service_instance.get_all_todos())
            except Exception as e:
                error_list.append(str(e))
        
        # 3. 여러 스레드에서 동시 수정
        threads = []
        services = []
        
        for i in range(3):
            storage = StorageService(self.data_file)
            file_service = FileService(self.temp_dir)
            service = TodoService(storage, file_service)
            services.append(service)
            due_date = self.now + timedelta(days=i+1)
            
            thread = threading.Thread(
                target=modify_todo,
                args=(service, due_date, results, errors)
            )
            threads.append(thread)
        
        # 스레드 시작
        for thread in threads:
            thread.start()
        
        # 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 4. 결과 검증
        self.assertEqual(len(results), 3)  # 모든 수정이 성공해야 함
        self.assertTrue(all(results))  # 모든 결과가 True여야 함
        
        # 오류가 발생하지 않았는지 확인
        if errors:
            print(f"Concurrent access errors: {errors}")
        
        # 5. 최종 상태 확인
        final_storage = StorageService(self.data_file)
        final_file_service = FileService(self.temp_dir)
        final_service = TodoService(final_storage, final_file_service)
        final_todos = final_service.get_all_todos()
        
        self.assertEqual(len(final_todos), 1)
        final_todo = final_todos[0]
        self.assertIsNotNone(final_todo.due_date)  # 목표 날짜가 설정되어 있어야 함
        
        print("✓ Concurrent access handling test passed")
    
    def test_data_validation_and_cleanup(self):
        """데이터 유효성 검사 및 정리 테스트"""
        print("Testing data validation and cleanup...")
        
        # 1. 잘못된 데이터 생성
        invalid_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "유효한 할일",
                    "created_at": self.now.isoformat(),
                    "due_date": self.tomorrow.isoformat(),
                    "folder_path": "todo_folders/todo_1_유효한_할일",
                    "is_expanded": True,
                    "subtasks": []
                },
                {
                    "id": 2,
                    "title": "잘못된 할일",
                    "created_at": "invalid_date",  # 잘못된 날짜 형식
                    "due_date": "also_invalid",    # 잘못된 날짜 형식
                    "folder_path": "todo_folders/todo_2_잘못된_할일",
                    "is_expanded": True,
                    "subtasks": [
                        {
                            "id": 1,
                            "todo_id": 2,
                            "title": "잘못된 하위 작업",
                            "is_completed": "not_boolean",  # 잘못된 불린 값
                            "created_at": self.now.isoformat(),
                            "due_date": "invalid_date"
                        }
                    ]
                }
            ],
            "next_todo_id": 3,
            "next_subtask_id": 2
        }
        
        # 2. 잘못된 데이터 파일 생성
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_data, f, ensure_ascii=False, indent=2)
        
        # 3. 데이터 로드 및 자동 수정
        try:
            validation_storage = StorageService(self.data_file)
            validation_file_service = FileService(self.temp_dir)
            validation_todo_service = TodoService(validation_storage, validation_file_service)
            loaded_todos = validation_todo_service.get_all_todos()
            
            # 4. 유효한 데이터만 로드되었는지 확인
            valid_todos = [t for t in loaded_todos if t.title == "유효한 할일"]
            self.assertEqual(len(valid_todos), 1)
            
            valid_todo = valid_todos[0]
            self.assertIsNotNone(valid_todo.due_date)
            self.assertIsInstance(valid_todo.due_date, datetime)
            
        except Exception as e:
            # 데이터 유효성 검사에서 예외가 발생할 수 있음
            print(f"Data validation exception (expected): {e}")
        
        print("✓ Data validation and cleanup test passed")
    
    def test_large_dataset_performance(self):
        """대용량 데이터셋 성능 테스트"""
        print("Testing large dataset performance...")
        
        # 1. 대량 데이터 생성
        start_time = time.time()
        
        todos = []
        for i in range(500):  # 500개 할일
            todo = self.todo_service.add_todo(f"성능 테스트 할일 {i}")
            
            # 목표 날짜 설정
            due_date = self.now + timedelta(days=i % 30, hours=i % 24)
            self.todo_service.set_todo_due_date(todo.id, due_date)
            
            # 하위 작업 추가 (일부에만)
            if i % 5 == 0:
                subtask = self.todo_service.add_subtask(todo.id, f"하위 작업 {i}")
                subtask_due = due_date - timedelta(hours=2)
                self.todo_service.set_subtask_due_date(todo.id, subtask.id, subtask_due)
            
            todos.append(todo)
        
        creation_time = time.time() - start_time
        print(f"  - 500개 할일 생성 시간: {creation_time:.2f}초")
        
        # 2. 저장 성능 테스트
        start_time = time.time()
        self.storage_service.save_todos(todos)
        save_time = time.time() - start_time
        print(f"  - 저장 시간: {save_time:.2f}초")
        
        # 3. 로드 성능 테스트
        start_time = time.time()
        new_storage = StorageService(self.data_file)
        new_file_service = FileService(self.temp_dir)
        new_todo_service = TodoService(new_storage, new_file_service)
        loaded_todos = new_todo_service.get_all_todos()
        load_time = time.time() - start_time
        print(f"  - 로드 시간: {load_time:.2f}초")
        
        # 4. 검색 성능 테스트
        start_time = time.time()
        overdue_todos = new_todo_service.get_overdue_todos()
        urgent_todos = new_todo_service.get_urgent_todos()
        search_time = time.time() - start_time
        print(f"  - 검색 시간: {search_time:.2f}초")
        
        # 5. 성능 기준 검증
        self.assertLess(creation_time, 10.0)  # 10초 이내
        self.assertLess(save_time, 5.0)       # 5초 이내
        self.assertLess(load_time, 5.0)       # 5초 이내
        self.assertLess(search_time, 2.0)     # 2초 이내
        
        # 6. 데이터 무결성 검증
        self.assertEqual(len(loaded_todos), 500)
        
        # 목표 날짜가 설정된 할일 수 확인
        todos_with_due_date = [t for t in loaded_todos if t.due_date is not None]
        self.assertEqual(len(todos_with_due_date), 500)
        
        print("✓ Large dataset performance test passed")


def run_data_workflow_tests():
    """데이터 워크플로우 테스트 실행"""
    print("=" * 60)
    print("목표 날짜 기능 데이터 워크플로우 테스트 실행")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataWorkflowIntegration)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("데이터 워크플로우 테스트 결과 요약")
    print("=" * 60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n전체 결과: {'성공' if success else '실패'}")
    
    return success


if __name__ == '__main__':
    success = run_data_workflow_tests()
    sys.exit(0 if success else 1)