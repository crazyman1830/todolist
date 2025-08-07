#!/usr/bin/env python3
"""
메인 프로그램 테스트

main.py의 서비스 초기화 및 의존성 주입을 테스트합니다.
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import initialize_services
from services.todo_service import TodoService
from ui.menu import MenuUI


class TestMain(unittest.TestCase):
    """메인 프로그램 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.test_dir, "test_todos.json")
        self.test_folders_dir = os.path.join(self.test_dir, "test_folders")
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('main.TODOS_FILE')
    @patch('main.TODO_FOLDERS_DIR')
    def test_initialize_services_success(self, mock_folders_dir, mock_todos_file):
        """서비스 초기화 성공 테스트"""
        # Mock 설정
        mock_todos_file.return_value = self.test_data_file
        mock_folders_dir.return_value = self.test_folders_dir
        
        # 실제 파일 경로로 패치
        with patch('main.TODOS_FILE', self.test_data_file), \
             patch('main.TODO_FOLDERS_DIR', self.test_folders_dir):
            
            # 서비스 초기화
            todo_service, menu_ui = initialize_services()
            
            # 검증
            self.assertIsInstance(todo_service, TodoService)
            self.assertIsInstance(menu_ui, MenuUI)
            self.assertEqual(menu_ui.todo_service, todo_service)
    
    @patch('main.StorageService')
    def test_initialize_services_storage_failure(self, mock_storage_service):
        """저장 서비스 초기화 실패 테스트"""
        # StorageService 초기화 시 예외 발생하도록 설정
        mock_storage_service.side_effect = Exception("Storage initialization failed")
        
        # 예외 발생 확인
        with self.assertRaises(RuntimeError) as context:
            initialize_services()
        
        self.assertIn("서비스 초기화에 실패했습니다", str(context.exception))
    
    def test_service_dependencies(self):
        """서비스 의존성 주입 테스트"""
        with patch('main.TODOS_FILE', self.test_data_file), \
             patch('main.TODO_FOLDERS_DIR', self.test_folders_dir):
            
            # 서비스 초기화
            todo_service, menu_ui = initialize_services()
            
            # 의존성 확인
            self.assertIsNotNone(todo_service.storage_service)
            self.assertIsNotNone(todo_service.file_service)
            self.assertEqual(menu_ui.todo_service, todo_service)
    
    def test_data_directory_creation(self):
        """데이터 디렉토리 생성 테스트"""
        with patch('main.TODOS_FILE', self.test_data_file), \
             patch('main.TODO_FOLDERS_DIR', self.test_folders_dir):
            
            # 서비스 초기화
            todo_service, menu_ui = initialize_services()
            
            # 디렉토리 생성 확인
            self.assertTrue(os.path.exists(os.path.dirname(self.test_data_file)))
            self.assertTrue(os.path.exists(self.test_folders_dir))


if __name__ == '__main__':
    unittest.main()