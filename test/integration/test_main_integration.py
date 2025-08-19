#!/usr/bin/env python3
"""
메인 프로그램 통합 테스트

실제 프로그램 실행 흐름을 테스트합니다.
"""

import unittest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMainIntegration(unittest.TestCase):
    """메인 프로그램 통합 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.test_dir, "test_todos.json")
        self.test_folders_dir = os.path.join(self.test_dir, "test_folders")
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('main.TODOS_FILE')
    @patch('main.TODO_FOLDERS_DIR')
    @patch('builtins.input', side_effect=['0'])  # 프로그램 종료 선택
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_program_execution(self, mock_stdout, mock_input, mock_folders_dir, mock_todos_file):
        """메인 프로그램 실행 테스트"""
        # Mock 설정
        mock_todos_file.return_value = self.test_data_file
        mock_folders_dir.return_value = self.test_folders_dir
        
        # 실제 파일 경로로 패치
        with patch('main.TODOS_FILE', self.test_data_file), \
             patch('main.TODO_FOLDERS_DIR', self.test_folders_dir):
            
            # SystemExit 예외를 잡아서 정상 종료 확인
            with self.assertRaises(SystemExit) as context:
                from main import main
                main()
            
            # 정상 종료 코드 확인 (0)
            self.assertEqual(context.exception.code, 0)
            
            # 출력 확인
            output = mock_stdout.getvalue()
            self.assertIn("할일 관리 프로그램에 오신 것을 환영합니다", output)
            self.assertIn("초기화가 완료되었습니다", output)
            self.assertIn("할일 관리 프로그램", output)
            self.assertIn("프로그램을 종료합니다", output)
    
    @patch('main.initialize_services')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_initialization_error(self, mock_stdout, mock_init_services):
        """초기화 오류 처리 테스트"""
        # 초기화 실패 시뮬레이션
        mock_init_services.side_effect = RuntimeError("Test initialization error")
        
        # SystemExit 예외를 잡아서 오류 종료 확인
        with self.assertRaises(SystemExit) as context:
            from main import main
            main()
        
        # 오류 종료 코드 확인 (1)
        self.assertEqual(context.exception.code, 1)
        
        # 오류 메시지 확인
        output = mock_stdout.getvalue()
        self.assertIn("초기화 오류", output)
        self.assertIn("Test initialization error", output)
    
    def test_signal_handler_import(self):
        """시그널 핸들러 함수 존재 확인"""
        from main import signal_handler
        self.assertTrue(callable(signal_handler))


if __name__ == '__main__':
    unittest.main()