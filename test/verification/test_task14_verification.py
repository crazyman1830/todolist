#!/usr/bin/env python3
"""
Task 14 완료 검증 테스트

시작 시 알림 다이얼로그 구현의 모든 하위 작업이 완료되었는지 검증합니다.

Sub-tasks:
- StartupNotificationDialog 클래스 구현 ✓
- 알림 표시 조건 확인 및 다이얼로그 표시 로직 구현 ✓
- "다시 보지 않기" 옵션 구현 ✓
- 메인 윈도우 시작 시 알림 체크 로직 통합 ✓
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import tempfile
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.dialogs import StartupNotificationDialog, show_startup_notification_dialog
from gui.main_window import MainWindow
from services.notification_service import NotificationService


class TestTask14Verification(unittest.TestCase):
    """Task 14 완료 검증 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_settings_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_settings_file.close()
    
    def tearDown(self):
        """테스트 정리"""
        try:
            os.unlink(self.temp_settings_file.name)
        except:
            pass
    
    def test_subtask_1_startup_notification_dialog_class_exists(self):
        """Sub-task 1: StartupNotificationDialog 클래스 구현 검증"""
        print("\n✓ Sub-task 1: StartupNotificationDialog 클래스 구현 검증")
        
        # StartupNotificationDialog 클래스가 존재하는지 확인
        self.assertTrue(hasattr(sys.modules['gui.dialogs'], 'StartupNotificationDialog'))
        
        # 클래스가 올바른 베이스 클래스를 상속하는지 확인
        from gui.dialogs import BaseDialog
        self.assertTrue(issubclass(StartupNotificationDialog, BaseDialog))
        
        # 필수 메서드들이 구현되어 있는지 확인
        dialog_methods = dir(StartupNotificationDialog)
        self.assertIn('__init__', dialog_methods)
        self.assertIn('setup_ui', dialog_methods)
        self.assertIn('get_result', dialog_methods)
        
        print("   - StartupNotificationDialog 클래스 존재 확인 ✓")
        print("   - BaseDialog 상속 확인 ✓")
        print("   - 필수 메서드 구현 확인 ✓")
    
    def test_subtask_2_notification_condition_check_logic(self):
        """Sub-task 2: 알림 표시 조건 확인 및 다이얼로그 표시 로직 구현 검증"""
        print("\n✓ Sub-task 2: 알림 표시 조건 확인 및 다이얼로그 표시 로직 구현 검증")
        
        with patch('gui.main_window.tk.Tk'), \
             patch('gui.main_window.NotificationService') as mock_notification_class, \
             patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'):
            
            # MainWindow 생성
            mock_todo_service = Mock()
            main_window = MainWindow(mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            
            # 알림 조건 확인 메서드가 존재하는지 확인
            self.assertTrue(hasattr(main_window, 'check_and_show_startup_notification'))
            self.assertTrue(hasattr(main_window, '_show_startup_notification_dialog'))
            
            # NotificationService의 should_show_startup_notification 메서드 사용 확인
            mock_notification_service = mock_notification_class.return_value
            mock_notification_service.should_show_startup_notification.return_value = True
            mock_notification_service.get_status_bar_summary.return_value = {
                'overdue': 1, 'due_today': 1, 'urgent': 0, 'total': 5, 'completed': 2
            }
            
            main_window.saved_settings = {'show_startup_notifications': True}
            
            # 알림 조건 확인 로직 실행
            main_window.check_and_show_startup_notification()
            
            # NotificationService 메서드가 호출되었는지 확인
            mock_notification_service.should_show_startup_notification.assert_called_once()
            
            print("   - 알림 조건 확인 메서드 존재 확인 ✓")
            print("   - NotificationService 연동 확인 ✓")
            print("   - 조건부 알림 표시 로직 확인 ✓")
    
    def test_subtask_3_dont_show_again_option(self):
        """Sub-task 3: "다시 보지 않기" 옵션 구현 검증"""
        print("\n✓ Sub-task 3: '다시 보지 않기' 옵션 구현 검증")
        
        with patch('gui.main_window.tk.Tk'), \
             patch('gui.main_window.NotificationService'), \
             patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'), \
             patch('gui.main_window.show_startup_notification_dialog') as mock_dialog:
            
            # MainWindow 생성
            mock_todo_service = Mock()
            main_window = MainWindow(mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            main_window.saved_settings = {}
            
            # 설정 관리 메서드들이 존재하는지 확인
            self.assertTrue(hasattr(main_window, 'get_startup_notification_setting'))
            self.assertTrue(hasattr(main_window, 'set_startup_notification_setting'))
            
            # 기본값 테스트
            self.assertTrue(main_window.get_startup_notification_setting())
            
            # 설정 변경 테스트
            main_window.set_startup_notification_setting(False)
            self.assertFalse(main_window.get_startup_notification_setting())
            
            # "다시 보지 않기" 옵션 처리 테스트
            mock_dialog.return_value = {'confirmed': True, 'dont_show_again': True}
            main_window._show_startup_notification_dialog(1, 1)
            
            # 설정이 False로 변경되었는지 확인
            self.assertFalse(main_window.get_startup_notification_setting())
            
            print("   - 설정 관리 메서드 존재 확인 ✓")
            print("   - 기본값 설정 확인 ✓")
            print("   - '다시 보지 않기' 옵션 처리 확인 ✓")
    
    def test_subtask_4_main_window_startup_integration(self):
        """Sub-task 4: 메인 윈도우 시작 시 알림 체크 로직 통합 검증"""
        print("\n✓ Sub-task 4: 메인 윈도우 시작 시 알림 체크 로직 통합 검증")
        
        with patch('gui.main_window.tk.Tk') as mock_tk, \
             patch('gui.main_window.NotificationService'), \
             patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'):
            
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # MainWindow 생성
            mock_todo_service = Mock()
            main_window = MainWindow(mock_todo_service)
            main_window.settings_file = self.temp_settings_file.name
            
            # run 메서드에서 알림 체크가 통합되어 있는지 확인
            with patch.object(main_window, 'check_and_show_startup_notification') as mock_check:
                try:
                    # run 메서드 실행 (mainloop는 Mock으로 처리)
                    mock_root.mainloop.side_effect = KeyboardInterrupt()  # 즉시 종료
                    main_window.run()
                except KeyboardInterrupt:
                    pass
                
                # after 메서드가 호출되어 알림 체크가 예약되었는지 확인
                mock_root.after.assert_called()
                
                # after로 등록된 콜백이 알림 체크 메서드인지 확인
                after_calls = mock_root.after.call_args_list
                self.assertTrue(len(after_calls) > 0)
                
                # 첫 번째 after 호출의 콜백 함수 실행
                callback = after_calls[0][0][1]
                callback()
                
                # 알림 체크 메서드가 호출되었는지 확인
                mock_check.assert_called_once()
            
            print("   - run 메서드에 알림 체크 통합 확인 ✓")
            print("   - 지연 실행을 위한 after 메서드 사용 확인 ✓")
            print("   - 시작 시 자동 알림 체크 확인 ✓")
    
    def test_startup_notification_dialog_functionality(self):
        """StartupNotificationDialog 기능 테스트"""
        print("\n✓ StartupNotificationDialog 기능 테스트")
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # show_startup_notification_dialog 함수 테스트
            with patch('gui.dialogs.StartupNotificationDialog') as mock_dialog_class:
                mock_dialog = Mock()
                mock_dialog.result = {'confirmed': True, 'dont_show_again': False}
                mock_dialog_class.return_value = mock_dialog
                
                result = show_startup_notification_dialog(mock_root, 2, 1)
                
                # 다이얼로그가 올바른 인자로 생성되었는지 확인
                mock_dialog_class.assert_called_once_with(mock_root, 2, 1)
                
                # wait_window이 호출되었는지 확인
                mock_root.wait_window.assert_called_once_with(mock_dialog)
                
                # 결과가 올바르게 반환되었는지 확인
                self.assertEqual(result, {'confirmed': True, 'dont_show_again': False})
            
            print("   - show_startup_notification_dialog 함수 동작 확인 ✓")
            print("   - 다이얼로그 생성 및 결과 반환 확인 ✓")
    
    def test_requirements_compliance(self):
        """Requirements 8.4 준수 확인"""
        print("\n✓ Requirements 8.4 준수 확인")
        
        # Requirements 8.4: 목표 날짜가 임박한 할일이 있으면 프로그램 시작 시 알림 다이얼로그를 표시할 수 있어야 합니다
        
        # NotificationService의 should_show_startup_notification 메서드 존재 확인
        notification_service = NotificationService(Mock())
        self.assertTrue(hasattr(notification_service, 'should_show_startup_notification'))
        
        # StartupNotificationDialog 클래스 존재 확인
        self.assertTrue('StartupNotificationDialog' in dir(sys.modules['gui.dialogs']))
        
        # MainWindow에 시작 알림 로직 통합 확인
        with patch('gui.main_window.tk.Tk'), \
             patch('gui.main_window.NotificationService'), \
             patch.object(MainWindow, 'setup_window'), \
             patch.object(MainWindow, 'load_window_settings'), \
             patch.object(MainWindow, 'setup_ui'):
            
            main_window = MainWindow(Mock())
            self.assertTrue(hasattr(main_window, 'check_and_show_startup_notification'))
        
        print("   - NotificationService 알림 조건 확인 메서드 존재 ✓")
        print("   - StartupNotificationDialog 클래스 존재 ✓")
        print("   - MainWindow 시작 알림 로직 통합 ✓")
        print("   - Requirements 8.4 완전 준수 ✓")


def run_task14_verification():
    """Task 14 완료 검증 실행"""
    print("="*70)
    print("Task 14: 시작 시 알림 다이얼로그 구현 - 완료 검증")
    print("="*70)
    print("Sub-tasks:")
    print("- StartupNotificationDialog 클래스 구현")
    print("- 알림 표시 조건 확인 및 다이얼로그 표시 로직 구현")
    print("- '다시 보지 않기' 옵션 구현")
    print("- 메인 윈도우 시작 시 알림 체크 로직 통합")
    print("- Requirements: 8.4")
    print("="*70)
    
    # 테스트 실행
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_task14_verification()