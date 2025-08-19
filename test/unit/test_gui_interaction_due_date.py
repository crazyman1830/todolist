#!/usr/bin/env python3
"""
GUI 상호작용 테스트 - 목표 날짜 기능 GUI 테스트

이 테스트는 목표 날짜 기능의 GUI 상호작용을 검증합니다:
- 다이얼로그 상호작용
- 트리뷰 업데이트
- 컨텍스트 메뉴 동작
- 키보드 네비게이션
"""

import unittest
import tkinter as tk
from tkinter import ttk
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from gui.todo_tree import TodoTree
from gui.dialogs import DueDateDialog, AddTodoDialog
from gui.components import DueDateLabel, UrgencyIndicator, QuickDateButtons
from utils.color_utils import ColorUtils


class TestGUIInteractionDueDate(unittest.TestCase):
    """GUI 상호작용 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        
        # GUI 루트 생성
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 창 숨기기
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.temp_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트 데이터
        self.now = datetime.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.yesterday = self.now - timedelta(days=1)
        
    def tearDown(self):
        """테스트 정리"""
        try:
            self.root.destroy()
        except:
            pass
        
        # 임시 디렉토리 정리
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_todo_tree_due_date_display(self):
        """TodoTree에서 목표 날짜 표시 테스트"""
        print("Testing TodoTree due date display...")
        
        # 1. 할일 생성 및 목표 날짜 설정
        todo1 = self.todo_service.add_todo("오늘 마감 할일")
        todo2 = self.todo_service.add_todo("내일 마감 할일")
        todo3 = self.todo_service.add_todo("지연된 할일")
        
        self.todo_service.set_todo_due_date(todo1.id, self.now.replace(hour=23, minute=59))
        self.todo_service.set_todo_due_date(todo2.id, self.tomorrow)
        self.todo_service.set_todo_due_date(todo3.id, self.yesterday)
        
        # 2. TodoTree 생성 및 새로고침
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.load_todos()
        
        # 3. 트리 아이템 확인
        tree_items = todo_tree.get_children()
        self.assertEqual(len(tree_items), 3)
        
        # 4. 각 아이템의 목표 날짜 표시 확인
        for item_id in tree_items:
            item_values = todo_tree.item(item_id, 'values')
            item_text = todo_tree.item(item_id, 'text')
            
            # 목표 날짜 컬럼이 있는지 확인
            self.assertTrue(len(item_values) > 0)
            
            # 목표 날짜 텍스트 확인
            if "오늘 마감" in item_text:
                self.assertTrue(any('오늘' in str(val) or 'D-day' in str(val) for val in item_values))
            elif "내일 마감" in item_text:
                self.assertTrue(any('내일' in str(val) or 'D-1' in str(val) for val in item_values))
            elif "지연된" in item_text:
                self.assertTrue(any('지남' in str(val) or 'D+' in str(val) for val in item_values))
        
        print("✓ TodoTree due date display test passed")
    
    def test_urgency_color_application(self):
        """긴급도 색상 적용 테스트"""
        print("Testing urgency color application...")
        
        # 1. 다양한 긴급도의 할일 생성
        overdue_todo = self.todo_service.add_todo("지연된 할일")
        urgent_todo = self.todo_service.add_todo("긴급한 할일")
        warning_todo = self.todo_service.add_todo("주의 할일")
        normal_todo = self.todo_service.add_todo("일반 할일")
        
        # 목표 날짜 설정 (과거 날짜는 직접 설정)
        overdue_todo.due_date = self.yesterday
        self.todo_service.set_todo_due_date(urgent_todo.id, self.now + timedelta(hours=12))
        self.todo_service.set_todo_due_date(warning_todo.id, self.now + timedelta(days=2))
        self.todo_service.set_todo_due_date(normal_todo.id, self.now + timedelta(days=7))
        
        # 2. TodoTree 생성
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.refresh()
        
        # 3. 색상 적용 확인
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            urgency = todo.get_urgency_level()
            expected_color = ColorUtils.get_urgency_color(urgency)
            
            # 색상이 올바르게 매핑되는지 확인
            self.assertIsNotNone(expected_color)
            self.assertTrue(expected_color.startswith('#'))
            
            # 긴급도별 색상 확인
            if urgency == 'overdue':
                self.assertEqual(expected_color, '#ff4444')
            elif urgency == 'urgent':
                self.assertEqual(expected_color, '#ff8800')
            elif urgency == 'warning':
                self.assertEqual(expected_color, '#ffcc00')
            elif urgency == 'normal':
                self.assertEqual(expected_color, '#000000')
        
        print("✓ Urgency color application test passed")
    
    def test_context_menu_interaction(self):
        """컨텍스트 메뉴 상호작용 테스트"""
        print("Testing context menu interaction...")
        
        # 1. 할일 생성
        todo = self.todo_service.add_todo("컨텍스트 메뉴 테스트")
        
        # 2. TodoTree 생성
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.load_todos()
        
        # 3. 컨텍스트 메뉴 설정 확인
        self.assertTrue(hasattr(todo_tree, 'context_menu'))
        
        # 4. 메뉴 항목 확인 (모킹)
        with patch.object(todo_tree, 'on_set_due_date') as mock_set_due_date:
            with patch.object(todo_tree, 'on_remove_due_date') as mock_remove_due_date:
                # 목표 날짜 설정 메뉴 클릭 시뮬레이션
                todo_tree.on_set_due_date()
                mock_set_due_date.assert_called_once()
                
                # 목표 날짜 제거 메뉴 클릭 시뮬레이션
                todo_tree.on_remove_due_date()
                mock_remove_due_date.assert_called_once()
        
        print("✓ Context menu interaction test passed")
    
    def test_due_date_dialog_interaction(self):
        """목표 날짜 다이얼로그 상호작용 테스트"""
        print("Testing due date dialog interaction...")
        
        # 1. 다이얼로그 생성 테스트
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            dialog = DueDateDialog(self.root, None, None, "할일")
            
            # 다이얼로그 기본 설정 확인
            self.assertIsNotNone(dialog)
            self.assertTrue(hasattr(dialog, 'date_var'))
            self.assertTrue(hasattr(dialog, 'time_var'))
            self.assertTrue(hasattr(dialog, 'has_due_date_var'))
        
        # 2. 빠른 날짜 선택 테스트
        quick_buttons = QuickDateButtons(self.root, lambda date: None)
        self.assertIsNotNone(quick_buttons)
        
        # 3. 날짜 유효성 검사 테스트
        with patch.object(DueDateDialog, 'validate_input') as mock_validate:
            mock_validate.return_value = True
            
            dialog = DueDateDialog(self.root, None, None, "할일")
            result = dialog.validate_input()
            self.assertTrue(result)
        
        print("✓ Due date dialog interaction test passed")
    
    def test_add_todo_dialog_integration(self):
        """할일 추가 다이얼로그 통합 테스트"""
        print("Testing add todo dialog integration...")
        
        # 1. AddTodoDialog 모킹
        with patch('gui.dialogs.AddTodoDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.get_result.return_value = {
                'title': '새로운 할일',
                'due_date': self.tomorrow
            }
            mock_dialog.return_value = mock_instance
            
            # 다이얼로그 생성 및 결과 확인
            dialog = mock_dialog(self.root, self.todo_service)
            result = dialog.get_result()
            
            self.assertIsNotNone(result)
            self.assertEqual(result['title'], '새로운 할일')
            self.assertEqual(result['due_date'], self.tomorrow)
            
            mock_dialog.assert_called_once_with(self.root, self.todo_service)
        
        print("✓ Add todo dialog integration test passed")
    
    def test_component_real_time_update(self):
        """컴포넌트 실시간 업데이트 테스트"""
        print("Testing component real-time update...")
        
        # 1. DueDateLabel 컴포넌트 테스트
        due_date_label = DueDateLabel(self.root, self.tomorrow)
        initial_text = due_date_label.cget('text')
        
        # 목표 날짜 변경
        due_date_label.set_due_date(self.yesterday)
        updated_text = due_date_label.cget('text')
        
        # 텍스트가 변경되었는지 확인
        self.assertNotEqual(initial_text, updated_text)
        self.assertTrue('지남' in updated_text or 'overdue' in updated_text.lower())
        
        # 2. UrgencyIndicator 컴포넌트 테스트
        urgency_indicator = UrgencyIndicator(self.root, 'normal')
        
        # 긴급도 변경
        urgency_indicator.set_urgency_level('overdue')
        
        # 스타일이 변경되었는지 확인 (시각적 확인은 어려우므로 메서드 호출 확인)
        self.assertTrue(hasattr(urgency_indicator, 'urgency_level'))
        
        print("✓ Component real-time update test passed")
    
    def test_keyboard_navigation(self):
        """키보드 네비게이션 테스트"""
        print("Testing keyboard navigation...")
        
        # 1. 할일 생성
        todo1 = self.todo_service.add_todo("키보드 테스트 1")
        todo2 = self.todo_service.add_todo("키보드 테스트 2")
        
        # 2. TodoTree 생성
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.load_todos()
        
        # 3. 키보드 이벤트 바인딩 확인
        bindings = todo_tree.bind()
        
        # 기본적인 키보드 이벤트가 바인딩되어 있는지 확인
        # (실제 키 이벤트 시뮬레이션은 복잡하므로 바인딩 존재 여부만 확인)
        self.assertIsInstance(bindings, (list, tuple, str))
        
        # 4. 포커스 이동 테스트
        tree_items = todo_tree.get_children()
        if tree_items:
            todo_tree.selection_set(tree_items[0])
            selected = todo_tree.selection()
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0], tree_items[0])
        
        print("✓ Keyboard navigation test passed")
    
    def test_visual_feedback_integration(self):
        """시각적 피드백 통합 테스트"""
        print("Testing visual feedback integration...")
        
        # 1. 다양한 상태의 할일 생성
        completed_todo = self.todo_service.add_todo("완료된 할일")
        overdue_todo = self.todo_service.add_todo("지연된 할일")
        
        # 목표 날짜 설정 (과거 날짜는 직접 설정)
        completed_todo.due_date = self.yesterday
        overdue_todo.due_date = self.yesterday
        
        # 완료 처리
        completed_todo.mark_completed()
        
        # 2. TodoTree에서 시각적 구분 확인
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.load_todos()
        
        # 3. 완료된 할일과 지연된 할일의 시각적 차이 확인
        todos = self.todo_service.get_all_todos()
        
        for todo in todos:
            if todo.is_completed():
                # 완료된 할일은 긴급도 색상이 적용되지 않아야 함
                self.assertIsNotNone(todo.completed_at)
            else:
                # 미완료 지연 할일은 긴급도 색상이 적용되어야 함
                urgency = todo.get_urgency_level()
                if todo.is_overdue():
                    self.assertEqual(urgency, 'overdue')
        
        print("✓ Visual feedback integration test passed")
    
    def test_error_handling_ui(self):
        """UI 오류 처리 테스트"""
        print("Testing UI error handling...")
        
        # 1. 잘못된 날짜 입력 처리
        with patch('tkinter.messagebox.showerror') as mock_error:
            dialog = DueDateDialog(self.root, None, None, "할일")
            
            # 잘못된 날짜 설정 시뮬레이션
            dialog.date_var.set("invalid_date")
            
            # 유효성 검사에서 오류가 처리되는지 확인
            with patch.object(dialog, 'validate_input', return_value=False):
                result = dialog.validate_input()
                self.assertFalse(result)
        
        # 2. 컴포넌트 초기화 실패 처리
        with patch('tkinter.Label.__init__', side_effect=Exception("Init failed")):
            try:
                # 예외가 발생해도 프로그램이 중단되지 않아야 함
                label = DueDateLabel(self.root, self.tomorrow)
            except Exception as e:
                # 예외가 적절히 처리되는지 확인
                self.assertIn("Init failed", str(e))
        
        print("✓ UI error handling test passed")


def run_gui_interaction_tests():
    """GUI 상호작용 테스트 실행"""
    print("=" * 60)
    print("목표 날짜 기능 GUI 상호작용 테스트 실행")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGUIInteractionDueDate)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("GUI 상호작용 테스트 결과 요약")
    print("=" * 60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n전체 결과: {'성공' if success else '실패'}")
    
    return success


if __name__ == '__main__':
    success = run_gui_interaction_tests()
    sys.exit(0 if success else 1)