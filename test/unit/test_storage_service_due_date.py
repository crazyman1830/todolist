import unittest
import os
import json
import tempfile
import shutil
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.storage_service import StorageService
from models.todo import Todo
from models.subtask import SubTask


class TestStorageServiceDueDate(unittest.TestCase):
    """StorageService의 목표 날짜 관련 기능 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.test_dir, 'test_todos.json')
        self.storage_service = StorageService(self.test_file_path, auto_save_enabled=False)
        
        # 목표 날짜가 포함된 테스트 데이터
        self.due_date = datetime(2025, 1, 15, 18, 0, 0)
        self.completed_at = datetime(2025, 1, 14, 16, 30, 0)
        
        self.sample_todo_with_due_date = Todo(
            id=1,
            title="목표 날짜 할일",
            created_at=datetime(2025, 1, 8, 10, 30, 0),
            folder_path="todo_folders/todo_1_목표_날짜_할일",
            due_date=self.due_date
        )
        
        self.sample_subtask_with_due_date = SubTask(
            id=1,
            todo_id=1,
            title="목표 날짜 하위 작업",
            is_completed=True,
            created_at=datetime(2025, 1, 8, 10, 35, 0),
            due_date=self.due_date,
            completed_at=self.completed_at
        )
        
        self.sample_todo_with_due_date.add_subtask(self.sample_subtask_with_due_date)
    
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_and_load_todos_with_due_dates(self):
        """목표 날짜가 포함된 할일 저장 및 로드 테스트"""
        # 저장
        result = self.storage_service.save_todos([self.sample_todo_with_due_date])
        self.assertTrue(result)
        
        # 로드
        loaded_todos = self.storage_service.load_todos()
        
        # 검증
        self.assertEqual(len(loaded_todos), 1)
        loaded_todo = loaded_todos[0]
        
        self.assertEqual(loaded_todo.id, 1)
        self.assertEqual(loaded_todo.title, "목표 날짜 할일")
        self.assertEqual(loaded_todo.due_date, self.due_date)
        # completed_at은 하위 작업이 완료되어 있어서 자동으로 설정될 수 있음
        if loaded_todo.is_completed():
            self.assertIsNotNone(loaded_todo.completed_at)
        else:
            self.assertIsNone(loaded_todo.completed_at)
        
        # 하위 작업 검증
        self.assertEqual(len(loaded_todo.subtasks), 1)
        loaded_subtask = loaded_todo.subtasks[0]
        self.assertEqual(loaded_subtask.due_date, self.due_date)
        self.assertEqual(loaded_subtask.completed_at, self.completed_at)
    
    def test_migrate_legacy_data_without_due_date_fields(self):
        """목표 날짜 필드가 없는 기존 데이터 마이그레이션 테스트"""
        # 기존 데이터 형식 생성
        legacy_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "기존 할일",
                    "created_at": "2025-01-08T10:30:00",
                    "folder_path": "todo_folders/todo_1_기존_할일",
                    "subtasks": [
                        {
                            "id": 1,
                            "todo_id": 1,
                            "title": "기존 하위 작업",
                            "is_completed": False,
                            "created_at": "2025-01-08T10:35:00"
                        }
                    ],
                    "is_expanded": True
                }
            ],
            "next_id": 2,
            "next_subtask_id": 2
        }
        
        # 테스트 파일에 기존 데이터 저장
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            json.dump(legacy_data, f, ensure_ascii=False, indent=2)
        
        # 데이터 로드 (마이그레이션 자동 실행)
        todos = self.storage_service.load_todos()
        
        # 검증
        self.assertEqual(len(todos), 1)
        todo = todos[0]
        
        # 새 필드들이 None으로 설정되었는지 확인
        self.assertIsNone(todo.due_date)
        self.assertIsNone(todo.completed_at)
        
        # 하위 작업도 확인
        self.assertEqual(len(todo.subtasks), 1)
        subtask = todo.subtasks[0]
        self.assertIsNone(subtask.due_date)
        self.assertIsNone(subtask.completed_at)
        
        # 마이그레이션된 파일 확인
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            migrated_data = json.load(f)
        
        # 새 필드들이 추가되었는지 확인
        self.assertIn('data_version', migrated_data)
        self.assertIn('settings', migrated_data)
        self.assertEqual(migrated_data['data_version'], '2.0')
        
        # 할일에 새 필드들이 추가되었는지 확인
        todo_data = migrated_data['todos'][0]
        self.assertIn('due_date', todo_data)
        self.assertIn('completed_at', todo_data)
        self.assertIsNone(todo_data['due_date'])
        self.assertIsNone(todo_data['completed_at'])
        
        # 하위 작업에도 새 필드들이 추가되었는지 확인
        subtask_data = todo_data['subtasks'][0]
        self.assertIn('due_date', subtask_data)
        self.assertIn('completed_at', subtask_data)
        self.assertIsNone(subtask_data['due_date'])
        self.assertIsNone(subtask_data['completed_at'])
    
    def test_validate_due_date_fields(self):
        """목표 날짜 필드 유효성 검사 테스트"""
        # 정상적인 데이터
        validation_result = self.storage_service.validate_due_date_fields([self.sample_todo_with_due_date])
        
        self.assertTrue(validation_result['valid'])
        self.assertEqual(validation_result['statistics']['total_todos'], 1)
        self.assertEqual(validation_result['statistics']['todos_with_due_date'], 1)
        self.assertEqual(validation_result['statistics']['total_subtasks'], 1)
        self.assertEqual(validation_result['statistics']['subtasks_with_due_date'], 1)
    
    def test_validate_due_date_fields_with_invalid_data(self):
        """잘못된 목표 날짜 필드 유효성 검사 테스트"""
        # 잘못된 데이터 생성
        invalid_todo = Todo(
            id=1,
            title="잘못된 할일",
            created_at=datetime.now(),
            folder_path="test_path"
        )
        # 잘못된 타입의 due_date 설정
        invalid_todo.due_date = "2025-01-15"  # 문자열 (datetime이어야 함)
        
        validation_result = self.storage_service.validate_due_date_fields([invalid_todo])
        
        self.assertFalse(validation_result['valid'])
        self.assertTrue(len(validation_result['issues']) > 0)
        self.assertIn("due_date가 datetime 타입이 아님", validation_result['issues'][0])
    
    def test_data_integrity_repair_with_due_dates(self):
        """목표 날짜 관련 데이터 무결성 복구 테스트"""
        # 손상된 데이터 생성
        corrupted_todo = Todo(
            id=1,
            title="손상된 할일",
            created_at=datetime.now(),
            folder_path="test_path"
        )
        # 잘못된 타입의 due_date 설정
        corrupted_todo.due_date = "2025-01-15T18:00:00"  # 문자열
        corrupted_todo.completed_at = "2025-01-14T16:30:00"  # 문자열
        
        # 복구 실행
        repaired_todos = self.storage_service._validate_and_repair_data([corrupted_todo])
        
        # 검증
        self.assertEqual(len(repaired_todos), 1)
        repaired_todo = repaired_todos[0]
        
        # 문자열이 datetime으로 변환되었는지 확인
        self.assertIsInstance(repaired_todo.due_date, datetime)
        self.assertIsInstance(repaired_todo.completed_at, datetime)
        self.assertEqual(repaired_todo.due_date, datetime(2025, 1, 15, 18, 0, 0))
        self.assertEqual(repaired_todo.completed_at, datetime(2025, 1, 14, 16, 30, 0))
    
    def test_export_import_data_with_due_dates(self):
        """목표 날짜 포함 데이터 내보내기/가져오기 테스트"""
        export_path = os.path.join(self.test_dir, 'export_test.json')
        
        # 데이터 내보내기
        result = self.storage_service.export_data_with_due_dates(
            export_path, [self.sample_todo_with_due_date]
        )
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))
        
        # 내보낸 파일 구조 확인
        with open(export_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        self.assertIn('export_info', export_data)
        self.assertIn('todos', export_data)
        self.assertIn('settings', export_data)
        self.assertEqual(export_data['export_info']['version'], '2.0')
        
        # 데이터 가져오기
        imported_todos = self.storage_service.import_data_with_due_dates(export_path)
        
        # 검증
        self.assertEqual(len(imported_todos), 1)
        imported_todo = imported_todos[0]
        
        self.assertEqual(imported_todo.id, 1)
        self.assertEqual(imported_todo.title, "목표 날짜 할일")
        self.assertEqual(imported_todo.due_date, self.due_date)
        
        # 하위 작업도 확인
        self.assertEqual(len(imported_todo.subtasks), 1)
        imported_subtask = imported_todo.subtasks[0]
        self.assertEqual(imported_subtask.due_date, self.due_date)
        self.assertEqual(imported_subtask.completed_at, self.completed_at)
    
    def test_backup_creation_with_due_dates(self):
        """목표 날짜 포함 백업 생성 테스트"""
        # 초기 데이터 저장
        self.storage_service.save_todos([self.sample_todo_with_due_date])
        
        # 백업 파일 경로
        backup_path = f"{self.test_file_path}.backup"
        
        # 새로운 데이터로 다시 저장 (백업 생성 트리거)
        new_todo = Todo(
            id=2,
            title="새로운 할일",
            created_at=datetime.now(),
            folder_path="todo_folders/todo_2",
            due_date=datetime.now() + timedelta(days=7)
        )
        self.storage_service.save_todos([new_todo])
        
        # 백업 파일 존재 확인
        self.assertTrue(os.path.exists(backup_path))
        
        # 백업 파일에 목표 날짜 데이터가 포함되어 있는지 확인
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        self.assertEqual(len(backup_data['todos']), 1)
        backed_up_todo = backup_data['todos'][0]
        self.assertEqual(backed_up_todo['title'], "목표 날짜 할일")
        self.assertEqual(backed_up_todo['due_date'], self.due_date.isoformat())
    
    def test_mixed_data_compatibility(self):
        """기존 데이터와 새 데이터 혼재 테스트"""
        # 기존 형식과 새 형식이 혼재된 데이터
        mixed_data = {
            "todos": [
                {
                    # 기존 형식 (목표 날짜 필드 없음)
                    "id": 1,
                    "title": "기존 할일",
                    "created_at": "2025-01-08T10:30:00",
                    "folder_path": "todo_folders/todo_1_기존_할일",
                    "subtasks": [],
                    "is_expanded": True
                },
                {
                    # 새 형식 (목표 날짜 필드 포함)
                    "id": 2,
                    "title": "새 할일",
                    "created_at": "2025-01-08T11:00:00",
                    "folder_path": "todo_folders/todo_2_새_할일",
                    "subtasks": [],
                    "is_expanded": True,
                    "due_date": "2025-01-15T18:00:00",
                    "completed_at": None
                }
            ],
            "next_id": 3,
            "next_subtask_id": 1
        }
        
        # 테스트 파일에 혼재 데이터 저장
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            json.dump(mixed_data, f, ensure_ascii=False, indent=2)
        
        # 데이터 로드
        todos = self.storage_service.load_todos()
        
        # 검증
        self.assertEqual(len(todos), 2)
        
        # 기존 형식 할일 (마이그레이션됨)
        old_todo = todos[0]
        self.assertEqual(old_todo.id, 1)
        self.assertIsNone(old_todo.due_date)
        self.assertIsNone(old_todo.completed_at)
        
        # 새 형식 할일
        new_todo = todos[1]
        self.assertEqual(new_todo.id, 2)
        self.assertEqual(new_todo.due_date, datetime(2025, 1, 15, 18, 0, 0))
        self.assertIsNone(new_todo.completed_at)
        
        # 다시 저장해서 모든 데이터가 새 형식으로 저장되는지 확인
        self.storage_service.save_todos(todos)
        
        # 파일 내용 확인
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # 모든 할일에 새 필드들이 있는지 확인
        for todo_data in saved_data['todos']:
            self.assertIn('due_date', todo_data)
            self.assertIn('completed_at', todo_data)
        
        # 새로운 메타데이터 필드들 확인
        self.assertIn('data_version', saved_data)
        self.assertIn('settings', saved_data)
        self.assertIn('last_saved', saved_data)
    
    def test_cleanup_old_backups(self):
        """오래된 백업 정리 테스트"""
        # 여러 백업 파일 생성
        backup_files = [
            f"{self.test_file_path}.backup",
            f"{self.test_file_path}.backup.1",
            f"{self.test_file_path}.manual_backup_test"
        ]
        
        for backup_file in backup_files:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump({"test": "data"}, f)
            
            # 파일을 오래된 것으로 만들기 (31일 전)
            old_time = os.path.getmtime(backup_file) - (31 * 24 * 60 * 60)
            os.utime(backup_file, (old_time, old_time))
        
        # 백업 정리 실행
        deleted_count = self.storage_service.cleanup_old_backups(30)
        
        # 검증
        self.assertEqual(deleted_count, 3)
        for backup_file in backup_files:
            self.assertFalse(os.path.exists(backup_file))


if __name__ == '__main__':
    unittest.main()