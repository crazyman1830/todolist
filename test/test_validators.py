"""
입력 유효성 검사 유틸리티 단위 테스트

TodoValidator 클래스의 모든 메서드에 대한 단위 테스트를 포함합니다.
"""

import unittest
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.validators import TodoValidator


class TestTodoValidator(unittest.TestCase):
    """TodoValidator 클래스 테스트"""
    
    def test_validate_title_valid_cases(self):
        """유효한 제목 테스트"""
        # 일반적인 제목
        self.assertTrue(TodoValidator.validate_title("프로젝트 문서 작성"))
        self.assertTrue(TodoValidator.validate_title("회의 준비"))
        self.assertTrue(TodoValidator.validate_title("a"))  # 최소 길이
        
        # 공백이 포함된 제목
        self.assertTrue(TodoValidator.validate_title("  할일 제목  "))
        
        # 특수문자가 포함된 제목
        self.assertTrue(TodoValidator.validate_title("할일 #1 - 중요!"))
        
        # 100자 제목
        long_title = "a" * 100
        self.assertTrue(TodoValidator.validate_title(long_title))
    
    def test_validate_title_invalid_cases(self):
        """무효한 제목 테스트"""
        # 빈 문자열
        self.assertFalse(TodoValidator.validate_title(""))
        
        # None
        self.assertFalse(TodoValidator.validate_title(None))
        
        # 공백만 있는 경우
        self.assertFalse(TodoValidator.validate_title("   "))
        self.assertFalse(TodoValidator.validate_title("\t\n"))
        
        # 문자열이 아닌 타입
        self.assertFalse(TodoValidator.validate_title(123))
        self.assertFalse(TodoValidator.validate_title([]))
        self.assertFalse(TodoValidator.validate_title({}))
        
        # 너무 긴 제목 (101자)
        long_title = "a" * 101
        self.assertFalse(TodoValidator.validate_title(long_title))
    
    def test_validate_todo_id_valid_cases(self):
        """유효한 ID 테스트"""
        # 정상적인 ID
        self.assertEqual(TodoValidator.validate_todo_id("1", 5), 1)
        self.assertEqual(TodoValidator.validate_todo_id("3", 5), 3)
        self.assertEqual(TodoValidator.validate_todo_id("5", 5), 5)
        
        # 공백이 있는 경우
        self.assertEqual(TodoValidator.validate_todo_id("  2  ", 5), 2)
        
        # 최대값과 같은 경우
        self.assertEqual(TodoValidator.validate_todo_id("10", 10), 10)
    
    def test_validate_todo_id_invalid_cases(self):
        """무효한 ID 테스트"""
        # 빈 문자열
        self.assertIsNone(TodoValidator.validate_todo_id("", 5))
        
        # None
        self.assertIsNone(TodoValidator.validate_todo_id(None, 5))
        
        # 숫자가 아닌 문자열
        self.assertIsNone(TodoValidator.validate_todo_id("abc", 5))
        self.assertIsNone(TodoValidator.validate_todo_id("1a", 5))
        self.assertIsNone(TodoValidator.validate_todo_id("a1", 5))
        
        # 0 또는 음수
        self.assertIsNone(TodoValidator.validate_todo_id("0", 5))
        self.assertIsNone(TodoValidator.validate_todo_id("-1", 5))
        
        # 최대값을 초과하는 경우
        self.assertIsNone(TodoValidator.validate_todo_id("6", 5))
        self.assertIsNone(TodoValidator.validate_todo_id("100", 5))
        
        # 문자열이 아닌 타입
        self.assertIsNone(TodoValidator.validate_todo_id(123, 5))
        self.assertIsNone(TodoValidator.validate_todo_id([], 5))
    
    def test_sanitize_folder_name_basic_cases(self):
        """기본적인 폴더명 정제 테스트"""
        # 일반적인 제목
        self.assertEqual(TodoValidator.sanitize_folder_name("프로젝트 문서 작성"), "프로젝트_문서_작성")
        self.assertEqual(TodoValidator.sanitize_folder_name("회의 준비"), "회의_준비")
        
        # 공백 처리
        self.assertEqual(TodoValidator.sanitize_folder_name("  할일  제목  "), "할일_제목")
        self.assertEqual(TodoValidator.sanitize_folder_name("여러    공백    테스트"), "여러_공백_테스트")
    
    def test_sanitize_folder_name_invalid_characters(self):
        """무효한 문자 정제 테스트"""
        # Windows에서 사용할 수 없는 문자들
        self.assertEqual(TodoValidator.sanitize_folder_name("파일<이름>"), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name('파일"이름"'), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name("파일|이름"), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name("파일?이름"), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name("파일*이름"), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name("파일\\이름"), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name("파일/이름"), "파일_이름")
        self.assertEqual(TodoValidator.sanitize_folder_name("파일:이름"), "파일_이름")
        
        # 복합 문자 테스트
        self.assertEqual(TodoValidator.sanitize_folder_name("파일<>:\"|?*\\/이름"), "파일_이름")
    
    def test_sanitize_folder_name_edge_cases(self):
        """경계 케이스 테스트"""
        # 빈 문자열
        self.assertEqual(TodoValidator.sanitize_folder_name(""), "untitled")
        
        # None
        self.assertEqual(TodoValidator.sanitize_folder_name(None), "untitled")
        
        # 공백만 있는 경우
        self.assertEqual(TodoValidator.sanitize_folder_name("   "), "untitled")
        
        # 무효한 문자만 있는 경우
        self.assertEqual(TodoValidator.sanitize_folder_name("<>:\"|?*\\/"), "untitled")
        
        # 문자열이 아닌 타입
        self.assertEqual(TodoValidator.sanitize_folder_name(123), "untitled")
        self.assertEqual(TodoValidator.sanitize_folder_name([]), "untitled")
    
    def test_sanitize_folder_name_length_limit(self):
        """길이 제한 테스트"""
        # 50자 제한
        long_title = "a" * 60
        result = TodoValidator.sanitize_folder_name(long_title)
        self.assertEqual(len(result), 50)
        self.assertEqual(result, "a" * 50)
        
        # 50자 정확히
        title_50 = "a" * 50
        self.assertEqual(TodoValidator.sanitize_folder_name(title_50), title_50)
        
        # 언더스코어로 끝나는 경우 제거
        long_title_with_space = "a" * 49 + " "
        result = TodoValidator.sanitize_folder_name(long_title_with_space)
        self.assertEqual(result, "a" * 49)
    
    def test_sanitize_folder_name_underscore_handling(self):
        """언더스코어 처리 테스트"""
        # 연속된 언더스코어 축약
        self.assertEqual(TodoValidator.sanitize_folder_name("파일___이름"), "파일_이름")
        
        # 앞뒤 언더스코어 제거
        self.assertEqual(TodoValidator.sanitize_folder_name("_파일이름_"), "파일이름")
        
        # 복합 케이스
        self.assertEqual(TodoValidator.sanitize_folder_name("__파일  ___  이름__"), "파일_이름")


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)