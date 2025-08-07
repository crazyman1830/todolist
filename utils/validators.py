"""
입력 유효성 검사 유틸리티 모듈

할일 제목, ID, 폴더명 등의 유효성 검사 및 정제 기능을 제공합니다.
"""

import re
from typing import Optional


class TodoValidator:
    """할일 관련 입력 유효성 검사 클래스"""
    
    @staticmethod
    def validate_title(title: str) -> bool:
        """
        할일 제목 유효성 검사
        
        Requirements 1.3: 빈 제목 입력 시 오류 메시지 표시
        
        Args:
            title: 검사할 할일 제목
            
        Returns:
            bool: 유효한 제목이면 True, 그렇지 않으면 False
        """
        if not title or not isinstance(title, str):
            return False
            
        # 공백만 있는 경우도 무효
        if not title.strip():
            return False
            
        # 제목 길이 제한 (1-100자)
        if len(title.strip()) > 100:
            return False
            
        return True
    
    @staticmethod
    def validate_todo_id(todo_id: str, max_id: int) -> Optional[int]:
        """
        할일 ID 유효성 검사
        
        Requirements 2.4, 3.4: 존재하지 않는 할일 선택 시 오류 메시지 표시
        
        Args:
            todo_id: 검사할 ID 문자열
            max_id: 현재 존재하는 최대 ID
            
        Returns:
            Optional[int]: 유효한 ID면 정수 반환, 그렇지 않으면 None
        """
        if not todo_id or not isinstance(todo_id, str):
            return None
            
        try:
            # 문자열을 정수로 변환
            id_int = int(todo_id.strip())
            
            # 양수이고 최대 ID 이하인지 확인
            if id_int > 0 and id_int <= max_id:
                return id_int
            else:
                return None
                
        except ValueError:
            # 정수로 변환할 수 없는 경우
            return None
    
    @staticmethod
    def sanitize_folder_name(title: str) -> str:
        """
        폴더명으로 사용할 수 있도록 제목을 정제
        
        파일 시스템에서 사용할 수 없는 문자들을 제거하거나 대체합니다.
        
        Args:
            title: 정제할 제목
            
        Returns:
            str: 정제된 폴더명
        """
        if not title or not isinstance(title, str):
            return "untitled"
            
        # 앞뒤 공백 제거
        sanitized = title.strip()
        
        if not sanitized:
            return "untitled"
        
        # Windows/Linux/macOS에서 사용할 수 없는 문자들을 언더스코어로 대체
        # < > : " | ? * \ /
        invalid_chars = r'[<>:"|?*\\/]'
        sanitized = re.sub(invalid_chars, '_', sanitized)
        
        # 연속된 공백을 언더스코어로 대체
        sanitized = re.sub(r'\s+', '_', sanitized)
        
        # 연속된 언더스코어를 하나로 축약
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # 앞뒤 언더스코어 제거
        sanitized = sanitized.strip('_')
        
        # 빈 문자열이 되면 기본값 사용
        if not sanitized:
            return "untitled"
        
        # 길이 제한 (50자)
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip('_')
        
        return sanitized