import unittest
import os
import sys
import tempfile
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from models.subtask import SubTask
from services.storage_service import StorageService


class TestDueDateSimple(unittest.TestCase):
    """목표 날짜 기능 간단 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.storage_service = StorageService(self.test_file, auto_save_enabled=False)
    
    def tearDown(self):
        """테스트 후 정리"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_todo_with_due_date_save_load(self):
        """목표 날짜가 있는 할일 저장/로드 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        
        # 목표 날짜가 있는 할일 생성
        todo = Todo(
            id=1,
            title="목표 날짜 할일",
            created_at=datetime(2025, 1, 8, 10, 30, 0),
            folder_path="todo_folders/todo_1_목표_날짜_할일",
            due_date=due_date
        )
        
        # 저장
        success = self.storage_service.save_todos([todo])
        self.assertTrue(success)
        
        # 로드
        loaded_todos = self.storage_service.load_todos()
        self.assertEqual(len(loaded_todos), 1)
        
        loaded_todo = loaded_todos[0]
        self.assertEqual(loaded_todo.title, "목표 날짜 할일")
        self.assertEqual(loaded_todo.due_date, due_date)
        self.assertIsNone(loaded_todo.completed_at)
    
    def test_subtask_with_due_date_save_load(self):
        """목표 날짜가 있는 하위 작업 저장/로드 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        completed_at = datetime(2025, 1, 14, 16, 30, 0)
        
        # 하위 작업 생성
        subtask = SubTask(
            id=1,
            todo_id=1,
            title="목표 날짜 하위 작업",
            is_completed=True,
            created_at=datetime(2025, 1, 8, 10, 35, 0),
            due_date=due_date,
            completed_at=completed_at
        )
        
        # 할일 생성
        todo = Todo(
            id=1,
            title="상위 할일",
            created_at=datetime(2025, 1, 8, 10, 30, 0),
            folder_path="todo_folders/todo_1_상위_할일",
            subtasks=[subtask]
        )
        
        # 저장
        success = self.storage_service.save_todos([todo])
        self.assertTrue(success)
        
        # 로드
        loaded_todos = self.storage_service.load_todos()
        self.assertEqual(len(loaded_todos), 1)
        
        loaded_todo = loaded_todos[0]
        self.assertEqual(len(loaded_todo.subtasks), 1)
        
        loaded_subtask = loaded_todo.subtasks[0]
        self.assertEqual(loaded_subtask.title, "목표 날짜 하위 작업")
        self.assertEqual(loaded_subtask.due_date, due_date)
        self.assertEqual(loaded_subtask.completed_at, completed_at)
        self.assertTrue(loaded_subtask.is_completed)
    
    def test_mixed_todos_save_load(self):
        """목표 날짜가 있는 할일과 없는 할일 혼재 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        
        # 목표 날짜가 없는 할일
        todo1 = Todo(
            id=1,
            title="일반 할일",
            created_at=datetime(2025, 1, 8, 10, 30, 0),
            folder_path="todo_folders/todo_1_일반_할일"
        )
        
        # 목표 날짜가 있는 할일
        todo2 = Todo(
            id=2,
            title="목표 날짜 할일",
            created_at=datetime(2025, 1, 8, 11, 0, 0),
            folder_path="todo_folders/todo_2_목표_날짜_할일",
            due_date=due_date
        )
        
        # 저장
        success = self.storage_service.save_todos([todo1, todo2])
        self.assertTrue(success)
        
        # 로드
        loaded_todos = self.storage_service.load_todos()
        self.assertEqual(len(loaded_todos), 2)
        
        # 일반 할일 검증
        normal_todo = next(t for t in loaded_todos if t.title == "일반 할일")
        self.assertIsNone(normal_todo.due_date)
        self.assertIsNone(normal_todo.completed_at)
        
        # 목표 날짜 할일 검증
        due_date_todo = next(t for t in loaded_todos if t.title == "목표 날짜 할일")
        self.assertEqual(due_date_todo.due_date, due_date)
        self.assertIsNone(due_date_todo.completed_at)


if __name__ == '__main__':
    unittest.main()