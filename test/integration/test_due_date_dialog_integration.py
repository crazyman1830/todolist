"""
목표 날짜 다이얼로그 통합 테스트

DueDateDialog와 기존 시스템의 통합을 테스트합니다.
"""

import unittest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.dialogs import DueDateDialog, show_due_date_dialog
from services.date_service import DateService
from models.todo import Todo
from models.subtask import SubTask


class TestDueDateDialogIntegration(unittest.TestCase):
    """목표 날짜 다이얼로그 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 창을 숨김
        
        # 테스트용 Todo 생성
        self.todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder"
        )
        
        # 테스트용 SubTask 생성
        self.subtask = SubTask(
            id=1,
            todo_id=1,
            title="테스트 하위작업",
            created_at=datetime.now()
        )
    
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    def test_dialog_with_todo_due_date(self):
        """Todo의 목표 날짜와 함께 다이얼로그 테스트"""
        # Todo에 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=5)
        self.todo.set_due_date(due_date)
        
        # 다이얼로그 생성
        dialog = DueDateDialog(self.root, current_due_date=self.todo.get_due_date())
        
        # 다이얼로그가 올바른 날짜로 초기화되었는지 확인
        self.assertTrue(dialog.has_due_date_var.get())
        self.assertEqual(dialog.selected_date, due_date)
        
        dialog.destroy()
    
    def test_dialog_with_subtask_validation(self):
        """SubTask의 목표 날짜 유효성 검사 테스트"""
        # Todo에 목표 날짜 설정
        todo_due_date = datetime.now() + timedelta(days=7)
        self.todo.set_due_date(todo_due_date)
        
        # SubTask 다이얼로그 생성
        dialog = DueDateDialog(
            self.root,
            parent_due_date=self.todo.get_due_date(),
            item_type="하위작업"
        )
        
        # 상위 할일보다 늦은 날짜 설정
        late_date = todo_due_date + timedelta(days=1)
        dialog.selected_date = late_date
        dialog.has_due_date_var.set(True)
        
        # 유효성 검사가 실패해야 함
        self.assertFalse(dialog.validate_input())
        
        # 상위 할일보다 빠른 날짜 설정
        early_date = todo_due_date - timedelta(days=1)
        dialog.selected_date = early_date
        
        # 유효성 검사가 성공해야 함
        self.assertTrue(dialog.validate_input())
        
        dialog.destroy()
    
    def test_date_service_integration(self):
        """DateService와의 통합 테스트"""
        dialog = DueDateDialog(self.root)
        
        # DateService의 빠른 날짜 옵션 사용
        quick_options = DateService.get_quick_date_options()
        
        # "내일" 옵션 테스트
        dialog.set_quick_date("내일")
        expected_date = quick_options["내일"]
        
        self.assertTrue(dialog.has_due_date_var.get())
        self.assertEqual(dialog.selected_date.date(), expected_date.date())
        self.assertEqual(dialog.selected_date.hour, expected_date.hour)
        
        dialog.destroy()
    
    def test_urgency_level_display(self):
        """긴급도 레벨 표시 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 지연된 날짜 설정
        overdue_date = datetime.now() - timedelta(hours=2)
        dialog.selected_date = overdue_date
        dialog.has_due_date_var.set(True)
        
        # 현재 설정 표시 업데이트
        dialog.update_current_setting_display()
        
        # 지연 표시가 포함되어야 함
        display_text = dialog.current_setting_var.get()
        self.assertIn("지남", display_text)
        
        # 미래 날짜 설정
        future_date = datetime.now() + timedelta(days=2)
        dialog.selected_date = future_date
        
        dialog.update_current_setting_display()
        
        # D-day 표시가 포함되어야 함
        display_text = dialog.current_setting_var.get()
        self.assertIn("D-", display_text)
        
        dialog.destroy()
    
    def test_time_remaining_text_integration(self):
        """남은 시간 텍스트 통합 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 24시간 이내 날짜 설정
        urgent_date = datetime.now() + timedelta(hours=3)
        dialog.selected_date = urgent_date
        dialog.has_due_date_var.set(True)
        
        dialog.update_current_setting_display()
        
        # 시간 단위 표시가 포함되어야 함
        display_text = dialog.current_setting_var.get()
        self.assertIn("시간 후", display_text)
        
        dialog.destroy()
    
    def test_validation_with_date_service(self):
        """DateService 유효성 검사 통합 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 유효한 미래 날짜
        valid_date = datetime.now() + timedelta(days=1)
        dialog.selected_date = valid_date
        dialog.has_due_date_var.set(True)
        
        # DateService 유효성 검사 호출
        is_valid, message = DateService.validate_due_date(dialog.selected_date)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
        
        # 다이얼로그 유효성 검사도 성공해야 함
        self.assertTrue(dialog.validate_input())
        
        dialog.destroy()
    
    def test_calendar_with_current_date(self):
        """현재 날짜와 달력 통합 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 현재 날짜가 달력에 올바르게 표시되는지 확인
        now = datetime.now()
        dialog.current_calendar_date = now.replace(day=1)
        
        # 달력 업데이트
        dialog.update_calendar()
        
        # 달력 버튼이 생성되었는지 확인
        self.assertGreater(len(dialog.calendar_buttons), 0)
        
        dialog.destroy()
    
    def test_quick_date_options_integration(self):
        """빠른 날짜 옵션 통합 테스트"""
        dialog = DueDateDialog(self.root)
        
        # DateService의 모든 빠른 옵션 테스트
        quick_options = DateService.get_quick_date_options()
        
        for option_name, expected_date in quick_options.items():
            dialog.set_quick_date(option_name)
            
            # 날짜가 올바르게 설정되었는지 확인
            self.assertTrue(dialog.has_due_date_var.get())
            self.assertEqual(dialog.selected_date.date(), expected_date.date())
            
            # 시간도 올바르게 설정되었는지 확인 (기본 18시)
            if option_name != "이번 주말":  # 주말은 특별 처리
                self.assertEqual(dialog.selected_date.hour, expected_date.hour)
        
        dialog.destroy()


class TestDueDateDialogWithRealModels(unittest.TestCase):
    """실제 모델과의 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    def test_todo_model_integration(self):
        """Todo 모델과의 통합 테스트"""
        # Todo 생성
        todo = Todo(
            id=1,
            title="통합 테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder"
        )
        
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=3)
        todo.set_due_date(due_date)
        
        # 다이얼로그로 수정
        dialog = DueDateDialog(self.root, current_due_date=todo.get_due_date())
        
        # 새로운 날짜 설정
        new_due_date = datetime.now() + timedelta(days=5)
        dialog.selected_date = new_due_date
        dialog.has_due_date_var.set(True)
        
        # 결과 적용
        result = dialog.get_result()
        if result:
            todo.set_due_date(result)
        
        # Todo의 목표 날짜가 업데이트되었는지 확인
        self.assertEqual(todo.get_due_date().date(), new_due_date.date())
        
        dialog.destroy()
    
    def test_subtask_model_integration(self):
        """SubTask 모델과의 통합 테스트"""
        # Todo와 SubTask 생성
        todo = Todo(
            id=1,
            title="상위 할일",
            created_at=datetime.now(),
            folder_path="test_folder"
        )
        
        subtask = SubTask(
            id=1,
            todo_id=1,
            title="하위 작업",
            created_at=datetime.now()
        )
        
        # Todo에 목표 날짜 설정
        todo_due_date = datetime.now() + timedelta(days=7)
        todo.set_due_date(todo_due_date)
        
        # SubTask 다이얼로그
        dialog = DueDateDialog(
            self.root,
            parent_due_date=todo.get_due_date(),
            item_type="하위작업"
        )
        
        # 유효한 하위작업 목표 날짜 설정
        subtask_due_date = todo_due_date - timedelta(days=2)
        dialog.selected_date = subtask_due_date
        dialog.has_due_date_var.set(True)
        
        # 유효성 검사 통과해야 함
        self.assertTrue(dialog.validate_input())
        
        # 결과 적용
        result = dialog.get_result()
        if result:
            subtask.set_due_date(result)
        
        # SubTask의 목표 날짜가 설정되었는지 확인
        self.assertEqual(subtask.get_due_date().date(), subtask_due_date.date())
        
        # 상위 할일보다 빠른지 확인
        self.assertLess(subtask.get_due_date(), todo.get_due_date())
        
        dialog.destroy()


if __name__ == '__main__':
    unittest.main()