#!/usr/bin/env python3
"""
할일 트리 새로고침 중복 누적 문제 테스트
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, MagicMock
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.todo_tree import TodoTree
from models.todo import Todo
from models.subtask import SubTask
from datetime import datetime


class TestTodoTreeRefresh(unittest.TestCase):
    """할일 트리 새로고침 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 윈도우 숨기기
        
        # Mock TodoService 생성
        self.mock_todo_service = Mock()
        self.mock_todo_service.get_all_todos.return_value = []
        self.mock_todo_service.update_todo_expansion_state = Mock()
        
        # 테스트용 프레임 생성
        self.test_frame = tk.Frame(self.root)
        
        # TodoTree 인스턴스 생성
        self.todo_tree = TodoTree(self.test_frame, self.mock_todo_service)
    
    def tearDown(self):
        """테스트 정리"""
        try:
            self.root.destroy()
        except:
            pass
    
    def create_test_todo(self, todo_id: int, title: str, completed: bool = False) -> Todo:
        """테스트용 할일 생성"""
        todo = Todo(
            id=todo_id,
            title=title,
            created_at=datetime.now(),
            folder_path=f"todo_{todo_id}",
            is_expanded=False
        )
        
        if completed:
            # 완료된 할일로 설정
            subtask = SubTask(
                id=todo_id * 10,
                todo_id=todo_id,
                title=f"{title} 하위작업",
                is_completed=True,
                created_at=datetime.now()
            )
            todo.subtasks = [subtask]
        
        return todo
    
    def test_populate_tree_clears_existing_data(self):
        """populate_tree가 기존 데이터를 지우는지 테스트"""
        # 첫 번째 할일 리스트 추가
        todos1 = [
            self.create_test_todo(1, "첫 번째 할일"),
            self.create_test_todo(2, "두 번째 할일")
        ]
        
        self.todo_tree.populate_tree(todos1)
        
        # 트리에 2개의 항목이 있는지 확인
        children1 = self.todo_tree.get_children()
        self.assertEqual(len(children1), 2)
        self.assertEqual(len(self.todo_tree.todo_nodes), 2)
        
        # 두 번째 할일 리스트로 교체
        todos2 = [
            self.create_test_todo(3, "세 번째 할일"),
            self.create_test_todo(4, "네 번째 할일"),
            self.create_test_todo(5, "다섯 번째 할일")
        ]
        
        self.todo_tree.populate_tree(todos2)
        
        # 트리에 3개의 항목만 있는지 확인 (중복 없음)
        children2 = self.todo_tree.get_children()
        self.assertEqual(len(children2), 3)
        self.assertEqual(len(self.todo_tree.todo_nodes), 3)
        
        # 이전 할일들이 제거되었는지 확인
        self.assertNotIn(1, self.todo_tree.todo_nodes)
        self.assertNotIn(2, self.todo_tree.todo_nodes)
        
        # 새로운 할일들이 추가되었는지 확인
        self.assertIn(3, self.todo_tree.todo_nodes)
        self.assertIn(4, self.todo_tree.todo_nodes)
        self.assertIn(5, self.todo_tree.todo_nodes)
    
    def test_refresh_tree_clears_existing_data(self):
        """refresh_tree가 기존 데이터를 지우는지 테스트"""
        # Mock 데이터 설정
        todos = [
            self.create_test_todo(1, "테스트 할일 1"),
            self.create_test_todo(2, "테스트 할일 2")
        ]
        self.mock_todo_service.get_all_todos.return_value = todos
        
        # 첫 번째 새로고침
        self.todo_tree.refresh_tree()
        children1 = self.todo_tree.get_children()
        self.assertEqual(len(children1), 2)
        
        # 두 번째 새로고침 (같은 데이터)
        self.todo_tree.refresh_tree()
        children2 = self.todo_tree.get_children()
        self.assertEqual(len(children2), 2)  # 중복되지 않음
        
        # 데이터 변경 후 새로고침
        new_todos = [
            self.create_test_todo(3, "새로운 할일")
        ]
        self.mock_todo_service.get_all_todos.return_value = new_todos
        
        self.todo_tree.refresh_tree()
        children3 = self.todo_tree.get_children()
        self.assertEqual(len(children3), 1)  # 새로운 데이터만 표시
    
    def test_progress_widgets_cleanup(self):
        """진행률 위젯이 제대로 정리되는지 테스트"""
        # 하위작업이 있는 할일 생성
        todo = self.create_test_todo(1, "진행률 테스트 할일")
        subtask = SubTask(
            id=10,
            todo_id=1,
            title="하위작업",
            is_completed=False,
            created_at=datetime.now()
        )
        todo.subtasks = [subtask]
        
        # 첫 번째 populate
        self.todo_tree.populate_tree([todo])
        initial_widget_count = len(self.todo_tree.progress_widgets)
        
        # 두 번째 populate (같은 데이터)
        self.todo_tree.populate_tree([todo])
        final_widget_count = len(self.todo_tree.progress_widgets)
        
        # 위젯 개수가 중복되지 않았는지 확인
        self.assertEqual(initial_widget_count, final_widget_count)
    
    def test_node_data_cleanup(self):
        """노드 데이터가 제대로 정리되는지 테스트"""
        # 테스트 데이터 생성
        todos = [
            self.create_test_todo(1, "테스트 할일 1"),
            self.create_test_todo(2, "테스트 할일 2")
        ]
        
        # 첫 번째 populate
        self.todo_tree.populate_tree(todos)
        self.assertEqual(len(self.todo_tree.todo_nodes), 2)
        self.assertEqual(len(self.todo_tree.node_data), 2)
        
        # 새로운 데이터로 populate
        new_todos = [
            self.create_test_todo(3, "새로운 할일")
        ]
        
        self.todo_tree.populate_tree(new_todos)
        
        # 이전 데이터가 정리되었는지 확인
        self.assertEqual(len(self.todo_tree.todo_nodes), 1)
        self.assertEqual(len(self.todo_tree.node_data), 1)
        self.assertIn(3, self.todo_tree.todo_nodes)
        self.assertNotIn(1, self.todo_tree.todo_nodes)
        self.assertNotIn(2, self.todo_tree.todo_nodes)


if __name__ == '__main__':
    unittest.main()