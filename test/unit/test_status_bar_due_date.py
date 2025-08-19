"""
상태바 목표 날짜 정보 표시 기능 테스트

Task 13: 상태바에 목표 날짜 관련 정보 표시
- 오늘 마감 할일 개수 표시 기능 구현
- 지연된 할일 개수 표시 기능 구현
- 상태바 레이아웃 조정 및 정보 업데이트 로직 구현
- 실시간 정보 업데이트 구현
"""

import unittest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from gui.components import StatusBar
from gui.main_window import MainWindow
from services.todo_service import TodoService
from services.notification_service import NotificationService
from models.todo import Todo


class TestStatusBarDueDateInfo(unittest.TestCase):
    """상태바 목표 날짜 정보 표시 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 윈도우 숨기기
        
        # Mock 서비스 생성
        self.mock_todo_service = Mock(spec=TodoService)
        self.mock_notification_service = Mock(spec=NotificationService)
        
        # StatusBar 컴포넌트 생성
        self.status_bar = StatusBar(self.root)
    
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    def test_status_bar_has_due_date_labels(self):
        """상태바에 목표 날짜 관련 레이블이 있는지 확인"""
        # 오늘 마감 레이블 확인
        self.assertTrue(hasattr(self.status_bar, 'due_today_label'))
        self.assertIsNotNone(self.status_bar.due_today_label)
        
        # 지연된 할일 레이블 확인
        self.assertTrue(hasattr(self.status_bar, 'overdue_label'))
        self.assertIsNotNone(self.status_bar.overdue_label)
    
    def test_update_due_date_info_zero_counts(self):
        """목표 날짜 정보 업데이트 - 0개인 경우"""
        # 0개로 업데이트
        self.status_bar.update_due_date_info(0, 0)
        
        # 레이블 텍스트 확인
        self.assertEqual(self.status_bar.due_today_label.cget('text'), "오늘 마감: 0개")
        self.assertEqual(self.status_bar.overdue_label.cget('text'), "지연: 0개")
        
        # 색상 확인 (0개일 때는 회색)
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "gray")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "gray")
    
    def test_update_due_date_info_with_counts(self):
        """목표 날짜 정보 업데이트 - 개수가 있는 경우"""
        # 개수가 있는 경우로 업데이트
        self.status_bar.update_due_date_info(3, 2)
        
        # 레이블 텍스트 확인
        self.assertEqual(self.status_bar.due_today_label.cget('text'), "오늘 마감: 3개")
        self.assertEqual(self.status_bar.overdue_label.cget('text'), "지연: 2개")
        
        # 색상 확인 (개수가 있을 때는 해당 색상)
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "orange")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "red")
    
    def test_get_due_date_info(self):
        """목표 날짜 정보 반환 테스트"""
        # 정보 업데이트
        self.status_bar.update_due_date_info(5, 3)
        
        # 정보 반환 확인
        info = self.status_bar.get_due_date_info()
        self.assertEqual(info['due_today'], 5)
        self.assertEqual(info['overdue'], 3)
    
    @patch('services.notification_service.NotificationService')
    def test_main_window_status_bar_integration(self, mock_notification_class):
        """메인 윈도우와 상태바 통합 테스트"""
        # Mock 설정
        mock_notification_instance = Mock()
        mock_notification_class.return_value = mock_notification_instance
        
        # 상태바 요약 정보 Mock
        mock_notification_instance.get_status_bar_summary.return_value = {
            'due_today': 2,
            'overdue': 1,
            'urgent': 3,
            'total': 10,
            'completed': 5
        }
        
        # 할일 목록 Mock
        mock_todos = [Mock(spec=Todo) for _ in range(10)]
        for i, todo in enumerate(mock_todos):
            todo.is_completed.return_value = i < 5  # 처음 5개는 완료
            todo.get_completion_rate.return_value = 1.0 if i < 5 else 0.5
        
        self.mock_todo_service.get_all_todos.return_value = mock_todos
        
        # MainWindow 생성 (실제 UI는 생성하지 않음)
        with patch('gui.main_window.MainWindow.setup_window'), \
             patch('gui.main_window.MainWindow.load_window_settings'), \
             patch('gui.main_window.MainWindow.setup_ui'):
            
            main_window = MainWindow(self.mock_todo_service)
            main_window.notification_service = mock_notification_instance
            main_window.status_bar = self.status_bar
            main_window.overall_progress_bar = Mock()
            
            # 상태바 업데이트 실행
            main_window.update_status_bar()
            
            # 목표 날짜 정보가 업데이트되었는지 확인
            self.assertEqual(self.status_bar.due_today_label.cget('text'), "오늘 마감: 2개")
            self.assertEqual(self.status_bar.overdue_label.cget('text'), "지연: 1개")
    
    def test_status_bar_color_coding(self):
        """상태바 색상 코딩 테스트"""
        # 0개일 때 회색
        self.status_bar.update_due_date_info(0, 0)
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "gray")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "gray")
        
        # 오늘 마감만 있을 때
        self.status_bar.update_due_date_info(3, 0)
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "orange")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "gray")
        
        # 지연된 할일만 있을 때
        self.status_bar.update_due_date_info(0, 2)
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "gray")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "red")
        
        # 둘 다 있을 때
        self.status_bar.update_due_date_info(1, 1)
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "orange")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "red")


class TestMainWindowStatusBarUpdates(unittest.TestCase):
    """메인 윈도우 상태바 업데이트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_todo_service = Mock(spec=TodoService)
        self.mock_notification_service = Mock(spec=NotificationService)
    
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    @patch('gui.main_window.MainWindow.setup_window')
    @patch('gui.main_window.MainWindow.load_window_settings')
    @patch('gui.main_window.MainWindow.setup_ui')
    def test_notification_service_initialization(self, mock_setup_ui, mock_load_settings, mock_setup_window):
        """NotificationService 초기화 테스트"""
        main_window = MainWindow(self.mock_todo_service)
        
        # NotificationService가 초기화되었는지 확인
        self.assertIsNotNone(main_window.notification_service)
        self.assertIsInstance(main_window.notification_service, NotificationService)
    
    @patch('gui.main_window.MainWindow.setup_window')
    @patch('gui.main_window.MainWindow.load_window_settings')
    @patch('gui.main_window.MainWindow.setup_ui')
    def test_periodic_update_method_exists(self, mock_setup_ui, mock_load_settings, mock_setup_window):
        """주기적 업데이트 메서드 존재 확인"""
        main_window = MainWindow(self.mock_todo_service)
        
        # 주기적 업데이트 관련 메서드들이 존재하는지 확인
        self.assertTrue(hasattr(main_window, 'start_status_bar_updates'))
        self.assertTrue(hasattr(main_window, '_update_status_bar_periodically'))
        self.assertTrue(callable(main_window.start_status_bar_updates))
        self.assertTrue(callable(main_window._update_status_bar_periodically))


