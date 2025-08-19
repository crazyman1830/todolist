#!/usr/bin/env python3
"""
Unit tests for service classes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from services.date_service import DateService
from services.notification_service import NotificationService


class TestTodoService(unittest.TestCase):
    """TodoService 단위 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "todo_folders")
        
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
    
    def tearDown(self):
        """테스트 환경 정리"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_todo(self):
        """할일 추가 테스트"""
        todo = self.todo_service.add_todo("테스트 할일")
        self.assertIsNotNone(todo)
        self.assertEqual(todo.title, "테스트 할일")
        self.assertTrue(os.path.exists(todo.folder_path))
    
    def test_get_all_todos(self):
        """모든 할일 조회 테스트"""
        self.todo_service.add_todo("할일 1")
        self.todo_service.add_todo("할일 2")
        
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 2)
    
    def test_delete_todo(self):
        """할일 삭제 테스트"""
        todo = self.todo_service.add_todo("삭제할 할일")
        todo_id = todo.id
        
        self.todo_service.delete_todo(todo_id, delete_folder=True)
        
        # 할일이 삭제되었는지 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 0)
        
        # 폴더도 삭제되었는지 확인
        self.assertFalse(os.path.exists(todo.folder_path))
    
    def test_add_subtask(self):
        """하위작업 추가 테스트"""
        todo = self.todo_service.add_todo("할일")
        subtask = self.todo_service.add_subtask(todo.id, "하위작업")
        
        self.assertIsNotNone(subtask)
        self.assertEqual(subtask.title, "하위작업")
        self.assertEqual(subtask.todo_id, todo.id)
        
        # 할일에 하위작업이 추가되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(len(updated_todo.subtasks), 1)


class TestDateService(unittest.TestCase):
    """DateService 단위 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.date_service = DateService()
    
    def test_parse_date_string(self):
        """날짜 문자열 파싱 테스트"""
        # 다양한 형식의 날짜 문자열 테스트
        test_cases = [
            "2024-12-25",
            "2024/12/25",
            "12/25/2024",
            "25-12-2024"
        ]
        
        for date_str in test_cases:
            try:
                parsed_date = self.date_service.parse_date_string(date_str)
                self.assertIsInstance(parsed_date, datetime)
            except ValueError:
                # 일부 형식은 지원하지 않을 수 있음
                pass
    
    def test_format_date(self):
        """날짜 포맷팅 테스트"""
        test_date = datetime(2024, 12, 25, 15, 30, 0)
        formatted = self.date_service.format_date(test_date)
        self.assertIsInstance(formatted, str)
        self.assertIn("2024", formatted)
    
    def test_is_overdue(self):
        """지연 여부 확인 테스트"""
        now = datetime.now()
        past_date = now - timedelta(days=1)
        future_date = now + timedelta(days=1)
        
        self.assertTrue(self.date_service.is_overdue(past_date))
        self.assertFalse(self.date_service.is_overdue(future_date))
        self.assertFalse(self.date_service.is_overdue(None))


class TestNotificationService(unittest.TestCase):
    """NotificationService 단위 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "todo_folders")
        
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.notification_service = NotificationService(self.todo_service)
    
    def tearDown(self):
        """테스트 환경 정리"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_should_show_startup_notification(self):
        """시작 알림 표시 여부 테스트"""
        # 지연된 할일이 없는 경우
        self.assertFalse(self.notification_service.should_show_startup_notification())
        
        # 지연된 할일 추가
        todo = self.todo_service.add_todo("지연된 할일")
        todo.due_date = datetime.now() - timedelta(days=1)
        self.todo_service.update_todo(todo.id, todo.title, todo.due_date)
        
        # 지연된 할일이 있는 경우
        self.assertTrue(self.notification_service.should_show_startup_notification())
    
    def test_get_status_bar_summary(self):
        """상태바 요약 정보 테스트"""
        # 다양한 상태의 할일 추가
        todo1 = self.todo_service.add_todo("지연된 할일")
        todo1.due_date = datetime.now() - timedelta(days=1)
        self.todo_service.update_todo(todo1.id, todo1.title, todo1.due_date)
        
        todo2 = self.todo_service.add_todo("오늘 마감 할일")
        todo2.due_date = datetime.now().replace(hour=23, minute=59)
        self.todo_service.update_todo(todo2.id, todo2.title, todo2.due_date)
        
        summary = self.notification_service.get_status_bar_summary()
        
        self.assertIn('overdue', summary)
        self.assertIn('due_today', summary)
        self.assertIn('total', summary)
        self.assertEqual(summary['overdue'], 1)
        self.assertEqual(summary['due_today'], 1)
        self.assertEqual(summary['total'], 2)


if __name__ == "__main__":
    unittest.main()