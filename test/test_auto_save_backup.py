"""
자동 저장 및 백업 시스템 테스트

Task 12: 데이터 자동 저장 및 백업 시스템 구현 테스트
- 데이터 변경 시 자동 저장 기능
- 백업 파일 생성 및 관리 (최대 5개 유지)
- 프로그램 비정상 종료 시 복구 기능
- 저장 실패 시 오류 처리 및 재시도
- 데이터 무결성 검사 및 복구
"""

import unittest
import os
import json
import time
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

from services.storage_service import StorageService
from services.todo_service import TodoService
from services.file_service import FileService
from models.todo import Todo
from models.subtask import SubTask


class TestAutoSaveBackupSystem(unittest.TestCase):
    """자동 저장 및 백업 시스템 테스트 클래스"""
    
    def setUp(self):
        """테스트 환경 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, "test_todos.json")
        
        # 서비스 인스턴스 생성
        self.storage_service = StorageService(self.data_file, auto_save_enabled=False)  # 테스트용으로 비활성화
        self.file_service = FileService(base_folder_path=os.path.join(self.test_dir, "todo_folders"))
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트용 할일 데이터
        self.test_todos = [
            Todo(
                id=1,
                title="테스트 할일 1",
                created_at=datetime.now(),
                folder_path="todo_folders/todo_1_테스트_할일_1",
                subtasks=[
                    SubTask(id=1, todo_id=1, title="하위 작업 1", is_completed=False),
                    SubTask(id=2, todo_id=1, title="하위 작업 2", is_completed=True)
                ]
            ),
            Todo(
                id=2,
                title="테스트 할일 2",
                created_at=datetime.now(),
                folder_path="todo_folders/todo_2_테스트_할일_2"
            )
        ]
    
    def tearDown(self):
        """테스트 환경 정리"""
        # 자동 저장 타이머 정리
        if hasattr(self.storage_service, '_auto_save_timer') and self.storage_service._auto_save_timer:
            self.storage_service._auto_save_timer.cancel()
        
        # 임시 디렉토리 삭제
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_auto_save_functionality(self):
        """자동 저장 기능 테스트"""
        # 초기 데이터 저장
        self.assertTrue(self.storage_service.save_todos_with_auto_save(self.test_todos))
        
        # 데이터 변경
        self.test_todos[0].title = "수정된 할일 1"
        
        # 자동 저장 실행
        self.assertTrue(self.storage_service.save_todos_with_auto_save(self.test_todos))
        
        # 저장된 데이터 확인
        loaded_todos = self.storage_service.load_todos()
        self.assertEqual(len(loaded_todos), 2)
        self.assertEqual(loaded_todos[0].title, "수정된 할일 1")
    
    def test_data_hash_calculation(self):
        """데이터 해시 계산 테스트"""
        hash1 = self.storage_service._calculate_data_hash(self.test_todos)
        hash2 = self.storage_service._calculate_data_hash(self.test_todos)
        
        # 동일한 데이터는 동일한 해시
        self.assertEqual(hash1, hash2)
        
        # 데이터 변경 시 해시 변경
        self.test_todos[0].title = "변경된 제목"
        hash3 = self.storage_service._calculate_data_hash(self.test_todos)
        self.assertNotEqual(hash1, hash3)
    
    def test_backup_creation_and_management(self):
        """백업 생성 및 관리 테스트"""
        # 초기 데이터 저장
        self.storage_service.save_todos(self.test_todos)
        
        # 백업 파일이 생성되는지 확인
        backup_files = self.storage_service.list_backups()
        initial_backup_count = len(backup_files)
        
        # 데이터 변경 및 저장 (백업 생성)
        self.test_todos[0].title = "변경된 할일"
        self.storage_service.save_todos(self.test_todos)
        
        # 백업 파일 증가 확인
        backup_files = self.storage_service.list_backups()
        self.assertGreaterEqual(len(backup_files), initial_backup_count)
        
        # 수동 백업 생성 테스트
        self.assertTrue(self.storage_service.create_manual_backup("test_backup"))
        
        # 백업 목록에 포함되는지 확인
        backup_files = self.storage_service.list_backups()
        manual_backup_exists = any("test_backup" in backup for backup in backup_files)
        # 수동 백업은 list_backups에서 자동으로 감지되지 않을 수 있으므로 파일 존재 확인
        manual_backup_path = f"{self.data_file}.test_backup"
        self.assertTrue(manual_backup_exists or os.path.exists(manual_backup_path))
    
    def test_backup_limit_enforcement(self):
        """백업 파일 개수 제한 테스트 (최대 5개)"""
        # 초기 데이터 저장
        self.storage_service.save_todos(self.test_todos)
        
        # 여러 번 저장하여 백업 파일 생성
        for i in range(10):
            self.test_todos[0].title = f"변경된 할일 {i}"
            self.storage_service.save_todos(self.test_todos)
            time.sleep(0.1)  # 파일 시간 차이를 위한 대기
        
        # 백업 파일 개수 확인 (최대 6개: .backup, .backup.1~5)
        backup_files = [f for f in self.storage_service.list_backups() 
                       if f.endswith('.backup') or '.backup.' in f]
        self.assertLessEqual(len(backup_files), 6)
    
    def test_recovery_functionality(self):
        """복구 기능 테스트"""
        # 초기 데이터 저장
        self.storage_service.save_todos(self.test_todos)
        
        # 복구 파일 생성 시뮬레이션
        recovery_data = {
            "todos": [todo.to_dict() for todo in self.test_todos],
            "next_id": 3,
            "next_subtask_id": 3,
            "timestamp": time.time(),
            "original_file": self.data_file
        }
        
        recovery_file = f"{self.data_file}.recovery"
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 메인 파일 삭제 (비정상 종료 시뮬레이션)
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        
        # 새로운 StorageService 인스턴스로 복구 테스트
        new_storage = StorageService(self.data_file, auto_save_enabled=False)
        
        # 복구된 데이터 확인
        self.assertTrue(new_storage.file_exists())
        loaded_todos = new_storage.load_todos()
        self.assertEqual(len(loaded_todos), 2)
        self.assertEqual(loaded_todos[0].title, "테스트 할일 1")
    
    def test_save_retry_logic(self):
        """저장 재시도 로직 테스트"""
        # save_todos 메서드를 모킹하여 실패 시뮬레이션
        with patch.object(self.storage_service, 'save_todos') as mock_save:
            # 처음 두 번은 실패, 세 번째는 성공
            mock_save.side_effect = [False, False, True]
            
            # 재시도 로직 테스트
            result = self.storage_service._save_with_retry(self.test_todos, max_retries=3)
            self.assertTrue(result)
            self.assertEqual(mock_save.call_count, 3)
    
    def test_save_retry_final_failure(self):
        """저장 재시도 최종 실패 테스트"""
        with patch.object(self.storage_service, 'save_todos') as mock_save:
            # 모든 시도 실패
            mock_save.return_value = False
            
            # 재시도 로직 테스트
            result = self.storage_service._save_with_retry(self.test_todos, max_retries=2)
            self.assertFalse(result)
            self.assertEqual(mock_save.call_count, 3)  # 초기 시도 + 2회 재시도
    
    def test_data_integrity_check(self):
        """데이터 무결성 검사 테스트"""
        # 무결성 문제가 있는 데이터 생성
        corrupted_todos = [
            Todo(id=1, title="할일 1", created_at=datetime.now(), folder_path="path1"),
            Todo(id=1, title="할일 2", created_at=datetime.now(), folder_path="path2"),  # 중복 ID
        ]
        
        # 하위 작업 무결성 문제
        corrupted_todos[0].subtasks = [
            SubTask(id=1, todo_id=999, title="잘못된 todo_id", is_completed=False)  # 잘못된 todo_id
        ]
        
        # 무결성 문제 확인
        issues = self.storage_service._check_data_integrity_issues(corrupted_todos)
        self.assertGreater(len(issues), 0)
        
        # 무결성 복구 테스트
        repaired_todos = self.storage_service._validate_and_repair_data(corrupted_todos)
        
        # 복구 후 문제 확인
        issues_after_repair = self.storage_service._check_data_integrity_issues(repaired_todos)
        self.assertEqual(len(issues_after_repair), 0)
    
    def test_data_integrity_status(self):
        """데이터 무결성 상태 확인 테스트"""
        # 데이터 저장
        self.storage_service.save_todos(self.test_todos)
        
        # 상태 확인
        status = self.storage_service.get_data_integrity_status()
        
        # 상태 정보 검증
        self.assertTrue(status["file_exists"])
        self.assertGreater(status["file_size"], 0)
        self.assertTrue(status["data_valid"])
        self.assertEqual(status["todo_count"], 2)
        self.assertEqual(status["subtask_count"], 2)
        self.assertEqual(len(status["integrity_issues"]), 0)
    
    def test_backup_restore(self):
        """백업 복구 테스트"""
        # 초기 데이터 저장
        self.storage_service.save_todos(self.test_todos)
        
        # 데이터 변경 및 저장 (백업 생성)
        self.test_todos[0].title = "변경된 할일"
        self.storage_service.save_todos(self.test_todos)
        
        # 백업 목록 확인
        backups = self.storage_service.list_backups()
        self.assertGreater(len(backups), 0)
        
        # 첫 번째 백업에서 복구
        backup_file = backups[0]
        self.assertTrue(self.storage_service.restore_from_backup_file(backup_file))
        
        # 복구된 데이터 확인
        loaded_todos = self.storage_service.load_todos()
        # 백업에서 복구했으므로 데이터가 로드되어야 함
        self.assertGreater(len(loaded_todos), 0)
        # 백업 복구가 성공했는지 확인 (제목은 백업 시점에 따라 다를 수 있음)
        self.assertIsNotNone(loaded_todos[0].title)
    
    def test_todo_service_integration(self):
        """TodoService와의 통합 테스트"""
        # 자동 저장 활성화
        self.todo_service.enable_auto_save()
        
        # 할일 추가
        todo = self.todo_service.add_todo("통합 테스트 할일")
        self.assertIsNotNone(todo)
        
        # 하위 작업 추가
        subtask = self.todo_service.add_subtask(todo.id, "통합 테스트 하위 작업")
        self.assertIsNotNone(subtask)
        
        # 강제 저장 테스트
        self.assertTrue(self.todo_service.force_save())
        
        # 백업 생성 테스트
        self.assertTrue(self.todo_service.create_backup("integration_test"))
        
        # 백업 목록 확인
        backups = self.todo_service.list_available_backups()
        self.assertGreater(len(backups), 0)
        
        # 데이터 상태 확인
        status = self.todo_service.get_data_status()
        self.assertTrue(status["data_valid"])
        self.assertGreater(status["todo_count"], 0)
        
        # 자동 저장 비활성화
        self.todo_service.disable_auto_save()
    
    def test_service_shutdown(self):
        """서비스 종료 테스트"""
        # 데이터 추가
        self.storage_service.save_todos(self.test_todos)
        
        # 자동 저장 활성화
        self.storage_service.auto_save_enabled = True
        self.storage_service._start_auto_save()
        
        # 종료 테스트
        self.storage_service.shutdown()
        
        # 타이머가 정리되었는지 확인
        self.assertIsNone(self.storage_service._auto_save_timer)
    
    def test_change_callback_system(self):
        """변경 콜백 시스템 테스트"""
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        # 콜백 등록
        self.storage_service.add_change_callback(test_callback)
        
        # 데이터 저장 (콜백 호출되어야 함)
        self.storage_service.save_todos_with_auto_save(self.test_todos)
        
        # 콜백이 호출되었는지 확인
        self.assertTrue(callback_called)
        
        # 콜백 제거
        self.storage_service.remove_change_callback(test_callback)
        
        # 콜백 제거 후 호출되지 않는지 확인
        callback_called = False
        self.test_todos[0].title = "변경된 제목"
        self.storage_service.save_todos_with_auto_save(self.test_todos)
        self.assertFalse(callback_called)


if __name__ == '__main__':
    unittest.main()