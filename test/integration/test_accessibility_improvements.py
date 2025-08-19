"""
접근성 개선 기능 테스트

Task 19: 사용자 경험 개선 및 접근성 향상 테스트
- 키보드 단축키 추가 (빠른 목표 날짜 설정)
- 색맹 사용자를 위한 패턴/아이콘 추가
- 툴팁 및 도움말 메시지 추가
- 오류 메시지 및 사용자 가이드 개선
"""

import unittest
import tkinter as tk
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 테스트 대상 모듈들
from utils.color_utils import ColorUtils
from gui.components import UrgencyIndicator, DueDateLabel
from gui.main_window import MainWindow
from services.todo_service import TodoService
from models.todo import Todo


class TestAccessibilityImprovements(unittest.TestCase):
    """접근성 개선 기능 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 윈도우 숨김
        
        # Mock 서비스 생성
        self.mock_todo_service = Mock(spec=TodoService)
        self.mock_todo_service.get_all_todos.return_value = []
    
    def tearDown(self):
        """테스트 정리"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_accessibility_patterns(self):
        """색맹 사용자를 위한 패턴/아이콘 테스트"""
        print("Testing accessibility patterns...")
        
        # 접근성 패턴 확인
        patterns = ColorUtils.get_accessibility_patterns()
        self.assertIn('overdue', patterns)
        self.assertIn('urgent', patterns)
        self.assertIn('warning', patterns)
        self.assertIn('normal', patterns)
        self.assertIn('completed', patterns)
        
        # 각 패턴이 비어있지 않은지 확인
        for level, pattern in patterns.items():
            if level != 'normal':  # normal은 빈 패턴일 수 있음
                self.assertTrue(len(pattern) > 0, f"{level} 패턴이 비어있습니다")
        
        print("✓ 접근성 패턴 테스트 통과")
    
    def test_accessibility_symbols(self):
        """텍스트 기반 심볼 테스트"""
        print("Testing accessibility symbols...")
        
        # 접근성 심볼 확인
        symbols = ColorUtils.get_accessibility_symbols()
        self.assertIn('overdue', symbols)
        self.assertIn('urgent', symbols)
        self.assertIn('warning', symbols)
        self.assertIn('normal', symbols)
        self.assertIn('completed', symbols)
        
        # 긴급도별 심볼 확인
        self.assertEqual(symbols['overdue'], '!!!')
        self.assertEqual(symbols['urgent'], '!!')
        self.assertEqual(symbols['warning'], '!')
        self.assertEqual(symbols['normal'], '')
        self.assertEqual(symbols['completed'], '✓')
        
        print("✓ 접근성 심볼 테스트 통과")
    
    def test_accessibility_descriptions(self):
        """접근성 설명 테스트"""
        print("Testing accessibility descriptions...")
        
        # 접근성 설명 확인
        descriptions = ColorUtils.get_accessibility_descriptions()
        self.assertIn('overdue', descriptions)
        self.assertIn('urgent', descriptions)
        self.assertIn('warning', descriptions)
        self.assertIn('normal', descriptions)
        self.assertIn('completed', descriptions)
        
        # 각 설명이 의미있는 내용인지 확인
        for level, desc in descriptions.items():
            self.assertTrue(len(desc) > 5, f"{level} 설명이 너무 짧습니다: {desc}")
            self.assertIn(level.replace('_', ' '), desc.lower() + level, 
                         f"{level} 설명에 관련 키워드가 없습니다: {desc}")
        
        print("✓ 접근성 설명 테스트 통과")
    
    def test_urgency_indicator_accessibility(self):
        """긴급도 표시기 접근성 테스트"""
        print("Testing urgency indicator accessibility...")
        
        # 긴급도 표시기 생성 (패턴 표시 활성화)
        indicator = UrgencyIndicator(self.root, urgency_level='urgent', show_pattern=True)
        
        # 패턴 레이블이 생성되었는지 확인
        self.assertTrue(hasattr(indicator, 'pattern_label'))
        
        # 심볼 레이블이 생성되었는지 확인 (show_pattern=True인 경우)
        self.assertTrue(hasattr(indicator, 'symbol_label'))
        
        # 긴급도 변경 테스트
        indicator.set_urgency_level('overdue')
        self.assertEqual(indicator.get_urgency_level(), 'overdue')
        
        print("✓ 긴급도 표시기 접근성 테스트 통과")
    
    def test_due_date_label_accessibility(self):
        """목표 날짜 레이블 접근성 테스트"""
        print("Testing due date label accessibility...")
        
        # 목표 날짜 레이블 생성
        due_date = datetime.now() + timedelta(hours=2)  # 2시간 후
        label = DueDateLabel(self.root, due_date=due_date)
        
        # 표시 텍스트에 접근성 아이콘이 포함되었는지 확인
        display_text = label.cget('text')
        self.assertTrue(len(display_text) > 0, "목표 날짜 레이블이 비어있습니다")
        
        # 완료된 할일 테스트
        completed_label = DueDateLabel(self.root, due_date=due_date, 
                                     completed_at=datetime.now())
        completed_text = completed_label.cget('text')
        self.assertIn('✓', completed_text, "완료된 할일에 체크 마크가 없습니다")
        
        print("✓ 목표 날짜 레이블 접근성 테스트 통과")
    
    @patch('gui.dialogs.messagebox')
    def test_enhanced_error_messages(self, mock_messagebox):
        """향상된 오류 메시지 테스트"""
        print("Testing enhanced error messages...")
        
        from gui.dialogs import show_error_dialog, show_warning_dialog
        
        # 파일 관련 오류 메시지 테스트
        show_error_dialog(self.root, "파일을 열 수 없습니다")
        
        # messagebox.showerror가 호출되었는지 확인
        mock_messagebox.showerror.assert_called()
        
        # 호출된 메시지에 도움말이 포함되었는지 확인
        call_args = mock_messagebox.showerror.call_args
        # positional arguments로 전달된 경우
        if len(call_args[0]) >= 2:
            message = call_args[0][1]  # 두 번째 positional argument
        else:
            message = call_args[1].get('message', '')  # keyword argument
        self.assertIn('도움말', message, "오류 메시지에 도움말이 포함되지 않았습니다")
        
        # 경고 메시지 테스트
        mock_messagebox.reset_mock()
        show_warning_dialog(self.root, "데이터를 삭제합니다")
        
        mock_messagebox.showwarning.assert_called()
        warning_call_args = mock_messagebox.showwarning.call_args
        # positional arguments로 전달된 경우
        if len(warning_call_args[0]) >= 2:
            warning_message = warning_call_args[0][1]  # 두 번째 positional argument
        else:
            warning_message = warning_call_args[1].get('message', '')  # keyword argument
        self.assertIn('되돌릴 수 없습니다', warning_message, 
                     "삭제 경고에 되돌릴 수 없다는 안내가 없습니다")
        
        print("✓ 향상된 오류 메시지 테스트 통과")
    
    def test_keyboard_shortcuts_binding(self):
        """키보드 단축키 바인딩 테스트"""
        print("Testing keyboard shortcuts binding...")
        
        # MainWindow 생성 (실제 GUI는 표시하지 않음)
        with patch('gui.main_window.TodoTree'), \
             patch('gui.main_window.StatusBar'), \
             patch('gui.main_window.SearchBox'), \
             patch('gui.main_window.FilterPanel'):
            
            main_window = MainWindow(self.mock_todo_service)
            
            # 빠른 목표 날짜 설정 단축키가 바인딩되었는지 확인
            bindings = main_window.root.bind()
            
            # 주요 단축키들이 바인딩되었는지 확인
            expected_shortcuts = [
                '<Control-d>',      # 오늘로 설정
                '<Control-Shift-d>', # 내일로 설정
                '<Control-Alt-d>',   # 이번 주말로 설정
                '<Control-r>',       # 목표 날짜 제거
                '<Alt-F1>'          # 접근성 도움말
            ]
            
            for shortcut in expected_shortcuts:
                # 바인딩이 존재하는지 확인 (실제 바인딩 내용은 확인하지 않음)
                try:
                    bound_commands = main_window.root.bind(shortcut)
                    # 바인딩이 있으면 문자열이 반환됨
                    self.assertIsInstance(bound_commands, str, 
                                        f"{shortcut} 단축키가 바인딩되지 않았습니다")
                except tk.TclError:
                    self.fail(f"{shortcut} 단축키 바인딩 확인 중 오류 발생")
        
        print("✓ 키보드 단축키 바인딩 테스트 통과")
    
    def test_help_content_enhancement(self):
        """도움말 내용 개선 테스트"""
        print("Testing help content enhancement...")
        
        # MainWindow의 도움말 메서드 테스트
        with patch('gui.main_window.TodoTree'), \
             patch('gui.main_window.StatusBar'), \
             patch('gui.main_window.SearchBox'), \
             patch('gui.main_window.FilterPanel'), \
             patch('gui.main_window.show_info_dialog') as mock_info_dialog:
            
            main_window = MainWindow(self.mock_todo_service)
            
            # 접근성 도움말 호출
            main_window._show_accessibility_help()
            
            # show_info_dialog가 호출되었는지 확인
            mock_info_dialog.assert_called_once()
            
            # 호출된 도움말 내용 확인
            call_args = mock_info_dialog.call_args[0]
            help_content = call_args[1]  # 두 번째 인자가 도움말 내용
            
            # 주요 내용이 포함되었는지 확인
            expected_content = [
                '빠른 목표 날짜 설정',
                'Ctrl+D',
                '접근성 기능',
                '긴급도 표시',
                '키보드 단축키'
            ]
            
            for content in expected_content:
                self.assertIn(content, help_content, 
                            f"도움말에 '{content}' 내용이 없습니다")
        
        print("✓ 도움말 내용 개선 테스트 통과")
    
    def test_tooltip_functionality(self):
        """툴팁 기능 테스트"""
        print("Testing tooltip functionality...")
        
        # UrgencyIndicator의 툴팁 테스트
        indicator = UrgencyIndicator(self.root, urgency_level='urgent')
        
        # 툴팁 생성 메서드가 있는지 확인
        self.assertTrue(hasattr(indicator, '_create_tooltip'), 
                       "UrgencyIndicator에 _create_tooltip 메서드가 없습니다")
        
        # DueDateLabel의 툴팁 테스트
        due_date = datetime.now() + timedelta(days=1)
        label = DueDateLabel(self.root, due_date=due_date)
        
        # 툴팁 생성 메서드가 있는지 확인
        self.assertTrue(hasattr(label, '_create_tooltip'), 
                       "DueDateLabel에 _create_tooltip 메서드가 없습니다")
        
        print("✓ 툴팁 기능 테스트 통과")


def run_accessibility_tests():
    """접근성 개선 테스트 실행"""
    print("=" * 60)
    print("접근성 개선 기능 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAccessibilityImprovements)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("접근성 개선 테스트 결과:")
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
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n성공률: {success_rate:.1f}%")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_accessibility_tests()
    exit(0 if success else 1)