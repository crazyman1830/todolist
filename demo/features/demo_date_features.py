"""
날짜 관련 기능 데모 스크립트

DateService, DateUtils, ColorUtils의 기능을 시연합니다.
"""

import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.date_service import DateService
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils


def demo_urgency_levels():
    """긴급도 레벨 데모"""
    print("=== 긴급도 레벨 데모 ===")
    now = datetime.now()
    
    test_cases = [
        ("지연된 할일", now - timedelta(hours=2)),
        ("긴급한 할일 (12시간 후)", now + timedelta(hours=12)),
        ("경고 할일 (2일 후)", now + timedelta(days=2)),
        ("일반 할일 (1주일 후)", now + timedelta(days=7)),
        ("목표 날짜 없음", None)
    ]
    
    for description, due_date in test_cases:
        urgency = DateService.get_urgency_level(due_date)
        color = ColorUtils.get_urgency_color(urgency)
        time_text = DateService.get_time_remaining_text(due_date)
        
        print(f"{description:20} | 긴급도: {urgency:8} | 색상: {color} | 시간: {time_text}")
    print()


def demo_date_parsing():
    """날짜 파싱 데모"""
    print("=== 날짜 파싱 데모 ===")
    
    test_inputs = [
        "오늘",
        "내일", 
        "모레",
        "01/25 14:30",
        "02/15",
        "25일 18시",
        "30일"
    ]
    
    for input_text in test_inputs:
        parsed = DateUtils.parse_user_date_input(input_text)
        if parsed:
            formatted = DateService.format_due_date(parsed, 'relative')
            print(f"입력: {input_text:12} | 파싱 결과: {formatted}")
        else:
            print(f"입력: {input_text:12} | 파싱 실패")
    print()


def demo_time_formatting():
    """시간 포맷팅 데모"""
    print("=== 시간 포맷팅 데모 ===")
    now = datetime.now()
    
    test_cases = [
        ("30분 후", now + timedelta(minutes=30)),
        ("3시간 후", now + timedelta(hours=3)),
        ("내일", now + timedelta(days=1)),
        ("3일 후", now + timedelta(days=3)),
        ("1주일 후", now + timedelta(days=7)),
        ("2시간 전", now - timedelta(hours=2)),
        ("1일 전", now - timedelta(days=1))
    ]
    
    for description, target_date in test_cases:
        relative_text = DateUtils.get_relative_time_text(target_date)
        remaining_text = DateService.get_time_remaining_text(target_date)
        formatted = DateService.format_due_date(target_date, 'relative')
        
        print(f"{description:10} | 상대시간: {relative_text:10} | 남은시간: {remaining_text:12} | 포맷: {formatted}")
    print()


def demo_color_features():
    """색상 기능 데모"""
    print("=== 색상 기능 데모 ===")
    
    urgency_levels = ['overdue', 'urgent', 'warning', 'normal']
    
    for urgency in urgency_levels:
        text_color = ColorUtils.get_urgency_color(urgency)
        bg_color = ColorUtils.get_urgency_background_color(urgency)
        pattern = ColorUtils.get_accessibility_patterns()[urgency]
        
        # 스타일 설정
        style = ColorUtils.get_urgency_style_config(urgency, False)
        completed_style = ColorUtils.get_urgency_style_config(urgency, True)
        
        print(f"긴급도: {urgency:8} | 텍스트: {text_color} | 배경: {bg_color} | 패턴: {pattern}")
        print(f"  일반 스타일: {style}")
        print(f"  완료 스타일: {completed_style}")
        print()


def demo_validation():
    """유효성 검사 데모"""
    print("=== 유효성 검사 데모 ===")
    now = datetime.now()
    
    test_cases = [
        ("유효한 미래 날짜", now + timedelta(days=3), None),
        ("과거 날짜", now - timedelta(days=1), None),
        ("너무 먼 미래", now + timedelta(days=4000), None),
        ("하위 작업 (유효)", now + timedelta(days=3), now + timedelta(days=5)),
        ("하위 작업 (무효)", now + timedelta(days=7), now + timedelta(days=5))
    ]
    
    for description, due_date, parent_due in test_cases:
        is_valid, message = DateService.validate_due_date(due_date, parent_due)
        status = "✓ 유효" if is_valid else "✗ 무효"
        
        print(f"{description:20} | {status} | {message}")
    print()


def demo_filter_ranges():
    """필터 범위 데모"""
    print("=== 필터 범위 데모 ===")
    
    ranges = DateService.get_date_filter_ranges()
    
    for filter_name, (start, end) in ranges.items():
        duration = end - start
        print(f"필터: {filter_name:8} | 시작: {start.strftime('%m/%d %H:%M')} | 종료: {end.strftime('%m/%d %H:%M')} | 기간: {DateUtils.format_duration(duration)}")
    print()


def demo_quick_dates():
    """빠른 날짜 선택 데모"""
    print("=== 빠른 날짜 선택 데모 ===")
    
    options = DateService.get_quick_date_options()
    
    for option_name, option_date in options.items():
        formatted = DateService.format_due_date(option_date, 'relative')
        urgency = DateService.get_urgency_level(option_date)
        
        print(f"옵션: {option_name:10} | 날짜: {formatted:15} | 긴급도: {urgency}")
    print()


def main():
    """메인 데모 함수"""
    print("날짜 관련 기능 데모")
    print("=" * 50)
    print()
    
    demo_urgency_levels()
    demo_date_parsing()
    demo_time_formatting()
    demo_color_features()
    demo_validation()
    demo_filter_ranges()
    demo_quick_dates()
    
    print("데모 완료!")


if __name__ == '__main__':
    main()