"""
DateUtils 테스트 모듈

날짜 유틸리티 함수들의 기능을 테스트합니다.
"""

import unittest
import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.date_utils import DateUtils


class TestDateUtils(unittest.TestCase):
    """DateUtils 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.reference_date = datetime(2025, 1, 15, 12, 0, 0)
    
    def test_get_relative_time_text_future(self):
        """미래 시간의 상대적 텍스트 테스트"""
        # 3일 후
        future_date = self.reference_date + timedelta(days=3)
        result = DateUtils.get_relative_time_text(future_date, self.reference_date)
        self.assertEqual(result, "3일 후")
        
        # 2시간 후
        future_date = self.reference_date + timedelta(hours=2)
        result = DateUtils.get_relative_time_text(future_date, self.reference_date)
        self.assertEqual(result, "2시간 후")
        
        # 30분 후
        future_date = self.reference_date + timedelta(minutes=30)
        result = DateUtils.get_relative_time_text(future_date, self.reference_date)
        self.assertEqual(result, "30분 후")
    
    def test_get_relative_time_text_past(self):
        """과거 시간의 상대적 텍스트 테스트"""
        # 2일 전
        past_date = self.reference_date - timedelta(days=2)
        result = DateUtils.get_relative_time_text(past_date, self.reference_date)
        self.assertEqual(result, "2일 전")
        
        # 1시간 전
        past_date = self.reference_date - timedelta(hours=1)
        result = DateUtils.get_relative_time_text(past_date, self.reference_date)
        self.assertEqual(result, "1시간 전")
    
    def test_parse_user_date_input_keywords(self):
        """키워드 입력 파싱 테스트"""
        result = DateUtils.parse_user_date_input("오늘")
        self.assertIsNotNone(result)
        self.assertEqual(result.hour, 18)  # 기본 시간
        
        result = DateUtils.parse_user_date_input("내일")
        self.assertIsNotNone(result)
        
        result = DateUtils.parse_user_date_input("모레")
        self.assertIsNotNone(result)
    
    def test_parse_user_date_input_formats(self):
        """다양한 날짜 형식 파싱 테스트"""
        # MM/DD HH:MM 형식
        result = DateUtils.parse_user_date_input("01/20 14:30")
        self.assertIsNotNone(result)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 20)
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 30)
        
        # MM/DD 형식
        result = DateUtils.parse_user_date_input("02/15")
        self.assertIsNotNone(result)
        self.assertEqual(result.month, 2)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 18)  # 기본 시간
        
        # "15일 18시" 형식
        result = DateUtils.parse_user_date_input("25일 20시")
        self.assertIsNotNone(result)
        self.assertEqual(result.day, 25)
        self.assertEqual(result.hour, 20)
    
    def test_parse_user_date_input_invalid(self):
        """잘못된 입력 파싱 테스트"""
        self.assertIsNone(DateUtils.parse_user_date_input(""))
        self.assertIsNone(DateUtils.parse_user_date_input("invalid"))
        self.assertIsNone(DateUtils.parse_user_date_input("13/40"))  # 잘못된 날짜
    
    def test_get_business_days_between(self):
        """영업일 계산 테스트"""
        # 월요일부터 금요일까지 (5일)
        start = datetime(2025, 1, 13)  # 월요일
        end = datetime(2025, 1, 17)    # 금요일
        
        business_days = DateUtils.get_business_days_between(start, end)
        self.assertEqual(business_days, 5)
        
        # 주말 포함 (월요일부터 일요일까지, 영업일은 5일)
        start = datetime(2025, 1, 13)  # 월요일
        end = datetime(2025, 1, 19)    # 일요일
        
        business_days = DateUtils.get_business_days_between(start, end)
        self.assertEqual(business_days, 5)
    
    def test_format_duration(self):
        """시간 간격 포맷팅 테스트"""
        # 2일 3시간
        duration = timedelta(days=2, hours=3)
        result = DateUtils.format_duration(duration)
        self.assertEqual(result, "2일 3시간")
        
        # 1시간 30분
        duration = timedelta(hours=1, minutes=30)
        result = DateUtils.format_duration(duration)
        self.assertEqual(result, "1시간 30분")
        
        # 45분
        duration = timedelta(minutes=45)
        result = DateUtils.format_duration(duration)
        self.assertEqual(result, "45분")
    
    def test_is_weekend(self):
        """주말 확인 테스트"""
        # 토요일
        saturday = datetime(2025, 1, 18)  # 토요일
        self.assertTrue(DateUtils.is_weekend(saturday))
        
        # 일요일
        sunday = datetime(2025, 1, 19)    # 일요일
        self.assertTrue(DateUtils.is_weekend(sunday))
        
        # 월요일
        monday = datetime(2025, 1, 20)    # 월요일
        self.assertFalse(DateUtils.is_weekend(monday))
    
    def test_get_next_weekday(self):
        """다음 요일 계산 테스트"""
        # 월요일에서 다음 금요일
        monday = datetime(2025, 1, 20)    # 월요일
        next_friday = DateUtils.get_next_weekday(monday, 4)  # 4 = 금요일
        
        self.assertEqual(next_friday.weekday(), 4)  # 금요일
        self.assertEqual((next_friday - monday).days, 4)
    
    def test_validate_date_range(self):
        """날짜 범위 유효성 검사 테스트"""
        start = datetime(2025, 1, 15)
        end = datetime(2025, 1, 20)
        
        is_valid, message = DateUtils.validate_date_range(start, end)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
        
        # 잘못된 범위 (시작이 끝보다 늦음)
        is_valid, message = DateUtils.validate_date_range(end, start)
        self.assertFalse(is_valid)
        self.assertIn("늦습니다", message)


if __name__ == '__main__':
    unittest.main()