"""
날짜 관련 비즈니스 로직을 처리하는 서비스 모듈

목표 날짜 기반 긴급도 계산, 시간 표시, 날짜 포맷팅 등의 기능을 제공합니다.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from utils.performance_utils import cached_urgency_calculation


class DateService:
    """날짜 관련 비즈니스 로직을 처리하는 서비스"""
    
    @staticmethod
    @cached_urgency_calculation
    def get_urgency_level(due_date: Optional[datetime]) -> str:
        """
        목표 날짜를 기준으로 긴급도 레벨 반환
        
        Requirements 3.1, 3.2, 3.3: 목표 날짜 기준 시각적 구분
        - 지난 날짜: 'overdue' (빨간색)
        - 24시간 이내: 'urgent' (주황색)  
        - 3일 이내: 'warning' (노란색)
        - 그 외: 'normal' (기본색)
        
        Args:
            due_date: 목표 날짜 (None이면 'normal' 반환)
            
        Returns:
            str: 긴급도 레벨 ('overdue', 'urgent', 'warning', 'normal')
        """
        if due_date is None:
            return 'normal'
            
        now = datetime.now()
        time_diff = due_date - now
        
        # 목표 날짜가 지난 경우
        if time_diff.total_seconds() < 0:
            return 'overdue'
        
        # 24시간 이내
        if time_diff.total_seconds() <= 24 * 3600:
            return 'urgent'
        
        # 3일 이내
        if time_diff.days <= 3:
            return 'warning'
        
        return 'normal'
    
    @staticmethod
    def get_time_remaining_text(due_date: Optional[datetime], 
                               completed_at: Optional[datetime] = None) -> str:
        """
        남은 시간을 사용자 친화적 텍스트로 반환
        
        Requirements 5.1, 5.2, 5.3, 5.4: 남은 시간 직관적 표시
        - 완료된 경우: 완료 날짜 표시
        - D-day 형태: "D-3", "D-day", "D+2"
        - 24시간 이내: "3시간 후", "30분 후"
        - 지연: "2일 지남", "3시간 지남"
        
        Args:
            due_date: 목표 날짜
            completed_at: 완료 날짜 (완료된 경우)
            
        Returns:
            str: 시간 표시 텍스트
        """
        if due_date is None:
            return ""
        
        # 완료된 경우 완료 날짜 표시
        if completed_at is not None:
            return f"완료: {completed_at.strftime('%m/%d %H:%M')}"
        
        now = datetime.now()
        time_diff = due_date - now
        total_seconds = time_diff.total_seconds()
        
        # 지연된 경우
        if total_seconds < 0:
            abs_diff = abs(time_diff)
            if abs_diff.days > 0:
                return f"{abs_diff.days}일 지남"
            else:
                hours = int(abs_diff.total_seconds() // 3600)
                if hours > 0:
                    return f"{hours}시간 지남"
                else:
                    minutes = int(abs_diff.total_seconds() // 60)
                    return f"{minutes}분 지남"
        
        # 24시간 이내인 경우 시간/분 단위로 표시
        if total_seconds <= 24 * 3600:
            if total_seconds <= 3600:  # 1시간 이내
                minutes = int(total_seconds // 60)
                if minutes <= 0:
                    return "곧 마감"
                return f"{minutes}분 후"
            else:
                hours = int(total_seconds // 3600)
                return f"{hours}시간 후"
        
        # D-day 형태로 표시
        days = time_diff.days
        if days == 0:
            return "D-day"
        else:
            return f"D-{days}"
    
    @staticmethod
    def format_due_date(due_date: Optional[datetime], 
                       format_type: str = 'relative') -> str:
        """
        목표 날짜를 지정된 형식으로 포맷팅
        
        Args:
            due_date: 포맷팅할 날짜
            format_type: 포맷 타입 ('relative', 'absolute', 'short')
            
        Returns:
            str: 포맷팅된 날짜 문자열
        """
        if due_date is None:
            return ""
        
        if format_type == 'relative':
            now = datetime.now()
            today = now.date()
            due_date_only = due_date.date()
            
            if due_date_only == today:
                return f"오늘 {due_date.strftime('%H:%M')}"
            elif due_date_only == today + timedelta(days=1):
                return f"내일 {due_date.strftime('%H:%M')}"
            elif due_date_only == today - timedelta(days=1):
                return f"어제 {due_date.strftime('%H:%M')}"
            else:
                return due_date.strftime('%m/%d %H:%M')
        
        elif format_type == 'absolute':
            return due_date.strftime('%Y-%m-%d %H:%M')
        
        elif format_type == 'short':
            return due_date.strftime('%m/%d')
        
        else:
            return due_date.strftime('%m/%d %H:%M')
    
    @staticmethod
    def is_same_day(date1: datetime, date2: datetime) -> bool:
        """
        두 날짜가 같은 날인지 확인
        
        Args:
            date1: 첫 번째 날짜
            date2: 두 번째 날짜
            
        Returns:
            bool: 같은 날이면 True
        """
        return date1.date() == date2.date()
    
    @staticmethod
    def get_quick_date_options() -> Dict[str, datetime]:
        """
        빠른 날짜 선택 옵션들 반환
        
        Returns:
            Dict[str, datetime]: 옵션명과 날짜의 매핑
        """
        now = datetime.now()
        today = now.replace(hour=18, minute=0, second=0, microsecond=0)  # 기본 6시
        
        options = {
            "오늘": today,
            "내일": today + timedelta(days=1),
            "모레": today + timedelta(days=2),
            "이번 주말": DateService._get_this_weekend(),
            "다음 주": today + timedelta(days=7),
            "1주일 후": today + timedelta(days=7),
            "2주일 후": today + timedelta(days=14),
            "1개월 후": today + timedelta(days=30)
        }
        
        return options
    
    @staticmethod
    def _get_this_weekend() -> datetime:
        """이번 주말 날짜 계산 (토요일)"""
        now = datetime.now()
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.weekday() == 5:  # 이미 토요일인 경우
            days_until_saturday = 7
        
        weekend = now + timedelta(days=days_until_saturday)
        return weekend.replace(hour=18, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def validate_due_date(due_date: datetime, 
                         parent_due_date: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        목표 날짜 유효성 검사
        
        Args:
            due_date: 검사할 목표 날짜
            parent_due_date: 상위 할일의 목표 날짜 (하위 작업인 경우)
            
        Returns:
            Tuple[bool, str]: (유효성 여부, 오류 메시지)
        """
        now = datetime.now()
        
        # 과거 날짜 체크 (1시간 전까지는 허용)
        if due_date < now - timedelta(hours=1):
            return False, "목표 날짜가 너무 과거입니다. 현재 시간 이후로 설정해주세요."
        
        # 너무 먼 미래 체크 (10년 후)
        if due_date > now + timedelta(days=3650):
            return False, "목표 날짜가 너무 먼 미래입니다. 10년 이내로 설정해주세요."
        
        # 상위 할일의 목표 날짜보다 늦은지 체크
        if parent_due_date is not None and due_date > parent_due_date:
            return False, f"하위 작업의 목표 날짜는 상위 할일의 목표 날짜({DateService.format_due_date(parent_due_date)})보다 빨라야 합니다."
        
        return True, ""
    
    @staticmethod
    def get_date_filter_ranges() -> Dict[str, Tuple[datetime, datetime]]:
        """
        날짜 필터링을 위한 범위들 반환
        
        Requirements 4.2, 4.3, 4.4: 날짜 기준 필터링
        
        Returns:
            Dict[str, Tuple[datetime, datetime]]: 필터명과 날짜 범위의 매핑
        """
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 이번 주 시작 (월요일)
        days_since_monday = now.weekday()
        week_start = today_start - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
        
        # 이번 달
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month = month_start.replace(year=now.year + 1, month=1)
        else:
            next_month = month_start.replace(month=now.month + 1)
        month_end = next_month - timedelta(microseconds=1)
        
        ranges = {
            "오늘": (today_start, today_end),
            "내일": (today_start + timedelta(days=1), today_end + timedelta(days=1)),
            "이번 주": (week_start, week_end),
            "이번 달": (month_start, month_end),
            "지연됨": (datetime.min, now),  # 현재 시간 이전
        }
        
        return ranges