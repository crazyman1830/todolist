#!/usr/bin/env python3
"""
목표 날짜 관련 GUI 컴포넌트들의 단위 테스트

DueDateLabel, UrgencyIndicator, DateTimeWidget, QuickDateButtons 컴포넌트들을 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from gui.components import DueDateLabel, UrgencyIndicator, DateTimeWidget, QuickDateButtons


class TestDueDateLabel(unittest.TestCase):
    """DueDateLabel 컴포넌트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 창 숨기기
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_init_with_due_date(self):
        """목표 날짜가 있는 경우 초기화 테스트"""
        due_date = datetime.now() + timedelta(days=1)
        label = DueDateLabel(self.root, due_date=due_date)
        
        self.assertEqual(label.get_due_date(), due_date)
        self.assertIsNotNone(label.cget('text'))
        self.assertNotEqual(label.cget('text'), '')
    
    def test_init_without_due_date(self):
        """목표 날짜가 없는 경우 초기화 테스트"""
        label = DueDateLabel(self.root, due_date=None)
        
        self.assertIsNone(label.get_due_date())
        self.assertEqual(label.cget('text'), '')
        self.assertEqual(str(label.cget('foreground')), 'gray')
    
    def test_completed_task_display(self):
        """완료된 작업 표시 테스트"""
        due_date = datetime.now() + timedelta(days=1)
        completed_at = datetime.now()
        label = DueDateLabel(self.root, due_date=due_date, completed_at=completed_at)
        
        text = label.cget('text')
        self.assertIn('완료', text)
        self.assertEqual(str(label.cget('foreground')), 'gray')
    
    def test_overdue_task_color(self):
        """지연된 작업 색상 테스트"""
        due_date = datetime.now() - timedelta(days=1)
        label = DueDateLabel(self.root, due_date=due_date)
        
        # 빨간색이어야 함
        color = str(label.cget('foreground'))
        self.assertEqual(color, '#ff4444')
    
    def test_urgent_task_color(self):
        """긴급한 작업 색상 테스트"""
        due_date = datetime.now() + timedelta(hours=12)
        label = DueDateLabel(self.root, due_date=due_date)
        
        # 주황색이어야 함
        color = str(label.cget('foreground'))
        self.assertEqual(color, '#ff8800')
    
    def test_set_due_date(self):
        """목표 날짜 설정 테스트"""
        label = DueDateLabel(self.root, due_date=None)
        
        # 처음에는 빈 텍스트
        self.assertEqual(label.cget('text'), '')
        
        # 목표 날짜 설정
        new_date = datetime.now() + timedelta(days=1)
        label.set_due_date(new_date)
        
        self.assertEqual(label.get_due_date(), new_date)
        self.assertNotEqual(label.cget('text'), '')
    
    def test_update_display(self):
        """표시 업데이트 테스트"""
        label = DueDateLabel(self.root, due_date=None)
        
        # 목표 날짜 설정 후 업데이트
        due_date = datetime.now() + timedelta(days=1)
        label.due_date = due_date
        label.update_display()
        
        self.assertNotEqual(label.cget('text'), '')


class TestUrgencyIndicator(unittest.TestCase):
    """UrgencyIndicator 컴포넌트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_init_normal(self):
        """일반 상태 초기화 테스트"""
        indicator = UrgencyIndicator(self.root, urgency_level='normal')
        
        self.assertEqual(indicator.get_urgency_level(), 'normal')
        self.assertIsNotNone(indicator.canvas)
    
    def test_init_with_pattern(self):
        """패턴 포함 초기화 테스트"""
        indicator = UrgencyIndicator(self.root, urgency_level='urgent', show_pattern=True)
        
        self.assertEqual(indicator.get_urgency_level(), 'urgent')
        self.assertTrue(hasattr(indicator, 'pattern_label'))
    
    def test_set_urgency_level(self):
        """긴급도 레벨 설정 테스트"""
        indicator = UrgencyIndicator(self.root, urgency_level='normal')
        
        # 긴급도 변경
        indicator.set_urgency_level('overdue')
        self.assertEqual(indicator.get_urgency_level(), 'overdue')
        
        indicator.set_urgency_level('urgent')
        self.assertEqual(indicator.get_urgency_level(), 'urgent')
        
        indicator.set_urgency_level('warning')
        self.assertEqual(indicator.get_urgency_level(), 'warning')
    
    def test_canvas_creation(self):
        """캔버스 생성 테스트"""
        indicator = UrgencyIndicator(self.root)
        
        self.assertIsNotNone(indicator.canvas)
        # 캔버스가 생성되었는지만 확인 (크기는 실제 렌더링 후에 결정됨)
        self.assertIsInstance(indicator.canvas, tk.Canvas)


class TestDateTimeWidget(unittest.TestCase):
    """DateTimeWidget 컴포넌트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_init_with_datetime(self):
        """날짜/시간과 함께 초기화 테스트"""
        initial_dt = datetime(2025, 1, 15, 14, 30)
        widget = DateTimeWidget(self.root, initial_datetime=initial_dt)
        
        result_dt = widget.get_datetime()
        self.assertEqual(result_dt.year, 2025)
        self.assertEqual(result_dt.month, 1)
        self.assertEqual(result_dt.day, 15)
        self.assertEqual(result_dt.hour, 14)
        self.assertEqual(result_dt.minute, 30)
    
    def test_init_without_datetime(self):
        """날짜/시간 없이 초기화 테스트"""
        widget = DateTimeWidget(self.root)
        
        result_dt = widget.get_datetime()
        self.assertIsNotNone(result_dt)
        self.assertIsInstance(result_dt, datetime)
    
    def test_set_datetime(self):
        """날짜/시간 설정 테스트"""
        widget = DateTimeWidget(self.root)
        
        new_dt = datetime(2025, 12, 25, 18, 0)
        widget.set_datetime(new_dt)
        
        result_dt = widget.get_datetime()
        self.assertEqual(result_dt, new_dt)
        
        # UI 요소들도 업데이트되었는지 확인
        self.assertEqual(widget.date_var.get(), '2025-12-25')
        self.assertEqual(widget.hour_var.get(), '18')
        self.assertEqual(widget.minute_var.get(), '00')
    
    def test_set_none_datetime(self):
        """None 날짜/시간 설정 테스트"""
        widget = DateTimeWidget(self.root)
        
        widget.set_datetime(None)
        
        # None을 설정하면 현재 시간으로 설정되어야 함
        result_dt = widget.get_datetime()
        self.assertIsNotNone(result_dt)
        self.assertIsInstance(result_dt, datetime)
    
    def test_ui_elements_exist(self):
        """UI 요소들 존재 확인 테스트"""
        widget = DateTimeWidget(self.root)
        
        self.assertIsNotNone(widget.date_entry)
        self.assertIsNotNone(widget.hour_spin)
        self.assertIsNotNone(widget.minute_spin)
        self.assertIsNotNone(widget.date_var)
        self.assertIsNotNone(widget.hour_var)
        self.assertIsNotNone(widget.minute_var)


