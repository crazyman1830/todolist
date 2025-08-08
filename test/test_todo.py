import unittest
import os
import sys
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from models.subtask import SubTask


class TestTodo(unittest.TestCase):
    """확장된 Todo 모델 테스트 클래스"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime(2025, 1, 8, 10, 30, 0),
            folder_path="todo_folders/todo_1_테스트_할일"
        )
        
        self.subtask1 = SubTask(
            id=1,
            todo_id=1,
            title="하위 작업 1",
            is_completed=False,
            created_at=datetime(2025, 1, 8, 10, 35, 0)
        )
        
        self.subtask2 = SubTask(
            id=2,
            todo_id=1,
            title="하위 작업 2",
            is_completed=True,
            created_at=datetime(2025, 1, 8, 10, 40, 0)
        )
    
    def test_todo_initialization_with_defaults(self):
        """Todo 객체가 기본값으로 올바르게 초기화되는지 테스트"""
        self.assertEqual(self.todo.id, 1)
        self.assertEqual(self.todo.title, "테스트 할일")
        self.assertEqual(self.todo.subtasks, [])
        self.assertTrue(self.todo.is_expanded)
    
    def test_get_completion_rate_empty_subtasks(self):
        """하위 작업이 없을 때 완료율이 0.0인지 테스트"""
        self.assertEqual(self.todo.get_completion_rate(), 0.0)
    
    def test_get_completion_rate_with_subtasks(self):
        """하위 작업이 있을 때 완료율이 올바르게 계산되는지 테스트"""
        self.todo.add_subtask(self.subtask1)  # 미완료
        self.todo.add_subtask(self.subtask2)  # 완료
        
        # 2개 중 1개 완료 = 0.5
        self.assertEqual(self.todo.get_completion_rate(), 0.5)
    
    def test_get_completion_rate_all_completed(self):
        """모든 하위 작업이 완료되었을 때 완료율이 1.0인지 테스트"""
        self.subtask1.is_completed = True
        self.todo.add_subtask(self.subtask1)
        self.todo.add_subtask(self.subtask2)
        
        self.assertEqual(self.todo.get_completion_rate(), 1.0)
    
    def test_get_completion_rate_none_completed(self):
        """모든 하위 작업이 미완료일 때 완료율이 0.0인지 테스트"""
        self.subtask2.is_completed = False
        self.todo.add_subtask(self.subtask1)
        self.todo.add_subtask(self.subtask2)
        
        self.assertEqual(self.todo.get_completion_rate(), 0.0)
    
    def test_is_completed_empty_subtasks(self):
        """하위 작업이 없을 때 완료되지 않은 것으로 판단하는지 테스트"""
        self.assertFalse(self.todo.is_completed())
    
    def test_is_completed_all_completed(self):
        """모든 하위 작업이 완료되었을 때 완료된 것으로 판단하는지 테스트"""
        self.subtask1.is_completed = True
        self.todo.add_subtask(self.subtask1)
        self.todo.add_subtask(self.subtask2)
        
        self.assertTrue(self.todo.is_completed())
    
    def test_is_completed_partial_completed(self):
        """일부 하위 작업만 완료되었을 때 미완료로 판단하는지 테스트"""
        self.todo.add_subtask(self.subtask1)  # 미완료
        self.todo.add_subtask(self.subtask2)  # 완료
        
        self.assertFalse(self.todo.is_completed())
    
    def test_add_subtask_success(self):
        """하위 작업 추가가 성공하는지 테스트"""
        self.todo.add_subtask(self.subtask1)
        
        self.assertEqual(len(self.todo.subtasks), 1)
        self.assertEqual(self.todo.subtasks[0], self.subtask1)
    
    def test_add_subtask_wrong_todo_id(self):
        """잘못된 todo_id를 가진 하위 작업 추가 시 오류 발생하는지 테스트"""
        wrong_subtask = SubTask(
            id=3,
            todo_id=999,  # 잘못된 todo_id
            title="잘못된 하위 작업",
            is_completed=False
        )
        
        with self.assertRaises(ValueError) as context:
            self.todo.add_subtask(wrong_subtask)
        
        self.assertIn("does not match Todo id", str(context.exception))
    
    def test_add_subtask_duplicate_id(self):
        """중복된 ID를 가진 하위 작업 추가 시 오류 발생하는지 테스트"""
        self.todo.add_subtask(self.subtask1)
        
        duplicate_subtask = SubTask(
            id=1,  # 중복된 ID
            todo_id=1,
            title="중복 ID 하위 작업",
            is_completed=False
        )
        
        with self.assertRaises(ValueError) as context:
            self.todo.add_subtask(duplicate_subtask)
        
        self.assertIn("already exists", str(context.exception))
    
    def test_remove_subtask_success(self):
        """하위 작업 제거가 성공하는지 테스트"""
        self.todo.add_subtask(self.subtask1)
        self.todo.add_subtask(self.subtask2)
        
        result = self.todo.remove_subtask(1)
        
        self.assertTrue(result)
        self.assertEqual(len(self.todo.subtasks), 1)
        self.assertEqual(self.todo.subtasks[0].id, 2)
    
    def test_remove_subtask_not_found(self):
        """존재하지 않는 하위 작업 제거 시 False 반환하는지 테스트"""
        self.todo.add_subtask(self.subtask1)
        
        result = self.todo.remove_subtask(999)
        
        self.assertFalse(result)
        self.assertEqual(len(self.todo.subtasks), 1)
    
    def test_to_dict_with_subtasks(self):
        """하위 작업이 포함된 Todo 객체의 딕셔너리 직렬화 테스트"""
        self.todo.add_subtask(self.subtask1)
        self.todo.add_subtask(self.subtask2)
        
        result = self.todo.to_dict()
        
        expected = {
            'id': 1,
            'title': "테스트 할일",
            'created_at': "2025-01-08T10:30:00",
            'folder_path': "todo_folders/todo_1_테스트_할일",
            'subtasks': [
                {
                    'id': 1,
                    'todo_id': 1,
                    'title': "하위 작업 1",
                    'is_completed': False,
                    'created_at': "2025-01-08T10:35:00"
                },
                {
                    'id': 2,
                    'todo_id': 1,
                    'title': "하위 작업 2",
                    'is_completed': True,
                    'created_at': "2025-01-08T10:40:00"
                }
            ],
            'is_expanded': True
        }
        
        self.assertEqual(result, expected)
    
    def test_from_dict_with_subtasks(self):
        """하위 작업이 포함된 딕셔너리에서 Todo 객체 역직렬화 테스트"""
        data = {
            'id': 1,
            'title': "테스트 할일",
            'created_at': "2025-01-08T10:30:00",
            'folder_path': "todo_folders/todo_1_테스트_할일",
            'subtasks': [
                {
                    'id': 1,
                    'todo_id': 1,
                    'title': "하위 작업 1",
                    'is_completed': False,
                    'created_at': "2025-01-08T10:35:00"
                }
            ],
            'is_expanded': False
        }
        
        todo = Todo.from_dict(data)
        
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.title, "테스트 할일")
        self.assertEqual(len(todo.subtasks), 1)
        self.assertEqual(todo.subtasks[0].title, "하위 작업 1")
        self.assertFalse(todo.is_expanded)
    
    def test_from_dict_without_subtasks(self):
        """하위 작업이 없는 딕셔너리에서 Todo 객체 역직렬화 테스트 (하위 호환성)"""
        data = {
            'id': 1,
            'title': "테스트 할일",
            'created_at': "2025-01-08T10:30:00",
            'folder_path': "todo_folders/todo_1_테스트_할일"
        }
        
        todo = Todo.from_dict(data)
        
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.title, "테스트 할일")
        self.assertEqual(len(todo.subtasks), 0)
        self.assertTrue(todo.is_expanded)  # 기본값
    
    def test_from_dict_without_is_expanded(self):
        """is_expanded 필드가 없는 딕셔너리에서 기본값 사용하는지 테스트"""
        data = {
            'id': 1,
            'title': "테스트 할일",
            'created_at': "2025-01-08T10:30:00",
            'folder_path': "todo_folders/todo_1_테스트_할일",
            'subtasks': []
        }
        
        todo = Todo.from_dict(data)
        
        self.assertTrue(todo.is_expanded)  # 기본값


if __name__ == '__main__':
    unittest.main()