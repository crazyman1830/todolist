"""
색상 관련 유틸리티 함수들

긴급도별 색상 매핑, 색상 변환, 접근성 관련 기능을 제공합니다.
"""

from typing import Dict, Tuple


class ColorUtils:
    """색상 관련 유틸리티 함수들"""
    
    # 긴급도별 색상 정의
    URGENCY_COLORS = {
        'overdue': '#ff4444',      # 빨간색 - 지연됨
        'urgent': '#ff8800',       # 주황색 - 24시간 이내
        'warning': '#ffcc00',      # 노란색 - 3일 이내
        'normal': '#000000'        # 검은색 - 일반
    }
    
    # 긴급도별 배경색 정의 (연한 색상)
    URGENCY_BACKGROUND_COLORS = {
        'overdue': '#ffe6e6',      # 연한 빨간색
        'urgent': '#fff2e6',       # 연한 주황색
        'warning': '#fffbe6',      # 연한 노란색
        'normal': '#ffffff'        # 흰색
    }
    
    # 완료된 항목 색상
    COMPLETED_COLORS = {
        'text': '#888888',         # 회색 텍스트
        'background': '#f5f5f5'    # 연한 회색 배경
    }
    
    @staticmethod
    def get_urgency_color(urgency_level: str) -> str:
        """
        긴급도에 따른 텍스트 색상 반환
        
        Requirements 3.1, 3.2, 3.3: 긴급도별 시각적 구분
        
        Args:
            urgency_level: 긴급도 레벨 ('overdue', 'urgent', 'warning', 'normal')
            
        Returns:
            str: 16진수 색상 코드
        """
        return ColorUtils.URGENCY_COLORS.get(urgency_level, ColorUtils.URGENCY_COLORS['normal'])
    
    @staticmethod
    def get_urgency_background_color(urgency_level: str) -> str:
        """
        긴급도에 따른 배경색 반환
        
        Args:
            urgency_level: 긴급도 레벨
            
        Returns:
            str: 16진수 배경색 코드
        """
        return ColorUtils.URGENCY_BACKGROUND_COLORS.get(
            urgency_level, 
            ColorUtils.URGENCY_BACKGROUND_COLORS['normal']
        )
    
    @staticmethod
    def get_completed_colors() -> Dict[str, str]:
        """
        완료된 항목의 색상 반환
        
        Requirements 3.4: 완료 시 긴급도 색상 제거
        
        Returns:
            Dict[str, str]: 완료된 항목의 텍스트 및 배경색
        """
        return ColorUtils.COMPLETED_COLORS.copy()
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        16진수 색상을 RGB 튜플로 변환
        
        Args:
            hex_color: 16진수 색상 코드 (#ffffff 형태)
            
        Returns:
            Tuple[int, int, int]: RGB 값 (0-255)
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return (0, 0, 0)  # 잘못된 형식이면 검은색 반환
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (0, 0, 0)
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        RGB 값을 16진수 색상으로 변환
        
        Args:
            r: 빨간색 값 (0-255)
            g: 초록색 값 (0-255)
            b: 파란색 값 (0-255)
            
        Returns:
            str: 16진수 색상 코드
        """
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def get_contrast_color(background_color: str) -> str:
        """
        배경색에 대한 대비가 좋은 텍스트 색상 반환
        
        Args:
            background_color: 배경색 16진수 코드
            
        Returns:
            str: 대비가 좋은 텍스트 색상 (검은색 또는 흰색)
        """
        r, g, b = ColorUtils.hex_to_rgb(background_color)
        
        # 밝기 계산 (0.299*R + 0.587*G + 0.114*B)
        brightness = (0.299 * r + 0.587 * g + 0.114 * b)
        
        # 밝기가 128보다 크면 검은색, 작으면 흰색
        return '#000000' if brightness > 128 else '#ffffff'
    
    @staticmethod
    def lighten_color(hex_color: str, factor: float = 0.2) -> str:
        """
        색상을 밝게 만들기
        
        Args:
            hex_color: 원본 색상
            factor: 밝기 증가 비율 (0.0-1.0)
            
        Returns:
            str: 밝아진 색상
        """
        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        
        # 각 색상 채널을 밝게 조정
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return ColorUtils.rgb_to_hex(r, g, b)
    
    @staticmethod
    def darken_color(hex_color: str, factor: float = 0.2) -> str:
        """
        색상을 어둡게 만들기
        
        Args:
            hex_color: 원본 색상
            factor: 어둡기 증가 비율 (0.0-1.0)
            
        Returns:
            str: 어두워진 색상
        """
        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        
        # 각 색상 채널을 어둡게 조정
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return ColorUtils.rgb_to_hex(r, g, b)
    
    @staticmethod
    def get_urgency_style_config(urgency_level: str, is_completed: bool = False) -> Dict[str, str]:
        """
        긴급도에 따른 완전한 스타일 설정 반환
        
        Args:
            urgency_level: 긴급도 레벨
            is_completed: 완료 여부
            
        Returns:
            Dict[str, str]: 스타일 설정 (foreground, background, font 등)
        """
        if is_completed:
            return {
                'foreground': ColorUtils.COMPLETED_COLORS['text'],
                'background': ColorUtils.COMPLETED_COLORS['background'],
                'font': ('TkDefaultFont', 9, 'overstrike')  # 취소선
            }
        
        config = {
            'foreground': ColorUtils.get_urgency_color(urgency_level),
            'background': ColorUtils.get_urgency_background_color(urgency_level),
            'font': ('TkDefaultFont', 9, 'normal')
        }
        
        # 긴급한 경우 굵은 글씨
        if urgency_level in ['overdue', 'urgent']:
            config['font'] = ('TkDefaultFont', 9, 'bold')
        
        return config
    
    @staticmethod
    def get_accessibility_patterns() -> Dict[str, str]:
        """
        색맹 사용자를 위한 패턴 정보 반환
        
        Requirements: 색맹 사용자를 위한 패턴/아이콘 추가
        
        Returns:
            Dict[str, str]: 긴급도별 패턴 정보
        """
        return {
            'overdue': '🔴',      # 빨간 원
            'urgent': '🟠',       # 주황 원
            'warning': '🟡',      # 노란 원
            'normal': '⚪',       # 흰 원
            'completed': '✅'     # 체크 마크
        }
    
    @staticmethod
    def get_accessibility_symbols() -> Dict[str, str]:
        """
        색맹 사용자를 위한 텍스트 기반 심볼 반환
        
        Requirements: 색맹 사용자를 위한 패턴/아이콘 추가
        
        Returns:
            Dict[str, str]: 긴급도별 텍스트 심볼
        """
        return {
            'overdue': '!!!',     # 매우 긴급
            'urgent': '!!',       # 긴급
            'warning': '!',       # 주의
            'normal': '',         # 일반
            'completed': '✓'      # 완료
        }
    
    @staticmethod
    def get_accessibility_descriptions() -> Dict[str, str]:
        """
        스크린 리더를 위한 접근성 설명 반환
        
        Requirements: 접근성 향상
        
        Returns:
            Dict[str, str]: 긴급도별 접근성 설명
        """
        return {
            'overdue': '지연됨 - 매우 긴급',
            'urgent': '24시간 이내 마감 - 긴급',
            'warning': '3일 이내 마감 - 주의 필요',
            'normal': '일반 우선순위',
            'completed': '완료됨 - 작업이 성공적으로 완료되었습니다'
        }
    
    @staticmethod
    def validate_hex_color(hex_color: str) -> bool:
        """
        16진수 색상 코드 유효성 검사
        
        Args:
            hex_color: 검사할 색상 코드
            
        Returns:
            bool: 유효하면 True
        """
        if not isinstance(hex_color, str):
            return False
        
        hex_color = hex_color.strip()
        
        # # 으로 시작하고 6자리 16진수인지 확인
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return False
        
        try:
            int(hex_color[1:], 16)
            return True
        except ValueError:
            return False