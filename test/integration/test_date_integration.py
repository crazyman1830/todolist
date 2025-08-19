"""
날짜 관련 기능 통합 테스트

DateService, DateUtils, ColorUtils가 함께 작동하는지 테스트합니다.
"""

import unittest
import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.date_service import DateService
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils


class TestDateIntegration(unittest.TestCase):
    """날짜 관련 기능 통합 테스트 클래스"""
    
    def test_urgency_workflow(self):
        """긴급도 계산부터 색상 적용까지의 전체 워크플로우 테스트"""
        now = datetime.now()
        
        # 지연된 할일
        overdue_date = now - timedelta(hours=2)
        urgency = DateService.get_urgency_level(overdue_date)
        self.assertEqual(urgency, 'overdue')
        
        color = ColorUtils.get_urgency_color(urgency)
        self.assertEqual(color, '#ff4444')
        
        time_text = DateService.get_time_remaining_text(overdue_date)
        self.assertIn('지남', time_text)
        
        # 긴급한 할일 (24시간 이내)
        urgent_date = now + timedelta(hours=12)
        urgency = DateService.get_urgency_level(urgent_date)
        self.assertEqual(urgency, 'urgent')
        
        color = ColorUtils.get_urgency_color(urgency)
        self.assertEqual(color, '#ff8800')
        
        time_text = DateService.get_time_remaining_text(urgent_date)
        self.assertIn('시간 후', time_text)
    
    def test_date_parsing_and_formatting(self):
        """날짜 파싱과 포맷팅 통합 테스트"""
        # 사용자 입력 파싱
        parsed_date = DateUtils.parse_user_date_input("내일")
        self.assertIsNotNone(parsed_date)
        
        # 포맷팅
        formatted = DateService.format_due_date(parsed_date, 'relative')
        self.assertIn('내일', formatted)
        
        # 긴급도 계산
        urgency = DateService.get_urgency_level(parsed_date)
        self.assertIn(urgency, ['urgent', 'warning', 'normal'])
    
    def test_completed_task_styling(self):
        """완료된 작업의 스타일링 테스트"""
        due_date = datetime.now() + timedelta(days=1)
        completed_at = datetime.now()
        
        # 완료된 작업의 시간 텍스트
        time_text = DateService.get_time_remaining_text(due_date, completed_at)
        self.assertIn('완료:', time_text)
        
        # 완료된 작업의 스타일
        style = ColorUtils.get_urgency_style_config('normal', is_completed=True)
        self.assertEqual(style['foreground'], '#888888')
        self.assertIn('overstrike', style['font'])
    
    def test_filter_ranges_and_urgency(self):
        """필터 범위와 긴급도의 일관성 테스트"""
        ranges = DateService.get_date_filter_ranges()
        
        # 오늘 범위의 할일들
        today_start, today_end = ranges['오늘']
        
        # 오늘 마감인 할일 (긴급함)
        today_due = today_end.replace(hour=18)
        urgency = DateService.get_urgency_level(today_due)
        self.assertEqual(urgency, 'urgent')
        
        # 지연된 할일 범위
        overdue_start, overdue_end = ranges['지연됨']
        self.assertLessEqual(overdue_end, datetime.now())
    
    def test_accessibility_features(self):
        """접근성 기능 테스트"""
        patterns = ColorUtils.get_accessibility_patterns()
        
        # 각 긴급도에 대한 패턴이 있는지 확인
        urgency_levels = ['overdue', 'urgent', 'warning', 'normal', 'completed']
        for level in urgency_levels:
            self.assertIn(level, patterns)
            self.assertIsInstance(patterns[level], str)
            self.assertGreater(len(patterns[level]), 0)
    
    def test_business_logic_consistency(self):
        """비즈니스 로직 일관성 테스트"""
        now = datetime.now()
        
        # 다양한 시점의 할일들
        test_dates = [
            now - timedelta(days=1),    # 지연됨
            now + timedelta(hours=12),  # 긴급
            now + timedelta(days=2),    # 경고
            now + timedelta(days=7),    # 일반
        ]
        
        expected_urgencies = ['overdue', 'urgent', 'warning', 'normal']
        
        for i, test_date in enumerate(test_dates):
            urgency = DateService.get_urgency_level(test_date)
            self.assertEqual(urgency, expected_urgencies[i])
            
            # 색상이 정의되어 있는지 확인
            color = ColorUtils.get_urgency_color(urgency)
            self.assertTrue(ColorUtils.validate_hex_color(color))
            
            # 시간 텍스트가 생성되는지 확인
            time_text = DateService.get_time_remaining_text(test_date)
            self.assertIsInstance(time_text, str)
            self.assertGreater(len(time_text), 0)
    
    def test_validation_workflow(self):
        """유효성 검사 워크플로우 테스트"""
        now = datetime.now()
        
        # 유효한 날짜
        valid_date = now + timedelta(days=3)
        is_valid, message = DateService.validate_due_date(valid_date)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
        
        # 무효한 날짜 (과거)
        invalid_date = now - timedelta(days=1)
        is_valid, message = DateService.validate_due_date(invalid_date)
        self.assertFalse(is_valid)
        self.assertGreater(len(message), 0)
        
        # 상위 할일과의 관계 검증
        parent_due = now + timedelta(days=5)
        child_due = now + timedelta(days=7)  # 상위보다 늦음
        
        is_valid, message = DateService.validate_due_date(child_due, parent_due)
        self.assertFalse(is_valid)
        self.assertIn('빨라야', message)


if __name__ == '__main__':
    unittest.main()