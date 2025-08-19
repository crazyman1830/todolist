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
from services.todo_service import TodoService
from services.file_service import FileService


class TestDueDateIntegration(unittest.TestCase):
    """목표 날짜 기능 통합 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.storage_service = StorageService(self.test_file, auto_save_enabled=False)
        self.file_service = FileService(self.temp_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
    
    def tearDown(self):
        """테스트 후 정리"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_todo_with_due_date(self):
        """목표 날짜가 있는 할일 생성 및 저장/로드 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        
        # 목표 날짜가 있는 할일 생성
        todo = self.todo_service.add_todo("목표 날짜 할일")
        
        # 목표 날짜 설정
        todo.due_date = due_date
        
        # 저장
        self.todo_service.force_save()
        
        # 새로운 서비스 인스턴스로 데이터 로드
        new_storage = StorageService(self.test_file, auto_save_enabled=False)
        new_file_service = FileService(self.temp_dir)
        new_service = TodoService(new_storage, new_file_service)
        
        # 로드된 데이터 검증
        loaded_todos = new_service.get_all_todos()
        self.assertEqual(len(loaded_todos), 1)
        
        loaded_todo = loaded_todos[0]
        self.assertEqual(loaded_todo.title, "목표 날짜 할일")
        self.assertEqual(loaded_todo.due_date, due_date)
        self.assertIsNone(loaded_todo.completed_at)
    
    def test_create_subtask_with_due_date(self):
        """목표 날짜가 있는 하위 작업 생성 및 저장/로드 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        completed_at = datetime(2025, 1, 14, 16, 30, 0)
        
        # 할일 생성
        todo = self.todo_service.add_todo("상위 할일")
        
        # 하위 작업 생성
        subtask = self.todo_service.add_subtask(todo.id, "목표 날짜 하위 작업")
        
        # 하위 작업에 목표 날짜 설정
        subtask.due_date = due_date
        subtask.is_completed = True
        subtask.completed_at = completed_at
        
        # 저장
        self.todo_service.force_save()
        
        # 새로운 서비스 인스턴스로 데이터 로드
        new_storage = StorageService(self.test_file, auto_save_enabled=False)
        new_file_service = FileService(self.temp_dir)
        new_service = TodoService(new_storage, new_file_service)
        
        # 로드된 데이터 검증
        loaded_todos = new_service.get_all_todos()
        self.assertEqual(len(loaded_todos), 1)
        
        loaded_todo = loaded_todos[0]
        self.assertEqual(len(loaded_todo.subtasks), 1)
        
        loaded_subtask = loaded_todo.subtasks[0]
        self.assertEqual(loaded_subtask.title, "목표 날짜 하위 작업")
        self.assertEqual(loaded_subtask.due_date, due_date)
        self.assertEqual(loaded_subtask.completed_at, completed_at)
        self.assertTrue(loaded_subtask.is_completed)
    
    def test_mixed_todos_with_and_without_due_dates(self):
        """목표 날짜가 있는 할일과 없는 할일이 혼재된 경우 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        
        # 목표 날짜가 없는 할일
        todo1 = self.todo_service.add_todo("일반 할일")
        
        # 목표 날짜가 있는 할일
        todo2 = self.todo_service.add_todo("목표 날짜 할일")
        todo2.due_date = due_date
        
        # 저장
        self.todo_service.force_save()
        
        # 새로운 서비스 인스턴스로 데이터 로드
        new_storage = StorageService(self.test_file, auto_save_enabled=False)
        new_file_service = FileService(self.temp_dir)
        new_service = TodoService(new_storage, new_file_service)
        
        # 로드된 데이터 검증
        loaded_todos = new_service.get_all_todos()
        self.assertEqual(len(loaded_todos), 2)
        
        # 일반 할일 검증
        normal_todo = next(t for t in loaded_todos if t.title == "일반 할일")
        self.assertIsNone(normal_todo.due_date)
        self.assertIsNone(normal_todo.completed_at)
        
        # 목표 날짜 할일 검증
        due_date_todo = next(t for t in loaded_todos if t.title == "목표 날짜 할일")
        self.assertEqual(due_date_todo.due_date, due_date)
        self.assertIsNone(due_date_todo.completed_at)
    
    def test_todo_completion_with_due_date(self):
        """목표 날짜가 있는 할일 완료 처리 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        
        # 목표 날짜가 있는 할일 생성
        todo = self.todo_service.add_todo("완료 테스트 할일")
        todo.due_date = due_date
        
        # 하위 작업 추가
        subtask = self.todo_service.add_subtask(todo.id, "하위 작업")
        
        # 하위 작업 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask.id)
        
        # 완료 시간 설정
        completed_time = datetime.now()
        subtask.completed_at = completed_time
        
        # 할일이 완료되었는지 확인
        self.assertTrue(todo.is_completed())
        
        # 저장 및 로드
        self.todo_service.force_save()
        
        new_storage = StorageService(self.test_file, auto_save_enabled=False)
        new_file_service = FileService(self.temp_dir)
        new_service = TodoService(new_storage, new_file_service)
        
        loaded_todos = new_service.get_all_todos()
        loaded_todo = loaded_todos[0]
        loaded_subtask = loaded_todo.subtasks[0]
        
        # 검증
        self.assertEqual(loaded_todo.due_date, due_date)
        self.assertTrue(loaded_subtask.is_completed)
        self.assertEqual(loaded_subtask.completed_at, completed_time)
        self.assertTrue(loaded_todo.is_completed())


if __name__ == '__main__':
    unittest.main()