"""
MenuUI 클래스에 대한 단위 테스트
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.menu import MenuUI
from services.todo_service import TodoService
from models.todo import Todo


class TestMenuUI(unittest.TestCase):
    """MenuUI 클래스 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.mock_todo_service = Mock(spec=TodoService)
        self.menu_ui = MenuUI(self.mock_todo_service)
    
    def test_init(self):
        """MenuUI 초기화 테스트"""
        self.assertEqual(self.menu_ui.todo_service, self.mock_todo_service)
    
    @patch('builtins.input', return_value='test input')
    def test_get_user_input(self, mock_input):
        """사용자 입력 받기 테스트"""
        result = self.menu_ui.get_user_input("Enter something: ")
        self.assertEqual(result, 'test input')
    
    @patch('builtins.input', side_effect=['invalid', 'y'])
    def test_get_user_choice(self, mock_input):
        """사용자 선택 받기 테스트"""
        with patch('builtins.print'):  # 오류 메시지 출력 무시
            result = self.menu_ui.get_user_choice("Choose (y/n): ", ['y', 'n'])
            self.assertEqual(result, 'y')
    
    @patch('builtins.print')
    def test_show_error_message(self, mock_print):
        """오류 메시지 표시 테스트"""
        self.menu_ui.show_error_message("Test error")
        mock_print.assert_called_with("\n❌ 오류: Test error")
    
    @patch('builtins.print')
    def test_show_success_message(self, mock_print):
        """성공 메시지 표시 테스트"""
        self.menu_ui.show_success_message("Test success")
        mock_print.assert_called_with("\n✅ Test success")
    
    @patch('builtins.print')
    def test_show_info_message(self, mock_print):
        """정보 메시지 표시 테스트"""
        self.menu_ui.show_info_message("Test info")
        mock_print.assert_called_with("\n💡 Test info")
    
    @patch('builtins.input', return_value='테스트 할일')
    @patch('builtins.print')
    def test_handle_add_todo_success(self, mock_print, mock_input):
        """할일 추가 성공 테스트"""
        # Mock todo 객체 생성
        mock_todo = Todo(
            id=1,
            title='테스트 할일',
            created_at=datetime.now(),
            folder_path='test/path'
        )
        
        self.mock_todo_service.add_todo.return_value = mock_todo
        
        self.menu_ui.handle_add_todo()
        
        self.mock_todo_service.add_todo.assert_called_once_with('테스트 할일')
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_handle_add_todo_cancel(self, mock_print, mock_input):
        """할일 추가 취소 테스트"""
        self.menu_ui.handle_add_todo()
        
        # add_todo가 호출되지 않아야 함
        self.mock_todo_service.add_todo.assert_not_called()
    
    @patch('builtins.print')
    def test_handle_list_todos_empty(self, mock_print):
        """빈 할일 목록 표시 테스트"""
        self.mock_todo_service.get_all_todos.return_value = []
        
        self.menu_ui.handle_list_todos()
        
        # 개선된 빈 목록 메시지가 출력되어야 함
        mock_print.assert_any_call("                    📭 등록된 할일이 없습니다")
    
    @patch('builtins.print')
    def test_handle_list_todos_with_items(self, mock_print):
        """할일이 있는 목록 표시 테스트"""
        mock_todos = [
            Todo(
                id=1,
                title='테스트 할일 1',
                created_at=datetime(2025, 1, 8, 10, 30),
                folder_path='test/path1'
            ),
            Todo(
                id=2,
                title='테스트 할일 2',
                created_at=datetime(2025, 1, 8, 11, 0),
                folder_path='test/path2'
            )
        ]
        
        self.mock_todo_service.get_all_todos.return_value = mock_todos
        
        self.menu_ui.handle_list_todos()
        
        # 개선된 할일 목록 메시지가 출력되어야 함
        mock_print.assert_any_call("                   총 2개의 할일이 등록되어 있습니다")
    
    @patch('builtins.input', side_effect=['1', '새로운 제목'])
    @patch('builtins.print')
    def test_handle_update_todo_success(self, mock_print, mock_input):
        """할일 수정 성공 테스트"""
        mock_todo = Todo(
            id=1,
            title='기존 제목',
            created_at=datetime.now(),
            folder_path='test/path'
        )
        
        self.mock_todo_service.get_all_todos.return_value = [mock_todo]
        self.mock_todo_service.get_max_todo_id.return_value = 1
        self.mock_todo_service.get_todo_by_id.return_value = mock_todo
        self.mock_todo_service.update_todo.return_value = True
        
        self.menu_ui.handle_update_todo()
        
        self.mock_todo_service.update_todo.assert_called_once_with(1, '새로운 제목')
    
    @patch('builtins.input', side_effect=['1', 'y', 'n'])
    @patch('builtins.print')
    def test_handle_delete_todo_success(self, mock_print, mock_input):
        """할일 삭제 성공 테스트"""
        mock_todo = Todo(
            id=1,
            title='삭제할 할일',
            created_at=datetime.now(),
            folder_path='test/path'
        )
        
        self.mock_todo_service.get_all_todos.return_value = [mock_todo]
        self.mock_todo_service.get_max_todo_id.return_value = 1
        self.mock_todo_service.get_todo_by_id.return_value = mock_todo
        self.mock_todo_service.delete_todo.return_value = True
        
        self.menu_ui.handle_delete_todo()
        
        self.mock_todo_service.delete_todo.assert_called_once_with(1, False)
    
    @patch('builtins.input', side_effect=['1'])
    @patch('builtins.print')
    def test_handle_open_folder_success(self, mock_print, mock_input):
        """할일 폴더 열기 성공 테스트"""
        mock_todo = Todo(
            id=1,
            title='테스트 할일',
            created_at=datetime.now(),
            folder_path='test/path'
        )
        
        mock_file_service = Mock()
        mock_file_service.open_todo_folder.return_value = True
        
        self.mock_todo_service.get_all_todos.return_value = [mock_todo]
        self.mock_todo_service.get_max_todo_id.return_value = 1
        self.mock_todo_service.get_todo_by_id.return_value = mock_todo
        self.mock_todo_service.file_service = mock_file_service
        
        self.menu_ui.handle_open_folder()
        
        mock_file_service.open_todo_folder.assert_called_once_with('test/path')


if __name__ == '__main__':
    unittest.main()