"""
목표 날짜 설정 다이얼로그 테스트

DueDateDialog의 기본 기능과 유효성 검사를 테스트합니다.
"""

import unittest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# 테스트를 위한 GUI 환경 설정
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.dialogs import DueDateDialog, show_due_date_dialog
from services.date_service import DateService


class TestDueDateDialog(unittest.TestCase):
    """DueDateDialog 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 창을 숨김
        
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    def test_dialog_creation_without_due_date(self):
        """목표 날짜 없이 다이얼로그 생성 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 기본 상태 확인
        self.assertFalse(dialog.has_due_date_var.get())
        self.assertIsNotNone(dialog.selected_date)
        self.assertEqual(dialog.item_type, "할일")
        
        dialog.destroy()
    
    def test_dialog_creation_with_due_date(self):
        """기존 목표 날짜로 다이얼로그 생성 테스트"""
        due_date = datetime.now() + timedelta(days=3)
        dialog = DueDateDialog(self.root, current_due_date=due_date)
        
        # 기본 상태 확인
        self.assertTrue(dialog.has_due_date_var.get())
        self.assertEqual(dialog.selected_date, due_date)
        
        dialog.destroy()
    
    def test_dialog_creation_with_parent_due_date(self):
        """상위 할일 목표 날짜와 함께 다이얼로그 생성 테스트"""
        parent_due_date = datetime.now() + timedelta(days=5)
        dialog = DueDateDialog(self.root, parent_due_date=parent_due_date, item_type="하위작업")
        
        # 기본 상태 확인
        self.assertEqual(dialog.parent_due_date, parent_due_date)
        self.assertEqual(dialog.item_type, "하위작업")
        
        dialog.destroy()
    
    def test_quick_date_selection(self):
        """빠른 날짜 선택 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 초기에는 목표 날짜 없음
        self.assertFalse(dialog.has_due_date_var.get())
        
        # 빠른 날짜 선택
        dialog.set_quick_date("내일")
        
        # 목표 날짜가 설정되었는지 확인
        self.assertTrue(dialog.has_due_date_var.get())
        
        # 내일 날짜가 설정되었는지 확인
        tomorrow = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual(dialog.selected_date.date(), tomorrow.date())
        
        dialog.destroy()
    
    def test_time_setting(self):
        """시간 설정 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 시간 설정
        dialog.set_time(14, 30)
        
        # 시간이 올바르게 설정되었는지 확인
        self.assertEqual(dialog.selected_date.hour, 14)
        self.assertEqual(dialog.selected_date.minute, 30)
        
        dialog.destroy()
    
    def test_due_date_toggle(self):
        """목표 날짜 토글 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 초기 상태: 목표 날짜 없음
        self.assertFalse(dialog.has_due_date_var.get())
        
        # 목표 날짜 활성화
        dialog.has_due_date_var.set(True)
        dialog.on_due_date_toggle()
        
        # 목표 날짜 비활성화
        dialog.has_due_date_var.set(False)
        dialog.on_due_date_toggle()
        
        dialog.destroy()
    
    def test_remove_due_date(self):
        """목표 날짜 제거 테스트"""
        due_date = datetime.now() + timedelta(days=1)
        dialog = DueDateDialog(self.root, current_due_date=due_date)
        
        # 초기에는 목표 날짜 있음
        self.assertTrue(dialog.has_due_date_var.get())
        
        # 목표 날짜 제거
        dialog.remove_due_date()
        
        # 목표 날짜가 제거되었는지 확인
        self.assertFalse(dialog.has_due_date_var.get())
        
        dialog.destroy()
    
    def test_validation_with_valid_date(self):
        """유효한 날짜 검증 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 미래 날짜 설정
        future_date = datetime.now() + timedelta(days=1)
        dialog.selected_date = future_date
        dialog.has_due_date_var.set(True)
        
        # 유효성 검사
        self.assertTrue(dialog.validate_input())
        
        dialog.destroy()
    
    def test_validation_with_past_date(self):
        """과거 날짜 검증 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 과거 날짜 설정 (2시간 전)
        past_date = datetime.now() - timedelta(hours=2)
        dialog.selected_date = past_date
        dialog.has_due_date_var.set(True)
        
        # 유효성 검사 (사용자 확인 다이얼로그를 모킹)
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.assertTrue(dialog.validate_input())
        
        with patch('tkinter.messagebox.askyesno', return_value=False):
            self.assertFalse(dialog.validate_input())
        
        dialog.destroy()
    
    def test_validation_with_parent_due_date_conflict(self):
        """상위 할일 목표 날짜와 충돌하는 경우 검증 테스트"""
        parent_due_date = datetime.now() + timedelta(days=3)
        dialog = DueDateDialog(self.root, parent_due_date=parent_due_date, item_type="하위작업")
        
        # 상위 할일보다 늦은 날짜 설정
        late_date = parent_due_date + timedelta(days=1)
        dialog.selected_date = late_date
        dialog.has_due_date_var.set(True)
        
        # 유효성 검사 실패해야 함
        self.assertFalse(dialog.validate_input())
        
        dialog.destroy()
    
    def test_get_result_with_due_date(self):
        """목표 날짜가 있는 경우 결과 반환 테스트"""
        due_date = datetime.now() + timedelta(days=1)
        dialog = DueDateDialog(self.root, current_due_date=due_date)
        
        # 결과 확인
        result = dialog.get_result()
        self.assertEqual(result, due_date)
        
        dialog.destroy()
    
    def test_get_result_without_due_date(self):
        """목표 날짜가 없는 경우 결과 반환 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 목표 날짜 없음으로 설정
        dialog.has_due_date_var.set(False)
        
        # 결과 확인
        result = dialog.get_result()
        self.assertIsNone(result)
        
        dialog.destroy()
    
    def test_calendar_navigation(self):
        """달력 네비게이션 테스트"""
        dialog = DueDateDialog(self.root)
        
        current_month = dialog.current_calendar_date.month
        current_year = dialog.current_calendar_date.year
        
        # 다음 달로 이동
        dialog.next_month()
        if current_month == 12:
            self.assertEqual(dialog.current_calendar_date.month, 1)
            self.assertEqual(dialog.current_calendar_date.year, current_year + 1)
        else:
            self.assertEqual(dialog.current_calendar_date.month, current_month + 1)
            self.assertEqual(dialog.current_calendar_date.year, current_year)
        
        # 이전 달로 이동 (원래 상태로)
        dialog.prev_month()
        self.assertEqual(dialog.current_calendar_date.month, current_month)
        self.assertEqual(dialog.current_calendar_date.year, current_year)
        
        dialog.destroy()
    
    def test_date_selection(self):
        """날짜 선택 테스트"""
        dialog = DueDateDialog(self.root)
        
        # 초기에는 목표 날짜 없음
        self.assertFalse(dialog.has_due_date_var.get())
        
        # 날짜 선택 (15일)
        dialog.select_date(15)
        
        # 목표 날짜가 활성화되고 날짜가 설정되었는지 확인
        self.assertTrue(dialog.has_due_date_var.get())
        self.assertEqual(dialog.selected_date.day, 15)
        
        dialog.destroy()


