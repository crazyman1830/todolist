#!/usr/bin/env python3
"""
시작 시 알림 다이얼로그 통합 테스트

Task 14 구현 검증을 위한 테스트
"""

import sys
import os
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.todo_service import TodoService
from services.notification_service import NotificationService
from gui.main_window import MainWindow


class TestStartupNotificationIntegration(unittest.TestCase):
    """시작 시 알림 다이얼로그 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Mock 서비스들 생성
        self.mock_todo_service = Mock(spec=TodoService)
        self.mock_notification_service = Mock(spec=NotificationService)
        
        # 임시 설정 파일 생성
        self.temp_settings_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_settings_file.close()
        
    def tearDown(self):
        """테스트 정리"""
        # 임시 파일 삭제
        try:
            os.unlink(self.temp_settings_file.name)
        except:
            pass
    
    @patch('gui.main_window.tk.Tk')
    @patch('gui.main_window.NotificationService')
    def test_startup_notification_enabled_with_overdue_todos(self, mock_notification_class, mock_tk):
        """지연된 할일이 있고 알림이 활성화된 경우 테스트"""
        # Mock 설정
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        mock_notification_service = Mock()
        mock_notification_class.return_value = mock_notification_service
        
        # 지연된 할일이 있는 상황 설정
        mock_notification_service.should_show_startup_notification.return_value = True
        mock_notification_service.get_status_bar_summary.return_value = {
            'overdue': 2,
            'due_today': 1,
            'urgent': 0,
            'total': 10,
            'completed': 5
        }
        
        # MainWindow 생성 (실제 UI는 생성하지 않음)
        with patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'), \
             patch('gui.main_window.show_startup_notification_dialog') as mock_dialog:
            
            main_window = MainWindow(self.mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            
            # 시작 알림 설정이 활성화된 상태로 설정
            main_window.saved_settings = {'show_startup_notifications': True}
            
            # 시작 알림 체크 실행
            main_window.check_and_show_startup_notification()
            
            # after 메서드가 호출되었는지 확인
            mock_root.after.assert_called()
            
            # after로 등록된 콜백 함수 실행
            callback = mock_root.after.call_args[0][1]
            callback()
            
            # 알림 다이얼로그가 호출되었는지 확인
            mock_dialog.assert_called_once_with(mock_root, 2, 1)
    
    @patch('gui.main_window.tk.Tk')
    @patch('gui.main_window.NotificationService')
    def test_startup_notification_disabled_by_setting(self, mock_notification_class, mock_tk):
        """알림이 비활성화된 경우 테스트"""
        # Mock 설정
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        mock_notification_service = Mock()
        mock_notification_class.return_value = mock_notification_service
        
        # MainWindow 생성
        with patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'), \
             patch('gui.main_window.show_startup_notification_dialog') as mock_dialog:
            
            main_window = MainWindow(self.mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            
            # 시작 알림 설정이 비활성화된 상태로 설정
            main_window.saved_settings = {'show_startup_notifications': False}
            
            # 시작 알림 체크 실행
            main_window.check_and_show_startup_notification()
            
            # after 메서드가 호출되지 않았는지 확인
            mock_root.after.assert_not_called()
            
            # 알림 다이얼로그가 호출되지 않았는지 확인
            mock_dialog.assert_not_called()
    
    @patch('gui.main_window.tk.Tk')
    @patch('gui.main_window.NotificationService')
    def test_startup_notification_no_urgent_todos(self, mock_notification_class, mock_tk):
        """긴급한 할일이 없는 경우 테스트"""
        # Mock 설정
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        mock_notification_service = Mock()
        mock_notification_class.return_value = mock_notification_service
        
        # 긴급한 할일이 없는 상황 설정
        mock_notification_service.should_show_startup_notification.return_value = False
        
        # MainWindow 생성
        with patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'), \
             patch('gui.main_window.show_startup_notification_dialog') as mock_dialog:
            
            main_window = MainWindow(self.mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            
            # 시작 알림 설정이 활성화된 상태로 설정
            main_window.saved_settings = {'show_startup_notifications': True}
            
            # 시작 알림 체크 실행
            main_window.check_and_show_startup_notification()
            
            # after 메서드가 호출되지 않았는지 확인
            mock_root.after.assert_not_called()
            
            # 알림 다이얼로그가 호출되지 않았는지 확인
            mock_dialog.assert_not_called()
    
    @patch('gui.main_window.tk.Tk')
    @patch('gui.main_window.NotificationService')
    def test_dont_show_again_option(self, mock_notification_class, mock_tk):
        """다시 보지 않기 옵션 테스트"""
        # Mock 설정
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        mock_notification_service = Mock()
        mock_notification_class.return_value = mock_notification_service
        
        # MainWindow 생성
        with patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'), \
             patch('gui.main_window.show_startup_notification_dialog') as mock_dialog:
            
            main_window = MainWindow(self.mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            main_window.saved_settings = {}
            
            # Mock 상태바
            main_window.status_bar = Mock()
            
            # 다이얼로그에서 "다시 보지 않기" 선택한 결과 설정
            mock_dialog.return_value = {
                'confirmed': True,
                'dont_show_again': True
            }
            
            # 다이얼로그 표시 함수 직접 호출
            main_window._show_startup_notification_dialog(1, 1)
            
            # 설정이 저장되었는지 확인
            self.assertFalse(main_window.get_startup_notification_setting())
            
            # 상태바 메시지가 업데이트되었는지 확인
            main_window.status_bar.update_status.assert_called_with("시작 알림이 비활성화되었습니다.")
    
    def test_startup_notification_setting_management(self):
        """시작 알림 설정 관리 테스트"""
        with patch('gui.main_window.tk.Tk'), \
             patch('gui.main_window.NotificationService'), \
             patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'):
            
            main_window = MainWindow(self.mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            
            # 기본값 테스트 (True)
            self.assertTrue(main_window.get_startup_notification_setting())
            
            # 설정 변경 테스트
            main_window.set_startup_notification_setting(False)
            self.assertFalse(main_window.get_startup_notification_setting())
            
            # 설정 다시 변경 테스트
            main_window.set_startup_notification_setting(True)
            self.assertTrue(main_window.get_startup_notification_setting())


def run_integration_test():
    """통합 테스트 실행"""
    print("="*60)
    print("시작 시 알림 다이얼로그 통합 테스트 실행")
    print("="*60)
    
    # 테스트 실행
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_integration_test()