class TestStatusBarLayoutAndUI(unittest.TestCase):
    """상태바 레이아웃 및 UI 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.status_bar = StatusBar(self.root)
    
    def tearDown(self):
        """테스트 정리"""
        if self.root:
            self.root.destroy()
    
    def test_status_bar_layout_structure(self):
        """상태바 레이아웃 구조 테스트"""
        # 기본 프레임들이 존재하는지 확인
        self.assertTrue(hasattr(self.status_bar, 'status_frame'))
        self.assertTrue(hasattr(self.status_bar, 'left_frame'))
        self.assertTrue(hasattr(self.status_bar, 'right_frame'))
        
        # 목표 날짜 관련 레이블들이 존재하는지 확인
        self.assertTrue(hasattr(self.status_bar, 'due_today_label'))
        self.assertTrue(hasattr(self.status_bar, 'overdue_label'))
        
        # 기존 레이블들도 여전히 존재하는지 확인
        self.assertTrue(hasattr(self.status_bar, 'todo_count_label'))
        self.assertTrue(hasattr(self.status_bar, 'completion_label'))
        self.assertTrue(hasattr(self.status_bar, 'status_message_label'))
        self.assertTrue(hasattr(self.status_bar, 'last_saved_label'))
    
    def test_status_bar_initial_values(self):
        """상태바 초기값 테스트"""
        # 목표 날짜 레이블 초기값 확인
        self.assertEqual(self.status_bar.due_today_label.cget('text'), "오늘 마감: 0개")
        self.assertEqual(self.status_bar.overdue_label.cget('text'), "지연: 0개")
        
        # 초기 색상 확인
        self.assertEqual(str(self.status_bar.due_today_label.cget('foreground')), "gray")
        self.assertEqual(str(self.status_bar.overdue_label.cget('foreground')), "gray")
    
    def test_status_bar_widget_packing(self):
        """상태바 위젯 패킹 테스트"""
        # 모든 위젯이 올바르게 패킹되어 있는지 확인
        widgets = self.status_bar.left_frame.winfo_children()
        self.assertGreater(len(widgets), 0)
        
        # 목표 날짜 레이블들이 패킹되어 있는지 확인
        packed_widgets = [w for w in widgets if w.winfo_manager() == 'pack']
        self.assertIn(self.status_bar.due_today_label, packed_widgets)
        self.assertIn(self.status_bar.overdue_label, packed_widgets)


if __name__ == '__main__':
    unittest.main()