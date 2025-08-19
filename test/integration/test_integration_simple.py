#!/usr/bin/env python3
"""
간단한 통합 테스트 - 기본 기능 검증
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime, timedelta
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestIntegrationSimple(unittest.TestCase):
    """간단한 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.temp_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트 데이터
        self.now = datetime.now()
        self.tomorrow = self.now + timedelta(days=1)
        
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_basic_due_date_functionality(self):
        """기본 목표 날짜 기능 테스트"""
        print("Testing basic due date functionality...")
        
        # 1. 할일 생성
        todo = self.todo_service.add_todo("테스트 할일")
        self.assertIsNotNone(todo)
        self.assertIsNone(todo.due_date)
        
        # 2. 목표 날짜 설정
        success = self.todo_service.set_todo_due_date(todo.id, self.tomorrow)
        self.assertTrue(success)
        
        # 3. 목표 날짜 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertIsNotNone(updated_todo.due_date)
        self.assertEqual(updated_todo.due_date.date(), self.tomorrow.date())
        
        # 4. 긴급도 확인
        urgency = updated_todo.get_urgency_level()
        self.assertIn(urgency, ['overdue', 'urgent', 'warning', 'normal'])
        
        print("✓ Basic due date functionality test passed")
    
    def test_data_persistence(self):
        """데이터 지속성 테스트"""
        print("Testing data persistence...")
        
        # 1. 할일 생성 및 목표 날짜 설정
        todo = self.todo_service.add_todo("지속성 테스트")
        self.todo_service.set_todo_due_date(todo.id, self.tomorrow)
        
        # 2. 데이터 저장
        todos = self.todo_service.get_all_todos()
        self.storage_service.save_todos(todos)
        
        # 3. 새로운 서비스로 로드
        new_storage = StorageService(self.data_file)
        new_file_service = FileService(self.temp_dir)
        new_todo_service = TodoService(new_storage, new_file_service)
        
        loaded_todos = new_todo_service.get_all_todos()
        
        # 4. 데이터 검증
        self.assertEqual(len(loaded_todos), 1)
        loaded_todo = loaded_todos[0]
        self.assertEqual(loaded_todo.title, "지속성 테스트")
        self.assertIsNotNone(loaded_todo.due_date)
        self.assertEqual(loaded_todo.due_date.date(), self.tomorrow.date())
        
        print("✓ Data persistence test passed")


def run_simple_tests():
    """간단한 테스트 실행"""
    print("=" * 50)
    print("간단한 통합 테스트 실행")
    print("=" * 50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationSimple)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n결과: {'성공' if success else '실패'}")
    
    return success


if __name__ == '__main__':
    success = run_simple_tests()
    sys.exit(0 if success else 1)