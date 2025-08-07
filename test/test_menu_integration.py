"""
MenuUI 통합 테스트 - 실제 서비스들과의 연동 테스트
"""

import unittest
import tempfile
import shutil
import os
import sys
from unittest.mock import patch

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.menu import MenuUI
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestMenuIntegration(unittest.TestCase):
    """MenuUI 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.menu_ui = MenuUI(self.todo_service)
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_menu_ui_initialization(self):
        """MenuUI가 실제 서비스들과 올바르게 초기화되는지 테스트"""
        self.assertIsInstance(self.menu_ui.todo_service, TodoService)
        self.assertEqual(self.menu_ui.todo_service, self.todo_service)
    
    @patch('builtins.input', return_value='테스트 할일')
    @patch('builtins.print')
    def test_add_todo_integration(self, mock_print, mock_input):
        """실제 서비스를 통한 할일 추가 통합 테스트"""
        # 할일 추가 실행
        self.menu_ui.handle_add_todo()
        
        # 할일이 실제로 추가되었는지 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, '테스트 할일')
        
        # 폴더가 실제로 생성되었는지 확인
        self.assertTrue(os.path.exists(todos[0].folder_path))
    
    @patch('builtins.print')
    def test_list_empty_todos_integration(self, mock_print):
        """빈 할일 목록 표시 통합 테스트"""
        self.menu_ui.handle_list_todos()
        
        # 개선된 빈 목록 메시지가 출력되어야 함
        mock_print.assert_any_call("                    📭 등록된 할일이 없습니다")
    
    def test_menu_ui_with_existing_data(self):
        """기존 데이터가 있는 상태에서 MenuUI 동작 테스트"""
        # 먼저 할일을 추가
        todo = self.todo_service.add_todo("기존 할일")
        
        # 새로운 MenuUI 인스턴스 생성 (데이터 로드 테스트)
        new_menu_ui = MenuUI(self.todo_service)
        
        # 할일 목록이 올바르게 로드되는지 확인
        with patch('builtins.print') as mock_print:
            new_menu_ui.handle_list_todos()
            
            # 개선된 할일 목록 메시지가 출력되어야 함
            mock_print.assert_any_call("                   총 1개의 할일이 등록되어 있습니다")


if __name__ == '__main__':
    unittest.main()