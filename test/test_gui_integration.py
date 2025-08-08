import unittest
import tkinter as tk
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService


class TestGUIIntegration(unittest.TestCase):
    """GUI 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Mock TodoService 생성
        self.mock_todo_service = Mock(spec=TodoService)
        
        # 테스트용 데이터 생성
        self.test_subtask = SubTask(
            id=1,
            todo_id=1,
            title="테스트 하위작업",
            is_completed=False,
            created_at=datetime(2025, 1, 8, 10, 0)
        )
        
        self.test_todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime(2025, 1, 8, 9, 0),
            folder_path="todo_folders/todo_1_테스트_할일",
            subtasks=[self.test_subtask],
            is_expanded=True
        )
        
        # Mock 서비스 메서드 설정
        self.mock_todo_service.get_all_todos.return_value = [self.test_todo]
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        self.mock_todo_service.get_subtasks.return_value = [self.test_subtask]
    
    def tearDown(self):
        """테스트 정리"""
        if hasattr(self, 'main_window'):
            self.main_window.root.destroy()
    
    @patch('os.path.exists')
    def test_main_window_with_tree_integration(self, mock_exists):
        """메인 윈도우와 트리 뷰 통합 테스트"""
        # 설정 파일이 없다고 가정
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.mock_todo_service)
        
        # 윈도우가 올바르게 생성되었는지 확인
        self.assertIsNotNone(self.main_window.root)
        self.assertEqual(self.main_window.root.title(), "할일 관리자 - GUI")
        
        # TodoTree가 올바르게 생성되었는지 확인
        self.assertTrue(hasattr(self.main_window, 'todo_tree'))
        self.assertIsNotNone(self.main_window.todo_tree)
        
        # 트리에 데이터가 로드되었는지 확인
        root_children = self.main_window.todo_tree.get_children()
        self.assertEqual(len(root_children), 1)
        
        # 서비스 호출 확인
        self.mock_todo_service.get_all_todos.assert_called()
    
    @patch('os.path.exists')
    def test_status_bar_update_with_tree_data(self, mock_exists):
        """상태바가 트리 데이터와 동기화되는지 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.mock_todo_service)
        
        # 상태바 업데이트
        self.main_window.update_status_bar()
        
        # 상태바 텍스트 확인
        todo_count_text = self.main_window.todo_count_label.cget('text')
        self.assertEqual(todo_count_text, "할일: 1개")
        
        # 완료율 확인 (하위작업이 미완료이므로 0%)
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 0.0%")
    
    @patch('os.path.exists')
    def test_tree_refresh_integration(self, mock_exists):
        """트리 새로고침 통합 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.mock_todo_service)
        
        # 새로고침 실행
        self.main_window.on_refresh()
        
        # 서비스가 다시 호출되었는지 확인 (초기화 시 여러 번 + 새로고침)
        self.assertGreaterEqual(self.mock_todo_service.get_all_todos.call_count, 2)
        
        # 상태 메시지 확인
        status_text = self.main_window.status_message_label.cget('text')
        self.assertEqual(status_text, "데이터가 새로고침되었습니다")
    
    @patch('os.path.exists')
    def test_expand_collapse_integration(self, mock_exists):
        """확장/축소 기능 통합 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.mock_todo_service)
        
        # 트리 노드 확인
        todo_node = self.main_window.todo_tree.todo_nodes[self.test_todo.id]
        
        # 초기 상태 (확장됨)
        self.assertTrue(self.main_window.todo_tree.item(todo_node, 'open'))
        
        # 모든 노드 축소
        self.main_window.on_collapse_all()
        self.assertFalse(self.main_window.todo_tree.item(todo_node, 'open'))
        
        # 모든 노드 확장
        self.main_window.on_expand_all()
        self.assertTrue(self.main_window.todo_tree.item(todo_node, 'open'))


if __name__ == '__main__':
    unittest.main()