class TestDueDateDialogUtility(unittest.TestCase):
    """DueDateDialog 유틸리티 함수 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 창을 숨김
        
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    @patch('gui.dialogs.DueDateDialog')
    def test_show_due_date_dialog(self, mock_dialog_class):
        """show_due_date_dialog 함수 테스트"""
        # 모킹 설정
        mock_dialog = MagicMock()
        mock_dialog.result = datetime.now() + timedelta(days=1)
        mock_dialog_class.return_value = mock_dialog
        
        # 함수 호출
        result = show_due_date_dialog(self.root)
        
        # 다이얼로그가 생성되고 결과가 반환되었는지 확인
        mock_dialog_class.assert_called_once_with(self.root, None, None, "할일")
        self.root.wait_window.assert_called_once_with(mock_dialog)
        self.assertEqual(result, mock_dialog.result)


if __name__ == '__main__':
    # GUI 테스트를 위한 설정
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        # 수동 테스트 모드
        root = tk.Tk()
        
        def test_dialog():
            result = show_due_date_dialog(root)
            print(f"선택된 날짜: {result}")
        
        def test_dialog_with_current():
            current = datetime.now() + timedelta(days=2)
            result = show_due_date_dialog(root, current_due_date=current)
            print(f"선택된 날짜: {result}")
        
        def test_subtask_dialog():
            parent_due = datetime.now() + timedelta(days=5)
            result = show_due_date_dialog(root, parent_due_date=parent_due, item_type="하위작업")
            print(f"선택된 날짜: {result}")
        
        # 테스트 버튼들
        tk.Button(root, text="새 목표 날짜 설정", command=test_dialog).pack(pady=5)
        tk.Button(root, text="기존 목표 날짜 수정", command=test_dialog_with_current).pack(pady=5)
        tk.Button(root, text="하위작업 목표 날짜", command=test_subtask_dialog).pack(pady=5)
        tk.Button(root, text="종료", command=root.quit).pack(pady=5)
        
        root.mainloop()
    else:
        # 자동 테스트 실행
        unittest.main()