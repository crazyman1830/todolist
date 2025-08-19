#!/usr/bin/env python3
"""
Unit tests for utility modules
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
from datetime import datetime, timedelta
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils
from utils.validators import Validators
from utils.performance_utils import PerformanceUtils


class TestDateUtils(unittest.TestCase):
    """DateUtils 단위 테스트"""
    
    def test_format_relative_time(self):
        """상대 시간 포맷팅 테스트"""
        now = datetime.now()
        
        # 과거 시간
        past_time = now - timedelta(hours=2)
        relative = DateUtils.format_relative_time(past_time)
        self.assertIn("전", relative)
        
        # 미래 시간
        future_time = now + timedelta(hours=2)
        relative = DateUtils.format_relative_time(future_time)
        self.assertIn("후", relative)
    
    def test_is_same_day(self):
        """같은 날짜 확인 테스트"""
        date1 = datetime(2024, 12, 25, 10, 0, 0)
        date2 = datetime(2024, 12, 25, 15, 30, 0)
        date3 = datetime(2024, 12, 26, 10, 0, 0)
        
        self.assertTrue(DateUtils.is_same_day(date1, date2))
        self.assertFalse(DateUtils.is_same_day(date1, date3))
    
    def test_get_urgency_level(self):
        """긴급도 레벨 계산 테스트"""
        now = datetime.now()
        
        # 지연된 할일
        overdue = now - timedelta(days=1)
        self.assertEqual(DateUtils.get_urgency_level(overdue), "overdue")
        
        # 오늘 마감
        today = now.replace(hour=23, minute=59)
        self.assertEqual(DateUtils.get_urgency_level(today), "due_today")
        
        # 내일 마감
        tomorrow = now + timedelta(days=1)
        self.assertEqual(DateUtils.get_urgency_level(tomorrow), "due_soon")
        
        # 일주일 후
        next_week = now + timedelta(days=7)
        self.assertEqual(DateUtils.get_urgency_level(next_week), "normal")


class TestColorUtils(unittest.TestCase):
    """ColorUtils 단위 테스트"""
    
    def test_get_urgency_color(self):
        """긴급도별 색상 테스트"""
        colors = {
            "overdue": ColorUtils.get_urgency_color("overdue"),
            "due_today": ColorUtils.get_urgency_color("due_today"),
            "due_soon": ColorUtils.get_urgency_color("due_soon"),
            "normal": ColorUtils.get_urgency_color("normal")
        }
        
        # 모든 색상이 반환되는지 확인
        for urgency, color in colors.items():
            self.assertIsNotNone(color)
            self.assertIsInstance(color, str)
    
    def test_get_progress_color(self):
        """진행률별 색상 테스트"""
        test_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for progress in test_values:
            color = ColorUtils.get_progress_color(progress)
            self.assertIsNotNone(color)
            self.assertIsInstance(color, str)
    
    def test_hex_to_rgb(self):
        """HEX to RGB 변환 테스트"""
        hex_color = "#FF0000"
        rgb = ColorUtils.hex_to_rgb(hex_color)
        self.assertEqual(rgb, (255, 0, 0))
    
    def test_rgb_to_hex(self):
        """RGB to HEX 변환 테스트"""
        rgb = (255, 0, 0)
        hex_color = ColorUtils.rgb_to_hex(rgb)
        self.assertEqual(hex_color, "#FF0000")


class TestValidators(unittest.TestCase):
    """Validators 단위 테스트"""
    
    def test_validate_todo_title(self):
        """할일 제목 검증 테스트"""
        # 유효한 제목
        self.assertTrue(Validators.validate_todo_title("유효한 할일"))
        self.assertTrue(Validators.validate_todo_title("A" * 100))  # 최대 길이
        
        # 무효한 제목
        self.assertFalse(Validators.validate_todo_title(""))  # 빈 문자열
        self.assertFalse(Validators.validate_todo_title("   "))  # 공백만
        self.assertFalse(Validators.validate_todo_title("A" * 256))  # 너무 긴 제목
    
    def test_validate_date_string(self):
        """날짜 문자열 검증 테스트"""
        # 유효한 날짜
        self.assertTrue(Validators.validate_date_string("2024-12-25"))
        self.assertTrue(Validators.validate_date_string("2024/12/25"))
        
        # 무효한 날짜
        self.assertFalse(Validators.validate_date_string("invalid-date"))
        self.assertFalse(Validators.validate_date_string("2024-13-01"))  # 잘못된 월
        self.assertFalse(Validators.validate_date_string("2024-02-30"))  # 잘못된 일
    
    def test_validate_file_path(self):
        """파일 경로 검증 테스트"""
        # 유효한 경로
        self.assertTrue(Validators.validate_file_path("/valid/path/file.txt"))
        self.assertTrue(Validators.validate_file_path("relative/path/file.txt"))
        
        # 무효한 경로
        self.assertFalse(Validators.validate_file_path(""))
        self.assertFalse(Validators.validate_file_path("path/with/invalid<>chars"))


class TestPerformanceUtils(unittest.TestCase):
    """PerformanceUtils 단위 테스트"""
    
    def test_measure_execution_time(self):
        """실행 시간 측정 테스트"""
        import time
        
        @PerformanceUtils.measure_execution_time
        def test_function():
            time.sleep(0.1)
            return "result"
        
        result = test_function()
        self.assertEqual(result, "result")
    
    def test_cache_result(self):
        """결과 캐싱 테스트"""
        call_count = 0
        
        @PerformanceUtils.cache_result(max_size=10, ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 첫 번째 호출
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # 두 번째 호출 (캐시에서 반환)
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # 호출 횟수 증가하지 않음
    
    def test_batch_operation(self):
        """배치 작업 테스트"""
        items = list(range(100))
        processed_batches = []
        
        def process_batch(batch):
            processed_batches.append(len(batch))
            return sum(batch)
        
        results = PerformanceUtils.batch_operation(items, process_batch, batch_size=10)
        
        self.assertEqual(len(results), 10)  # 10개 배치
        self.assertEqual(len(processed_batches), 10)
        self.assertTrue(all(size == 10 for size in processed_batches))


if __name__ == "__main__":
    unittest.main()