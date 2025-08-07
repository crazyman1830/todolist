"""
할일 비즈니스 로직 서비스

할일 추가, 조회, 수정, 삭제 등의 핵심 비즈니스 로직을 처리합니다.
"""

from typing import List, Optional
from datetime import datetime
from models.todo import Todo
from services.storage_service import StorageService
from services.file_service import FileService
from utils.validators import TodoValidator


class TodoService:
    """할일 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, storage_service: StorageService, file_service: FileService):
        """
        TodoService 초기화
        
        Args:
            storage_service: 데이터 저장/로드 서비스
            file_service: 파일 시스템 관리 서비스
        """
        self.storage_service = storage_service
        self.file_service = file_service
        self._todos_cache: Optional[List[Todo]] = None
    
    def add_todo(self, title: str) -> Todo:
        """
        새로운 할일을 추가합니다.
        
        Requirements 1.1, 1.2: 할일 추가 기능 및 폴더 생성
        
        Args:
            title: 할일 제목
            
        Returns:
            Todo: 생성된 할일 객체
            
        Raises:
            ValueError: 제목이 유효하지 않은 경우
            RuntimeError: 저장에 실패한 경우
        """
        # 제목 유효성 검사
        if not TodoValidator.validate_title(title):
            raise ValueError("할일 제목이 유효하지 않습니다.")
        
        # 현재 할일 목록 로드
        todos = self.get_all_todos()
        
        # 새 ID 생성
        next_id = self.storage_service.get_next_id()
        
        # 폴더 경로 생성
        temp_todo = Todo(
            id=next_id,
            title=title.strip(),
            created_at=datetime.now(),
            folder_path=""  # 임시로 빈 문자열
        )
        
        # 폴더 생성
        try:
            folder_path = self.file_service.create_todo_folder(temp_todo)
            # 실제 폴더 경로로 업데이트
            todo = Todo(
                id=next_id,
                title=title.strip(),
                created_at=temp_todo.created_at,
                folder_path=folder_path
            )
        except OSError as e:
            raise RuntimeError(f"할일 폴더 생성에 실패했습니다: {e}")
        
        # 할일 목록에 추가
        todos.append(todo)
        
        # 저장
        if not self.storage_service.save_todos(todos):
            # 저장 실패 시 생성된 폴더 삭제
            self.file_service.delete_todo_folder(folder_path)
            raise RuntimeError("할일 저장에 실패했습니다.")
        
        # 캐시 무효화
        self._todos_cache = None
        
        return todo
    
    def get_all_todos(self) -> List[Todo]:
        """
        모든 할일 목록을 조회합니다.
        
        Requirements 4.1, 4.2, 4.3: 할일 목록 조회 기능
        
        Returns:
            List[Todo]: 할일 목록 (생성 순서대로 정렬)
        """
        # 캐시가 있으면 캐시 반환
        if self._todos_cache is not None:
            return self._todos_cache.copy()
        
        # 저장소에서 로드
        todos = self.storage_service.load_todos()
        
        # 생성 시간 순으로 정렬 (Requirements 4.3)
        todos.sort(key=lambda x: x.created_at)
        
        # 캐시 업데이트
        self._todos_cache = todos.copy()
        
        return todos.copy()
    
    def update_todo(self, todo_id: int, new_title: str) -> bool:
        """
        기존 할일의 제목을 수정합니다.
        
        Requirements 2.1, 2.2, 2.3: 할일 수정 기능
        
        Args:
            todo_id: 수정할 할일의 ID
            new_title: 새로운 제목
            
        Returns:
            bool: 수정 성공 여부
            
        Raises:
            ValueError: 제목이 유효하지 않거나 할일을 찾을 수 없는 경우
        """
        # 제목 유효성 검사
        if not TodoValidator.validate_title(new_title):
            raise ValueError("할일 제목이 유효하지 않습니다.")
        
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        todo_to_update = None
        for todo in todos:
            if todo.id == todo_id:
                todo_to_update = todo
                break
        
        if todo_to_update is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 제목 업데이트
        old_title = todo_to_update.title
        todo_to_update.title = new_title.strip()
        
        # 저장
        if not self.storage_service.save_todos(todos):
            # 저장 실패 시 원래 제목으로 복원
            todo_to_update.title = old_title
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def delete_todo(self, todo_id: int, delete_folder: bool = False) -> bool:
        """
        할일을 삭제합니다.
        
        Requirements 3.1, 3.2, 3.3: 할일 삭제 기능 (폴더 삭제 옵션 포함)
        
        Args:
            todo_id: 삭제할 할일의 ID
            delete_folder: 관련 폴더도 삭제할지 여부
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            ValueError: 할일을 찾을 수 없는 경우
        """
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        todo_to_delete = None
        todo_index = -1
        for i, todo in enumerate(todos):
            if todo.id == todo_id:
                todo_to_delete = todo
                todo_index = i
                break
        
        if todo_to_delete is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 할일 목록에서 제거
        todos.pop(todo_index)
        
        # 저장
        if not self.storage_service.save_todos(todos):
            return False
        
        # 폴더 삭제 (요청된 경우)
        if delete_folder and todo_to_delete.folder_path:
            folder_deleted = self.file_service.delete_todo_folder(todo_to_delete.folder_path)
            if not folder_deleted:
                print(f"경고: 폴더 삭제에 실패했습니다: {todo_to_delete.folder_path}")
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        """
        ID로 특정 할일을 검색합니다.
        
        Args:
            todo_id: 검색할 할일의 ID
            
        Returns:
            Optional[Todo]: 찾은 할일 객체 (없으면 None)
        """
        todos = self.get_all_todos()
        
        for todo in todos:
            if todo.id == todo_id:
                return todo
        
        return None
    
    def get_max_todo_id(self) -> int:
        """
        현재 존재하는 할일 중 최대 ID를 반환합니다.
        
        Returns:
            int: 최대 ID (할일이 없으면 0)
        """
        todos = self.get_all_todos()
        if not todos:
            return 0
        
        return max(todo.id for todo in todos)
    
    def clear_cache(self) -> None:
        """캐시를 무효화합니다."""
        self._todos_cache = None