class TestQuickDateButtons(unittest.TestCase):
    """QuickDateButtons 컴포넌트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.selected_date = None
        self.callback_called = False
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def date_selected_callback(self, date):
        """날짜 선택 콜백"""
        self.selected_date = date
        self.callback_called = True
    
    def test_init_with_callback(self):
        """콜백과 함께 초기화 테스트"""
        buttons = QuickDateButtons(self.root, on_date_selected=self.date_selected_callback)
        
        self.assertIsNotNone(buttons.on_date_selected)
        
        # 버튼들이 생성되었는지 확인
        children = buttons.winfo_children()
        self.assertGreater(len(children), 0)
    
    def test_button_creation(self):
        """버튼 생성 테스트"""
        buttons = QuickDateButtons(self.root, on_date_selected=self.date_selected_callback)
        
        # 프레임들이 생성되었는지 확인 (3개 행)
        frames = [child for child in buttons.winfo_children() if isinstance(child, ttk.Frame)]
        self.assertEqual(len(frames), 3)
        
        # 각 프레임에 버튼들이 있는지 확인
        total_buttons = 0
        for frame in frames:
            frame_buttons = [child for child in frame.winfo_children() if isinstance(child, ttk.Button)]
            total_buttons += len(frame_buttons)
        
        self.assertGreater(total_buttons, 0)
    
    def test_update_options(self):
        """옵션 업데이트 테스트"""
        buttons = QuickDateButtons(self.root, on_date_selected=self.date_selected_callback)
        
        # 초기 자식 위젯 수
        initial_children_count = len(buttons.winfo_children())
        
        # 옵션 업데이트
        buttons.update_options()
        
        # 자식 위젯 수가 유지되는지 확인 (재생성됨)
        updated_children_count = len(buttons.winfo_children())
        self.assertEqual(initial_children_count, updated_children_count)


class TestComponentsIntegration(unittest.TestCase):
    """컴포넌트들 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_components_work_together(self):
        """컴포넌트들이 함께 작동하는지 테스트"""
        # 날짜/시간 위젯으로 날짜 선택
        datetime_widget = DateTimeWidget(self.root)
        test_date = datetime.now() + timedelta(hours=12)
        datetime_widget.set_datetime(test_date)
        
        # 선택된 날짜로 다른 컴포넌트들 업데이트
        selected_date = datetime_widget.get_datetime()
        
        # DueDateLabel 업데이트
        due_date_label = DueDateLabel(self.root)
        due_date_label.set_due_date(selected_date)
        
        # UrgencyIndicator 업데이트
        from services.date_service import DateService
        urgency = DateService.get_urgency_level(selected_date)
        urgency_indicator = UrgencyIndicator(self.root)
        urgency_indicator.set_urgency_level(urgency)
        
        # 모든 컴포넌트가 올바르게 설정되었는지 확인
        self.assertEqual(due_date_label.get_due_date(), selected_date)
        self.assertEqual(urgency_indicator.get_urgency_level(), urgency)
        self.assertNotEqual(due_date_label.cget('text'), '')
    
    def test_quick_date_to_datetime_widget(self):
        """빠른 날짜 선택에서 날짜/시간 위젯으로 연동 테스트"""
        datetime_widget = DateTimeWidget(self.root)
        
        def on_quick_date_selected(date):
            datetime_widget.set_datetime(date)
        
        quick_buttons = QuickDateButtons(self.root, on_date_selected=on_quick_date_selected)
        
        # 빠른 날짜 옵션 중 하나 선택 시뮬레이션
        from services.date_service import DateService
        quick_options = DateService.get_quick_date_options()
        
        if "오늘" in quick_options:
            test_date = quick_options["오늘"]
            on_quick_date_selected(test_date)
            
            # DateTimeWidget이 업데이트되었는지 확인
            selected_date = datetime_widget.get_datetime()
            self.assertEqual(selected_date.date(), test_date.date())
            self.assertEqual(selected_date.hour, test_date.hour)


def run_tests():
    """테스트 실행"""
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 각 테스트 클래스의 모든 테스트 메서드 추가
    test_classes = [
        TestDueDateLabel,
        TestUrgencyIndicator,
        TestDateTimeWidget,
        TestQuickDateButtons,
        TestComponentsIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)