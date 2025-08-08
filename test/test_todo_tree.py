import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock, MagicMock
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.todo_tree import TodoTree
from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService


class TestTodoTree(unittest.TestCase):
    """TodoTree 컴포넌트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Tkinter 루트 윈도우 생성 (테스트용)
        self.root = tk.Tk()
        self.root.withdraw()  # 윈도우 숨기기
        
        # Mock TodoService 생성
        self.mock_todo_service = Mock(spec=TodoService)
        
        # 테스트용 데이터 생성
        self.test_subtask1 = SubTask(
            id=1,
            todo_id=1,
            title="테스트 하위작업 1",
            is_completed=True,
            created_at=datetime(2025, 1, 8, 10, 0)
        )
        
        self.test_subtask2 = SubTask(
            id=2,
            todo_id=1,
            title="테스트 하위작업 2",
            is_completed=False,
            created_at=datetime(2025, 1, 8, 11, 0)
        )
        
        self.test_todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime(2025, 1, 8, 9, 0),
            folder_path="todo_folders/todo_1_테스트_할일",
            subtasks=[self.test_subtask1, self.test_subtask2],
            is_expanded=True
        )
        
        # Mock 서비스 메서드 설정
        self.mock_todo_service.get_all_todos.return_value = [self.test_todo]
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        self.mock_todo_service.get_subtasks.return_value = [self.test_subtask1, self.test_subtask2]
        self.mock_todo_service.toggle_subtask_completion.return_value = True
        
        # 테스트 프레임 생성
        self.test_frame = ttk.Frame(self.root)
        
        # TodoTree 인스턴스 생성
        self.todo_tree = TodoTree(self.test_frame, self.mock_todo_service)
    
    def tearDown(self):
        """테스트 정리"""
        if hasattr(self, 'todo_tree'):
            self.todo_tree.destroy()
        if hasattr(self, 'test_frame'):
            self.test_frame.destroy()
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_tree_initialization(self):
        """트리 초기화 테스트"""
        # 트리가 올바르게 생성되었는지 확인
        self.assertIsInstance(self.todo_tree, ttk.Treeview)
        
        # 컬럼이 올바르게 설정되었는지 확인
        self.assertEqual(self.todo_tree['columns'], ('progress', 'created_at'))
        
        # 초기 데이터 로드 확인
        self.mock_todo_service.get_all_todos.assert_called_once()
    
    def test_populate_tree(self):
        """트리 데이터 채우기 테스트"""
        # 트리에 노드가 추가되었는지 확인
        root_children = self.todo_tree.get_children()
        self.assertEqual(len(root_children), 1)
        
        # 할일 노드 확인
        todo_node = root_children[0]
        self.assertIn(self.test_todo.id, self.todo_tree.todo_nodes)
        self.assertEqual(self.todo_tree.todo_nodes[self.test_todo.id], todo_node)
        
        # 하위작업 노드 확인
        subtask_children = self.todo_tree.get_children(todo_node)
        self.assertEqual(len(subtask_children), 2)
        
        # 하위작업 매핑 확인
        self.assertIn(self.test_subtask1.id, self.todo_tree.subtask_nodes)
        self.assertIn(self.test_subtask2.id, self.todo_tree.subtask_nodes)
    
    def test_todo_icon_selection(self):
        """할일 아이콘 선택 테스트"""
        # 진행 중인 할일 (일부 하위작업 완료)
        icon = self.todo_tree._get_todo_icon(self.test_todo)
        self.assertEqual(icon, "🔄")
        
        # 완료된 할일
        self.test_subtask2.is_completed = True
        icon = self.todo_tree._get_todo_icon(self.test_todo)
        self.assertEqual(icon, "✅")
        
        # 하위작업이 없는 할일
        empty_todo = Todo(
            id=2,
            title="빈 할일",
            created_at=datetime.now(),
            folder_path="test",
            subtasks=[]
        )
        icon = self.todo_tree._get_todo_icon(empty_todo)
        self.assertEqual(icon, "📝")
    
    def test_subtask_icon_selection(self):
        """하위작업 아이콘 선택 테스트"""
        # 완료된 하위작업
        icon = self.todo_tree._get_subtask_icon(self.test_subtask1)
        self.assertEqual(icon, "☑️")
        
        # 미완료 하위작업
        icon = self.todo_tree._get_subtask_icon(self.test_subtask2)
        self.assertEqual(icon, "☐")
    
    def test_progress_formatting(self):
        """진행률 포맷팅 테스트"""
        # 0% 진행률
        formatted = self.todo_tree._format_progress(0.0)
        self.assertEqual(formatted, "0%")
        
        # 50% 진행률
        formatted = self.todo_tree._format_progress(0.5)
        self.assertEqual(formatted, "50%")
        
        # 100% 진행률
        formatted = self.todo_tree._format_progress(1.0)
        self.assertEqual(formatted, "100% ✅")
    
    def test_get_selected_todo_id(self):
        """선택된 할일 ID 가져오기 테스트"""
        # 할일 노드 선택
        todo_node = self.todo_tree.todo_nodes[self.test_todo.id]
        self.todo_tree.selection_set(todo_node)
        
        selected_id = self.todo_tree.get_selected_todo_id()
        self.assertEqual(selected_id, self.test_todo.id)
        
        # 하위작업 노드 선택 (상위 할일 ID 반환)
        subtask_node = self.todo_tree.subtask_nodes[self.test_subtask1.id]
        self.todo_tree.selection_set(subtask_node)
        
        selected_id = self.todo_tree.get_selected_todo_id()
        self.assertEqual(selected_id, self.test_todo.id)
    
    def test_get_selected_subtask_id(self):
        """선택된 하위작업 ID 가져오기 테스트"""
        # 하위작업 노드 선택
        subtask_node = self.todo_tree.subtask_nodes[self.test_subtask1.id]
        self.todo_tree.selection_set(subtask_node)
        
        selected_id = self.todo_tree.get_selected_subtask_id()
        self.assertEqual(selected_id, self.test_subtask1.id)
        
        # 할일 노드 선택 (None 반환)
        todo_node = self.todo_tree.todo_nodes[self.test_todo.id]
        self.todo_tree.selection_set(todo_node)
        
        selected_id = self.todo_tree.get_selected_subtask_id()
        self.assertIsNone(selected_id)
    
    def test_node_type_detection(self):
        """노드 타입 감지 테스트"""
        # 할일 노드
        todo_node = self.todo_tree.todo_nodes[self.test_todo.id]
        self.todo_tree.selection_set(todo_node)
        
        node_type = self.todo_tree.get_selected_node_type()
        self.assertEqual(node_type, 'todo')
        
        # 하위작업 노드
        subtask_node = self.todo_tree.subtask_nodes[self.test_subtask1.id]
        self.todo_tree.selection_set(subtask_node)
        
        node_type = self.todo_tree.get_selected_node_type()
        self.assertEqual(node_type, 'subtask')
    
    def test_refresh_tree(self):
        """트리 새로고침 테스트"""
        # 초기 상태 확인
        initial_children = len(self.todo_tree.get_children())
        
        # 새로운 할일 추가
        new_todo = Todo(
            id=2,
            title="새 할일",
            created_at=datetime.now(),
            folder_path="test",
            subtasks=[]
        )
        self.mock_todo_service.get_all_todos.return_value = [self.test_todo, new_todo]
        
        # 새로고침
        self.todo_tree.refresh_tree()
        
        # 노드 수 증가 확인
        new_children = len(self.todo_tree.get_children())
        self.assertEqual(new_children, 2)
        
        # 서비스 호출 확인
        self.assertEqual(self.mock_todo_service.get_all_todos.call_count, 2)  # 초기화 + 새로고침
    
    def test_expand_collapse_all(self):
        """전체 확장/축소 테스트"""
        # 초기 상태에서 노드가 확장되어 있는지 확인
        todo_node = self.todo_tree.todo_nodes[self.test_todo.id]
        self.assertTrue(self.todo_tree.item(todo_node, 'open'))
        
        # 모든 노드 축소
        self.todo_tree.collapse_all()
        self.assertFalse(self.todo_tree.item(todo_node, 'open'))
        
        # 모든 노드 확장
        self.todo_tree.expand_all()
        self.assertTrue(self.todo_tree.item(todo_node, 'open'))
    
    def test_expansion_state_persistence(self):
        """확장 상태 저장/복원 테스트"""
        # 확장 상태 저장 메서드 호출
        self.todo_tree.save_expansion_states()
        
        # 서비스의 update_todo_expansion_state 메서드가 호출되었는지 확인
        # (Mock 객체이므로 실제 저장은 되지 않지만 호출 여부는 확인 가능)
        self.mock_todo_service.update_todo_expansion_state = Mock(return_value=True)
        
        # 확장 상태 변경 후 저장
        todo_node = self.todo_tree.todo_nodes[self.test_todo.id]
        self.todo_tree.item(todo_node, open=False)
        self.todo_tree.save_expansion_states()
        
        # 복원 테스트
        self.todo_tree.restore_expansion_states()
        
        # 초기 상태로 복원되었는지 확인 (test_todo.is_expanded = True)
        self.assertTrue(self.todo_tree.item(todo_node, 'open'))


if __name__ == '__main__':
    unittest.main()