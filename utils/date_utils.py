"""
날짜 관련 유틸리티 함수들

날짜 파싱, 포맷팅, 계산 등의 유틸리티 기능을 제공합니다.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


class DateUtils:
    """날짜 관련 유틸리티 함수들"""
    
    @staticmethod
    def get_relative_time_text(target_date: datetime, 
                              reference_date: Optional[datetime] = None) -> str:
        """
        상대적 시간 텍스트 반환
        
        Requirements 5.1, 5.2, 5.3: 직관적인 시간 표시
        
        Args:
            target_date: 대상 날짜
            reference_date: 기준 날짜 (None이면 현재 시간)
            
        Returns:
            str: 상대적 시간 텍스트
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        time_diff = target_date - reference_date
        total_seconds = time_diff.total_seconds()
        
        # 미래인 경우
        if total_seconds > 0:
            if time_diff.days > 0:
                return f"{time_diff.days}일 후"
            elif total_seconds >= 3600:  # 1시간 이상
                hours = int(total_seconds // 3600)
                return f"{hours}시간 후"
            elif total_seconds >= 60:  # 1분 이상
                minutes = int(total_seconds // 60)
                return f"{minutes}분 후"
            else:
                return "곧"
        
        # 과거인 경우
        else:
            abs_diff = abs(time_diff)
            if abs_diff.days > 0:
                return f"{abs_diff.days}일 전"
            elif abs_diff.total_seconds() >= 3600:  # 1시간 이상
                hours = int(abs_diff.total_seconds() // 3600)
                return f"{hours}시간 전"
            elif abs_diff.total_seconds() >= 60:  # 1분 이상
                minutes = int(abs_diff.total_seconds() // 60)
                return f"{minutes}분 전"
            else:
                return "방금"
    
    @staticmethod
    def parse_user_date_input(date_string: str) -> Optional[datetime]:
        """
        사용자 입력 날짜 문자열 파싱
        
        다양한 형식의 날짜 입력을 파싱합니다:
        - "2025-01-15 18:00"
        - "01/15 18:00"
        - "15일 18시"
        - "내일"
        - "오늘"
        
        Args:
            date_string: 파싱할 날짜 문자열
            
        Returns:
            Optional[datetime]: 파싱된 날짜 (실패시 None)
        """
        if not date_string or not isinstance(date_string, str):
            return None
        
        date_string = date_string.strip()
        now = datetime.now()
        
        # 특수 키워드 처리
        if date_string in ["오늘", "today"]:
            return now.replace(hour=18, minute=0, second=0, microsecond=0)
        elif date_string in ["내일", "tomorrow"]:
            return (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
        elif date_string in ["모레"]:
            return (now + timedelta(days=2)).replace(hour=18, minute=0, second=0, microsecond=0)
        
        # ISO 형식: 2025-01-15 18:00
        try:
            return datetime.fromisoformat(date_string.replace('T', ' '))
        except ValueError:
            pass
        
        # MM/DD HH:MM 형식
        pattern1 = r'^(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})$'
        match = re.match(pattern1, date_string)
        if match:
            month, day, hour, minute = map(int, match.groups())
            try:
                year = now.year
                # 과거 날짜면 내년으로 설정
                target_date = datetime(year, month, day, hour, minute)
                if target_date < now:
                    target_date = target_date.replace(year=year + 1)
                return target_date
            except ValueError:
                pass
        
        # MM/DD 형식 (시간은 18:00으로 기본 설정)
        pattern2 = r'^(\d{1,2})/(\d{1,2})$'
        match = re.match(pattern2, date_string)
        if match:
            month, day = map(int, match.groups())
            try:
                year = now.year
                target_date = datetime(year, month, day, 18, 0)
                if target_date < now:
                    target_date = target_date.replace(year=year + 1)
                return target_date
            except ValueError:
                pass
        
        # "15일 18시" 형식
        pattern3 = r'^(\d{1,2})일\s+(\d{1,2})시$'
        match = re.match(pattern3, date_string)
        if match:
            day, hour = map(int, match.groups())
            try:
                year = now.year
                month = now.month
                target_date = datetime(year, month, day, hour, 0)
                if target_date < now:
                    # 다음 달로 설정
                    if month == 12:
                        target_date = target_date.replace(year=year + 1, month=1)
                    else:
                        target_date = target_date.replace(month=month + 1)
                return target_date
            except ValueError:
                pass
        
        # "15일" 형식 (시간은 18:00으로 기본 설정)
        pattern4 = r'^(\d{1,2})일$'
        match = re.match(pattern4, date_string)
        if match:
            day = int(match.group(1))
            try:
                year = now.year
                month = now.month
                target_date = datetime(year, month, day, 18, 0)
                if target_date < now:
                    # 다음 달로 설정
                    if month == 12:
                        target_date = target_date.replace(year=year + 1, month=1)
                    else:
                        target_date = target_date.replace(month=month + 1)
                return target_date
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def get_business_days_between(start_date: datetime, end_date: datetime) -> int:
        """
        두 날짜 사이의 영업일 수 계산 (주말 제외)
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            int: 영업일 수
        """
        if start_date > end_date:
            return 0
        
        business_days = 0
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # 월요일(0) ~ 금요일(4)만 영업일로 계산
            if current_date.weekday() < 5:
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def format_duration(duration: timedelta) -> str:
        """
        시간 간격을 사용자 친화적 문자열로 포맷팅
        
        Args:
            duration: 시간 간격
            
        Returns:
            str: 포맷팅된 문자열
        """
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 0:
            return "0초"
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}일")
        if hours > 0:
            parts.append(f"{hours}시간")
        if minutes > 0 and days == 0:  # 일 단위가 있으면 분은 생략
            parts.append(f"{minutes}분")
        if seconds > 0 and days == 0 and hours == 0:  # 일, 시간 단위가 있으면 초는 생략
            parts.append(f"{seconds}초")
        
        if not parts:
            return "0초"
        
        return " ".join(parts)
    
    @staticmethod
    def is_weekend(date: datetime) -> bool:
        """
        주말인지 확인
        
        Args:
            date: 확인할 날짜
            
        Returns:
            bool: 주말이면 True (토요일, 일요일)
        """
        return date.weekday() >= 5  # 토요일(5), 일요일(6)
    
    @staticmethod
    def get_next_weekday(date: datetime, weekday: int) -> datetime:
        """
        다음 특정 요일 날짜 반환
        
        Args:
            date: 기준 날짜
            weekday: 요일 (0=월요일, 6=일요일)
            
        Returns:
            datetime: 다음 해당 요일 날짜
        """
        days_ahead = weekday - date.weekday()
        if days_ahead <= 0:  # 오늘이거나 이미 지난 요일
            days_ahead += 7
        
        return date + timedelta(days=days_ahead)
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
        """
        날짜 범위 유효성 검사
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            Tuple[bool, str]: (유효성 여부, 오류 메시지)
        """
        if start_date > end_date:
            return False, "시작 날짜가 종료 날짜보다 늦습니다."
        
        # 너무 긴 기간 체크 (1년)
        if (end_date - start_date).days > 365:
            return False, "날짜 범위가 너무 깁니다. 1년 이내로 설정해주세요."
        
        return True, ""