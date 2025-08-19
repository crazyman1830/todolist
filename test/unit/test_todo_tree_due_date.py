"""
TodoTree 목표 날짜 표시 기능 테스트

Requirements 2.1, 2.2, 3.1, 3.2, 3.3, 5.1, 5.2, 5.3 검증
"""

import unittest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from gui.todo_tree import TodoTree
from services.todo_service import TodoService
from models.todo import Todo
from models.subtask import SubTask


class TestTodoTreeDueDate(unittest.TestCase):
    """TodoTree 목표 날짜 표시 기능 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 창 숨기기
        
        # Mock TodoService
        self.mock_todo_service = Mock(spec=TodoService)
        
        # 테스트용 할일 데이터 생성
        now = datetime.now()
        
        # 지연된 할일
        self.overdue_todo = Todo(
            id=1,
            title="지연된 할일",
            created_at=now - timedelta(days=2),
            folder_path="test_folder_1",
            due_date=now - timedelta(hours=2),  # 2시간 전 마감
            subtasks=[]
        )
        
        # 긴급한 할일 (24시간 이내)
        self.urgent_todo = Todo(
            id=2,
            title="긴급한 할일",
            created_at=now - timedelta(hours=1),
            folder_path="test_folder_2",
            due_date=now + timedelta(hours=12),  # 12시간 후 마감
            subtasks=[]
        )
        
        # 경고 할일 (3일 이내)
        self.warning_todo = Todo(
            id=3,
            title="경고 할일",
            created_at=now - timedelta(hours=1),
            folder_path="test_folder_3",
            due_date=now + timedelta(days=2),  # 2일 후 마감
            subtasks=[]
        )
        
        # 일반 할일
        self.normal_todo = Todo(
            id=4,
            title="일반 할일",
            created_at=now - timedelta(hours=1),
            folder_path="test_folder_4",
            due_date=now + timedelta(days=7),  # 1주일 후 마감
            subtasks=[]
        )
        
        # 목표 날짜가 없는 할일
        self.no_due_date_todo = Todo(
            id=5,
            title="목표 날짜 없는 할일",
            created_at=now - timedelta(hours=1),
            folder_path="test_folder_5",
            due_date=None,
            subtasks=[]
        )
        
        # 완료된 할일
        self.completed_todo = Todo(
            id=6,
            title="완료된 할일",
            created_at=now - timedelta(days=1),
            folder_path="test_folder_6",
            due_date=now - timedelta(hours=1),  # 1시간 전 마감이었지만 완료됨
            completed_at=now - timedelta(minutes=30),
            subtasks=[]
        )
        
        # 하위작업이 있는 할일
        subtask1 = SubTask(
            id=1,
            todo_id=7,
            title="하위작업 1",
            is_completed=False,
            due_date=now + timedelta(hours=6)  # 6시간 후 마감
        )
        
        subtask2 = SubTask(
            id=2,
            todo_id=7,
            title="하위작업 2",
            is_completed=True,
            due_date=now + timedelta(hours=12),  # 12시간 후 마감
            completed_at=now - timedelta(minutes=10)
        )
        
        self.todo_with_subtasks = Todo(
            id=7,
            title="하위작업이 있는 할일",
            created_at=now - timedelta(hours=2),
            folder_path="test_folder_7",
            due_date=now + timedelta(days=1),  # 1일 후 마감
            subtasks=[subtask1, subtask2]
        )
        
        self.test_todos = [
            self.overdue_todo,
            self.urgent_todo,
            self.warning_todo,
            self.normal_todo,
            self.no_due_date_todo,
            self.completed_todo,
            self.todo_with_subtasks
        ]
        
        # Mock 서비스 설정
        self.mock_todo_service.get_all_todos.return_value = self.test_todos
        
        # TodoTree 생성
        self.frame = tk.Frame(self.root)
        self.todo_tree = TodoTree(self.frame, self.mock_todo_service)
    
    def tearDown(self):
        """테스트 정리"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_columns_setup(self):
        """컬럼 설정 테스트 - Requirements 2.1"""
        # 목표 날짜 컬럼이 추가되었는지 확인
        columns = self.todo_tree['columns']
        self.assertIn('due_date', columns)
        
        # 컬럼 순서 확인
        expected_columns = ('progress', 'due_date', 'created_at')
        self.assertEqual(columns, expected_columns)
        
        # 헤딩 텍스트 확인
        heading_text = self.todo_tree.heading('due_date')['text']
        self.assertEqual(heading_text, '목표 날짜')
    
    def test_due_date_display_format(self):
        """목표 날짜 표시 형식 테스트 - Requirements 2.2, 5.1, 5.2, 5.3"""
        # 트리 새로고침하여 데이터 로드
        self.todo_tree.refresh_tree()
        
        # 각 할일의 목표 날짜 표시 확인
        for todo in self.test_todos:
            if todo.id in self.todo_tree.todo_nodes:
                node_id = self.todo_tree.todo_nodes[todo.id]
                values = self.todo_tree.item(node_id)['values']
                
                if len(values) >= 2:
                    due_date_text = values[1]  # 목표 날짜 컬럼
                    
                    if todo.due_date is None:
                        # 목표 날짜가 없는 경우 빈 문자열
                        self.assertEqual(due_date_text, "")
                    elif todo.is_completed():
                        # 완료된 경우 완료 시간 표시
                        self.assertIn("완료:", due_date_text)
                    else:
                        # 미완료인 경우 남은 시간 또는 지연 시간 표시
                        self.assertIsInstance(due_date_text, str)
                        self.assertNotEqual(due_date_text, "")
    
    def test_urgency_level_calculation(self):
        """긴급도 레벨 계산 테스트 - Requirements 3.1, 3.2, 3.3"""
        # 각 할일의 긴급도 레벨 확인
        self.assertEqual(self.overdue_todo.get_urgency_level(), 'overdue')
        self.assertEqual(self.urgent_todo.get_urgency_level(), 'urgent')
        self.assertEqual(self.warning_todo.get_urgency_level(), 'warning')
        self.assertEqual(self.normal_todo.get_urgency_level(), 'normal')
        self.assertEqual(self.no_due_date_todo.get_urgency_level(), 'normal')
        self.assertEqual(self.completed_todo.get_urgency_level(), 'normal')  # 완료된 할일은 normal
    
    def test_urgency_styling_application(self):
        """긴급도 스타일링 적용 테스트 - Requirements 3.1, 3.2, 3.3"""
        # 트리 새로고침하여 데이터 로드
        self.todo_tree.refresh_tree()
        
        # 긴급도별 태그 확인
        for todo in self.test_todos:
            if todo.id in self.todo_tree.todo_nodes:
                node_id = self.todo_tree.todo_nodes[todo.id]
                tags = self.todo_tree.item(node_id)['tags']
                
                if todo.is_completed():
                    self.assertIn('completed', tags)
                else:
                    urgency_level = todo.get_urgency_level()
                    expected_tag = f'urgency_{urgency_level}'
                    self.assertIn(expected_tag, tags)
    
    def test_subtask_due_date_display(self):
        """하위작업 목표 날짜 표시 테스트 - Requirements 7.1, 7.4"""
        # 트리 새로고침하여 데이터 로드
        self.todo_tree.refresh_tree()
        
        # 하위작업의 목표 날짜 표시 확인
        for subtask in self.todo_with_subtasks.subtasks:
            if subtask.id in self.todo_tree.subtask_nodes:
                node_id = self.todo_tree.subtask_nodes[subtask.id]
                values = self.todo_tree.item(node_id)['values']
                
                if len(values) >= 2:
                    due_date_text = values[1]  # 목표 날짜 컬럼
                    
                    if subtask.due_date is None:
                        self.assertEqual(due_date_text, "")
                    elif subtask.is_completed:
                        self.assertIn("완료:", due_date_text)
                    else:
                        self.assertIsInstance(due_date_text, str)
                        self.assertNotEqual(due_date_text, "")
    
    def test_context_menu_due_date_options(self):
        """컨텍스트 메뉴 목표 날짜 옵션 테스트 - Requirements 1.1, 1.2, 6.4, 7.1"""
        # 할일용 컨텍스트 메뉴에 목표 날짜 옵션이 있는지 확인
        todo_menu_labels = []
        for i in range(self.todo_tree.todo_context_menu.index('end') + 1):
            try:
                label = self.todo_tree.todo_context_menu.entrycget(i, 'label')
                todo_menu_labels.append(label)
            except:
                pass  # 구분선 등은 무시
        
        self.assertIn("목표 날짜 설정", todo_menu_labels)
        self.assertIn("목표 날짜 제거", todo_menu_labels)
        
        # 하위작업용 컨텍스트 메뉴에 목표 날짜 옵션이 있는지 확인
        subtask_menu_labels = []
        for i in range(self.todo_tree.subtask_context_menu.index('end') + 1):
            try:
                label = self.todo_tree.subtask_context_menu.entrycget(i, 'label')
                subtask_menu_labels.append(label)
            except:
                pass  # 구분선 등은 무시
        
        self.assertIn("목표 날짜 설정", subtask_menu_labels)
        self.assertIn("목표 날짜 제거", subtask_menu_labels)
    
    def test_color_utils_integration(self):
        """ColorUtils 통합 테스트"""
        # 트리 새로고침하여 데이터 로드
        self.todo_tree.refresh_tree()
        
        # 긴급도 스타일이 설정되었는지 확인
        self.assertTrue(hasattr(self.todo_tree, '_urgency_styles_configured'))
        
        # 각 긴급도별 태그가 설정되었는지 확인
        urgency_levels = ['overdue', 'urgent', 'warning', 'normal']
        for level in urgency_levels:
            tag_name = f'urgency_{level}'
            # 태그가 존재하는지 확인 (tag_configure가 호출되었는지)
            try:
                # Treeview의 tag_configure 메서드를 통해 태그 설정 확인
                config = self.todo_tree.tag_configure(tag_name)
                self.assertIsInstance(config, dict)
                # 태그가 존재하면 성공
            except tk.TclError:
                self.fail(f"긴급도 태그 '{tag_name}'이 설정되지 않았습니다.")
    
    def test_time_remaining_text_format(self):
        """남은 시간 텍스트 형식 테스트 - Requirements 5.1, 5.2, 5.3"""
        # 각 할일의 남은 시간 텍스트 확인
        overdue_text = self.overdue_todo.get_time_remaining_text()
        self.assertIn("지남", overdue_text)  # 지연된 경우
        
        urgent_text = self.urgent_todo.get_time_remaining_text()
        self.assertIn("시간", urgent_text)  # 시간 단위 표시
        
        warning_text = self.warning_todo.get_time_remaining_text()
        self.assertIn("D-", warning_text)  # D-day 형태
        
        normal_text = self.normal_todo.get_time_remaining_text()
        self.assertIn("D-", normal_text)  # D-day 형태
        
        no_due_text = self.no_due_date_todo.get_time_remaining_text()
        self.assertEqual(no_due_text, "")  # 목표 날짜 없음
        
        completed_text = self.completed_todo.get_time_remaining_text()
        self.assertIn("완료:", completed_text)  # 완료 시간 표시


if __name__ == '__main__':
    unittest.main()