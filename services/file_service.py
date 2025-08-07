"""
파일 시스템 관리 서비스
할일별 폴더 생성, 삭제, 열기 등 파일 시스템 관련 기능을 제공합니다.
"""
import os
import shutil
import subprocess
import platform
import stat
from typing import Optional
from models.todo import Todo
from config import TODO_FOLDERS_DIR


class FileService:
    """파일 시스템 관리 서비스 클래스"""
    
    def __init__(self, base_folder_path: str = TODO_FOLDERS_DIR):
        """
        FileService 초기화
        
        Args:
            base_folder_path: 할일 폴더들이 저장될 기본 경로
        """
        self.base_folder_path = base_folder_path
        self.ensure_base_folder_exists()
    
    def create_todo_folder(self, todo: Todo) -> str:
        """
        할일을 위한 전용 폴더를 생성합니다.
        
        Args:
            todo: 폴더를 생성할 할일 객체
            
        Returns:
            str: 생성된 폴더의 전체 경로
            
        Raises:
            OSError: 폴더 생성에 실패한 경우
        """
        if not todo or not hasattr(todo, 'get_folder_name'):
            raise ValueError("유효하지 않은 할일 객체입니다")
        
        try:
            folder_name = todo.get_folder_name()
            if not folder_name or folder_name.strip() == "":
                raise ValueError("폴더명이 비어있습니다")
            
            folder_path = os.path.join(self.base_folder_path, folder_name)
            
            # 경로 길이 제한 확인 (Windows: 260자, Unix: 4096자)
            max_path_length = 260 if os.name == 'nt' else 4096
            if len(folder_path) > max_path_length:
                raise OSError(f"폴더 경로가 너무 깁니다 ({len(folder_path)} > {max_path_length})")
            
            # 폴더가 이미 존재하지 않는 경우에만 생성
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
            elif not os.path.isdir(folder_path):
                raise OSError(f"같은 이름의 파일이 이미 존재합니다: {folder_path}")
            
            # 폴더 생성 확인
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                raise OSError(f"폴더 생성 확인 실패: {folder_path}")
            
            return folder_path
            
        except (OSError, PermissionError) as e:
            raise OSError(f"폴더 생성에 실패했습니다: {folder_path} - {e}") from e
        except Exception as e:
            raise OSError(f"폴더 생성 중 예상치 못한 오류: {e}") from e
    
    def delete_todo_folder(self, folder_path: str) -> bool:
        """
        할일 폴더와 그 내용을 모두 삭제합니다.
        
        Args:
            folder_path: 삭제할 폴더의 경로
            
        Returns:
            bool: 삭제 성공 여부
        """
        if not folder_path or folder_path.strip() == "":
            print("경고: 빈 폴더 경로입니다")
            return False
        
        # 안전성 검사: 기본 폴더 내부의 폴더만 삭제 허용
        try:
            abs_folder_path = os.path.abspath(folder_path)
            abs_base_path = os.path.abspath(self.base_folder_path)
            
            if not abs_folder_path.startswith(abs_base_path):
                print(f"보안 오류: 기본 폴더 외부의 폴더 삭제 시도: {folder_path}")
                return False
        except Exception as e:
            print(f"경로 검증 중 오류: {e}")
            return False
        
        try:
            if not os.path.exists(folder_path):
                print(f"폴더가 존재하지 않습니다: {folder_path}")
                return False
            
            if not os.path.isdir(folder_path):
                print(f"폴더가 아닙니다: {folder_path}")
                return False
            
            # 읽기 전용 파일들의 권한을 변경하여 삭제 가능하게 함
            def handle_remove_readonly(func, path, exc):
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            
            shutil.rmtree(folder_path, onerror=handle_remove_readonly)
            
            # 삭제 확인
            if os.path.exists(folder_path):
                print(f"폴더 삭제 확인 실패: {folder_path}")
                return False
            
            return True
            
        except PermissionError as e:
            print(f"폴더 삭제 권한 오류: {e}")
            return False
        except OSError as e:
            print(f"폴더 삭제 중 시스템 오류: {e}")
            return False
        except Exception as e:
            print(f"폴더 삭제 중 예상치 못한 오류: {e}")
            return False
    
    def open_todo_folder(self, folder_path: str) -> bool:
        """
        할일 폴더를 시스템의 기본 파일 탐색기에서 엽니다.
        크로스 플랫폼을 지원합니다.
        
        Args:
            folder_path: 열 폴더의 경로
            
        Returns:
            bool: 폴더 열기 성공 여부
        """
        if not self.folder_exists(folder_path):
            print(f"폴더가 존재하지 않습니다: {folder_path}")
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows에서는 explorer 사용
                subprocess.run(["explorer", folder_path], check=True)
            elif system == "Darwin":  # macOS
                # macOS에서는 open 사용
                subprocess.run(["open", folder_path], check=True)
            elif system == "Linux":
                # Linux에서는 xdg-open 사용
                subprocess.run(["xdg-open", folder_path], check=True)
            else:
                print(f"지원하지 않는 운영체제입니다: {system}")
                return False
                
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"폴더 열기 중 오류가 발생했습니다: {e}")
            return False
    
    def folder_exists(self, folder_path: str) -> bool:
        """
        폴더가 존재하는지 확인합니다.
        
        Args:
            folder_path: 확인할 폴더의 경로
            
        Returns:
            bool: 폴더 존재 여부
        """
        return os.path.exists(folder_path) and os.path.isdir(folder_path)
    
    def ensure_base_folder_exists(self) -> None:
        """
        기본 폴더 디렉토리가 존재하는지 확인하고, 없으면 생성합니다.
        """
        try:
            if not os.path.exists(self.base_folder_path):
                os.makedirs(self.base_folder_path, exist_ok=True)
        except OSError as e:
            print(f"기본 폴더 생성에 실패했습니다: {e}")
    
    def get_todo_folder_path(self, todo: Todo) -> str:
        """
        할일 객체로부터 폴더 경로를 생성합니다.
        
        Args:
            todo: 할일 객체
            
        Returns:
            str: 할일 폴더의 전체 경로
        """
        folder_name = todo.get_folder_name()
        return os.path.join(self.base_folder_path, folder_name)