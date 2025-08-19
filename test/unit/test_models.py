#!/usr/bin/env python3
"""
Unit tests for model classes (Todo, SubTask)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
from datetime import datetime, timedelta
from models.todo import Todo
from models.subtask import SubTask


class TestTodoModel(unittest.TestCase):
    """Todo 모델 단위 테스트"""
    
    def test_todo_creation(self):
        """할일 생성 테스트"""
        todo = Todo(1, "테스트 할일", datetime.now(), "test_folder")
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.title, "테스트 할일")
        self.assertIsNotNone(todo.created_at)
        self.assertEqual(todo.folder_path, "test_folder")
        self.assertIsNone(todo.completed_at)
        self.assertEqual(len(todo.subtasks), 0)
    
    def test_todo_completion(self):
        """할일 완료 상태 테스트"""
        todo = Todo(1, "테스트 할일", datetime.now(), "test_folder")
        self.assertFalse(todo.is_completed())
        
        # 완료 처리
        todo.completed_at = datetime.now()
        self.assertTrue(todo.is_completed())
    
    def test_todo_progress_calculation(self):
        """할일 진행률 계산 테스트"""
        todo = Todo(1, "테스트 할일", datetime.now(), "test_folder")
        
        # 하위작업이 없는 경우
        self.assertEqual(todo.get_completion_rate(), 0.0)
        
        # 하위작업 추가
        subtask1 = SubTask(1, 1, "하위작업 1", False, datetime.now())
        subtask2 = SubTask(2, 1, "하위작업 2", True, datetime.now())
        todo.subtasks = [subtask1, subtask2]
        
        # 50% 완료
        self.assertEqual(todo.get_completion_rate(), 0.5)
    
    def test_todo_due_date_handling(self):
        """할일 목표 날짜 처리 테스트"""
        todo = Todo(1, "테스트 할일", datetime.now(), "test_folder")
        
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=1)
        todo.due_date = due_date
        self.assertEqual(todo.due_date, due_date)
        
        # 목표 날짜 없음
        todo.due_date = None
        self.assertIsNone(todo.due_date)


class TestSubTaskModel(unittest.TestCase):
    """SubTask 모델 단위 테스트"""
    
    def test_subtask_creation(self):
        """하위작업 생성 테스트"""
        subtask = SubTask(1, 1, "테스트 하위작업", False, datetime.now())
        self.assertEqual(subtask.id, 1)
        self.assertEqual(subtask.todo_id, 1)
        self.assertEqual(subtask.title, "테스트 하위작업")
        self.assertFalse(subtask.is_completed)
        self.assertIsNotNone(subtask.created_at)
    
    def test_subtask_completion(self):
        """하위작업 완료 상태 테스트"""
        subtask = SubTask(1, 1, "테스트 하위작업", False, datetime.now())
        self.assertFalse(subtask.is_completed)
        
        # 완료 처리
        subtask.is_completed = True
        self.assertTrue(subtask.is_completed)


if __name__ == "__main__":
    unittest.main()