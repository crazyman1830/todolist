import unittest
import os
import sys
import json
import tempfile
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from models.subtask import SubTask
from services.storage_service import StorageService


class TestDataMigration(unittest.TestCase):
    """데이터 마이그레이션 테스트 클래스"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_todos.json')
    
    def tearDown(self):
        """테스트 후 정리"""
        # 모든 파일 삭제
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_load_legacy_data_without_due_date_fields(self):
        """목표 날짜 필드가 없는 기존 데이터 로드 테스트"""
        # 기존 데이터 형식 (due_date, completed_at 필드 없음)
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
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(legacy_data, f, ensure_ascii=False, indent=2)
        
        # StorageService로 데이터 로드
        storage_service = StorageService(self.test_file)
        todos = storage_service.load_todos()
        
        # 검증
        self.assertEqual(len(todos), 1)
        todo = todos[0]
        
        # Todo 객체 검증
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.title, "기존 할일")
        self.assertIsNone(todo.due_date)  # 새 필드는 None이어야 함
        self.assertIsNone(todo.completed_at)  # 새 필드는 None이어야 함
        
        # SubTask 객체 검증
        self.assertEqual(len(todo.subtasks), 1)
        subtask = todo.subtasks[0]
        self.assertEqual(subtask.id, 1)
        self.assertEqual(subtask.title, "기존 하위 작업")
        self.assertIsNone(subtask.due_date)  # 새 필드는 None이어야 함
        self.assertIsNone(subtask.completed_at)  # 새 필드는 None이어야 함
    
    def test_save_and_load_with_due_date_fields(self):
        """목표 날짜 필드가 포함된 데이터 저장 및 로드 테스트"""
        # 목표 날짜가 포함된 Todo 생성
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        completed_at = datetime(2025, 1, 14, 16, 30, 0)
        
        todo = Todo(
            id=1,
            title="목표 날짜 할일",
            created_at=datetime(2025, 1, 8, 10, 30, 0),
            folder_path="todo_folders/todo_1_목표_날짜_할일",
            due_date=due_date
        )
        
        subtask = SubTask(
            id=1,
            todo_id=1,
            title="목표 날짜 하위 작업",
            is_completed=True,
            created_at=datetime(2025, 1, 8, 10, 35, 0),
            due_date=due_date,
            completed_at=completed_at
        )
        
        todo.add_subtask(subtask)
        
        # StorageService로 데이터 저장
        storage_service = StorageService(self.test_file)
        storage_service.save_todos([todo])
        
        # 데이터 다시 로드
        loaded_todos = storage_service.load_todos()
        
        # 검증
        self.assertEqual(len(loaded_todos), 1)
        loaded_todo = loaded_todos[0]
        
        # Todo 객체 검증
        self.assertEqual(loaded_todo.id, 1)
        self.assertEqual(loaded_todo.title, "목표 날짜 할일")
        self.assertEqual(loaded_todo.due_date, due_date)
        # completed_at은 하위 작업이 완료되어 있어서 자동으로 설정될 수 있음
        if loaded_todo.is_completed():
            self.assertIsNotNone(loaded_todo.completed_at)
        else:
            self.assertIsNone(loaded_todo.completed_at)
        
        # SubTask 객체 검증
        self.assertEqual(len(loaded_todo.subtasks), 1)
        loaded_subtask = loaded_todo.subtasks[0]
        self.assertEqual(loaded_subtask.id, 1)
        self.assertEqual(loaded_subtask.title, "목표 날짜 하위 작업")
        self.assertEqual(loaded_subtask.due_date, due_date)
        self.assertEqual(loaded_subtask.completed_at, completed_at)
    
    def test_mixed_data_compatibility(self):
        """기존 데이터와 새 데이터가 혼재된 경우 테스트"""
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
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(mixed_data, f, ensure_ascii=False, indent=2)
        
        # StorageService로 데이터 로드
        storage_service = StorageService(self.test_file)
        todos = storage_service.load_todos()
        
        # 검증
        self.assertEqual(len(todos), 2)
        
        # 기존 형식 할일 검증
        old_todo = todos[0]
        self.assertEqual(old_todo.id, 1)
        self.assertEqual(old_todo.title, "기존 할일")
        self.assertIsNone(old_todo.due_date)
        self.assertIsNone(old_todo.completed_at)
        
        # 새 형식 할일 검증
        new_todo = todos[1]
        self.assertEqual(new_todo.id, 2)
        self.assertEqual(new_todo.title, "새 할일")
        self.assertEqual(new_todo.due_date, datetime(2025, 1, 15, 18, 0, 0))
        self.assertIsNone(new_todo.completed_at)


if __name__ == '__main__':
    unittest.main()