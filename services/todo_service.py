"""
할일 비즈니스 로직 서비스

할일 추가, 조회, 수정, 삭제 등의 핵심 비즈니스 로직을 처리합니다.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from models.todo import Todo
from models.subtask import SubTask
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
            # 더 상세한 오류 메시지 제공
            error_msg = str(e)
            if "Permission denied" in error_msg or "권한" in error_msg:
                raise RuntimeError(f"할일 폴더 생성 권한이 없습니다.\n관리자 권한으로 실행하거나 다른 위치를 선택해주세요.\n상세 오류: {e}")
            elif "No space left" in error_msg or "공간" in error_msg:
                raise RuntimeError(f"디스크 공간이 부족하여 폴더를 생성할 수 없습니다.\n불필요한 파일을 삭제한 후 다시 시도해주세요.\n상세 오류: {e}")
            elif "File name too long" in error_msg or "경로가 너무" in error_msg:
                raise RuntimeError(f"할일 제목이 너무 길어 폴더를 생성할 수 없습니다.\n제목을 짧게 수정해주세요.\n상세 오류: {e}")
            else:
                raise RuntimeError(f"할일 폴더 생성에 실패했습니다.\n시스템 관리자에게 문의하거나 다른 위치를 시도해주세요.\n상세 오류: {e}")
        
        # 할일 목록에 추가
        todos.append(todo)
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
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
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
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
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
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
    
    # 하위 작업 관련 메서드들
    
    def add_subtask(self, todo_id: int, subtask_title: str) -> Optional[SubTask]:
        """
        할일에 하위 작업을 추가합니다.
        
        Requirements 2.1: 하위 작업 추가 기능
        
        Args:
            todo_id: 하위 작업을 추가할 할일의 ID
            subtask_title: 하위 작업 제목
            
        Returns:
            Optional[SubTask]: 생성된 하위 작업 객체 (실패 시 None)
            
        Raises:
            ValueError: 제목이 유효하지 않거나 할일을 찾을 수 없는 경우
        """
        # 제목 유효성 검사
        if not TodoValidator.validate_title(subtask_title):
            raise ValueError("하위 작업 제목이 유효하지 않습니다.")
        
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        target_todo = None
        for todo in todos:
            if todo.id == todo_id:
                target_todo = todo
                break
        
        if target_todo is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 새 하위 작업 ID 생성
        next_subtask_id = self.storage_service.get_next_subtask_id()
        
        # 하위 작업 생성
        subtask = SubTask(
            id=next_subtask_id,
            todo_id=todo_id,
            title=subtask_title.strip(),
            is_completed=False,
            created_at=datetime.now()
        )
        
        # 할일에 하위 작업 추가
        target_todo.add_subtask(subtask)
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            # 저장 실패 시 하위 작업 제거
            target_todo.remove_subtask(subtask.id)
            return None
        
        # 캐시 무효화
        self._todos_cache = None
        
        return subtask
    
    def update_subtask(self, todo_id: int, subtask_id: int, new_title: str) -> bool:
        """
        하위 작업의 제목을 수정합니다.
        
        Requirements 2.2: 하위 작업 수정 기능
        
        Args:
            todo_id: 할일 ID
            subtask_id: 수정할 하위 작업 ID
            new_title: 새로운 제목
            
        Returns:
            bool: 수정 성공 여부
            
        Raises:
            ValueError: 제목이 유효하지 않거나 할일/하위작업을 찾을 수 없는 경우
        """
        # 제목 유효성 검사
        if not TodoValidator.validate_title(new_title):
            raise ValueError("하위 작업 제목이 유효하지 않습니다.")
        
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        target_todo = None
        for todo in todos:
            if todo.id == todo_id:
                target_todo = todo
                break
        
        if target_todo is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 해당 하위 작업 찾기
        target_subtask = None
        for subtask in target_todo.subtasks:
            if subtask.id == subtask_id:
                target_subtask = subtask
                break
        
        if target_subtask is None:
            raise ValueError("해당 하위 작업을 찾을 수 없습니다.")
        
        # 제목 업데이트
        old_title = target_subtask.title
        target_subtask.title = new_title.strip()
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            # 저장 실패 시 원래 제목으로 복원
            target_subtask.title = old_title
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def delete_subtask(self, todo_id: int, subtask_id: int) -> bool:
        """
        하위 작업을 삭제합니다.
        
        Requirements 2.3: 하위 작업 삭제 기능
        
        Args:
            todo_id: 할일 ID
            subtask_id: 삭제할 하위 작업 ID
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            ValueError: 할일이나 하위작업을 찾을 수 없는 경우
        """
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        target_todo = None
        for todo in todos:
            if todo.id == todo_id:
                target_todo = todo
                break
        
        if target_todo is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 하위 작업 삭제
        if not target_todo.remove_subtask(subtask_id):
            raise ValueError("해당 하위 작업을 찾을 수 없습니다.")
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def toggle_subtask_completion(self, todo_id: int, subtask_id: int) -> bool:
        """
        하위 작업의 완료 상태를 토글합니다.
        
        Requirements 2.3: 하위 작업 완료 상태 변경 기능
        
        Args:
            todo_id: 할일 ID
            subtask_id: 토글할 하위 작업 ID
            
        Returns:
            bool: 토글 성공 여부
            
        Raises:
            ValueError: 할일이나 하위작업을 찾을 수 없는 경우
        """
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        target_todo = None
        for todo in todos:
            if todo.id == todo_id:
                target_todo = todo
                break
        
        if target_todo is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 해당 하위 작업 찾기
        target_subtask = None
        for subtask in target_todo.subtasks:
            if subtask.id == subtask_id:
                target_subtask = subtask
                break
        
        if target_subtask is None:
            raise ValueError("해당 하위 작업을 찾을 수 없습니다.")
        
        # 완료 상태 토글
        target_subtask.toggle_completion()
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            # 저장 실패 시 상태 복원
            target_subtask.toggle_completion()
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def get_subtasks(self, todo_id: int) -> List[SubTask]:
        """
        특정 할일의 하위 작업 목록을 조회합니다.
        
        Requirements 4.3: 하위 작업 목록 조회 기능
        
        Args:
            todo_id: 할일 ID
            
        Returns:
            List[SubTask]: 하위 작업 목록 (생성 순서대로 정렬)
            
        Raises:
            ValueError: 할일을 찾을 수 없는 경우
        """
        # 해당 할일 찾기
        target_todo = self.get_todo_by_id(todo_id)
        
        if target_todo is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 하위 작업 목록을 생성 시간 순으로 정렬하여 반환
        subtasks = target_todo.subtasks.copy()
        subtasks.sort(key=lambda x: x.created_at)
        
        return subtasks
    
    # 필터링 및 검색 메서드들
    
    def filter_todos(self, show_completed: bool = True, search_term: str = "") -> List[Todo]:
        """
        할일 목록을 필터링합니다.
        
        Args:
            show_completed: 완료된 할일 표시 여부
            search_term: 검색어 (제목이나 하위작업에서 검색)
            
        Returns:
            List[Todo]: 필터링된 할일 목록
        """
        todos = self.get_all_todos()
        filtered_todos = []
        
        for todo in todos:
            # 완료된 할일 필터링
            if not show_completed and todo.is_completed():
                continue
            
            # 검색어 필터링
            if search_term:
                search_term_lower = search_term.lower()
                
                # 할일 제목에서 검색
                title_match = search_term_lower in todo.title.lower()
                
                # 하위 작업에서 검색
                subtask_match = any(
                    search_term_lower in subtask.title.lower()
                    for subtask in todo.subtasks
                )
                
                if not (title_match or subtask_match):
                    continue
            
            filtered_todos.append(todo)
        
        return filtered_todos
    
    def sort_todos(self, todos: List[Todo], sort_by: str = "created_at") -> List[Todo]:
        """
        할일 목록을 정렬합니다.
        
        Args:
            todos: 정렬할 할일 목록
            sort_by: 정렬 기준 ("created_at", "title", "progress")
            
        Returns:
            List[Todo]: 정렬된 할일 목록
        """
        if sort_by == "title":
            return sorted(todos, key=lambda x: x.title.lower())
        elif sort_by == "progress":
            return sorted(todos, key=lambda x: x.get_completion_rate())
        else:  # "created_at" (기본값)
            return sorted(todos, key=lambda x: x.created_at)
    
    def update_todo_expansion_state(self, todo_id: int, is_expanded: bool) -> bool:
        """
        할일의 트리 확장/축소 상태를 업데이트합니다.
        
        Args:
            todo_id: 할일 ID
            is_expanded: 확장 상태 (True: 확장, False: 축소)
            
        Returns:
            bool: 업데이트 성공 여부
            
        Raises:
            ValueError: 할일을 찾을 수 없는 경우
        """
        # 할일 목록 로드
        todos = self.get_all_todos()
        
        # 해당 할일 찾기
        target_todo = None
        for todo in todos:
            if todo.id == todo_id:
                target_todo = todo
                break
        
        if target_todo is None:
            raise ValueError("해당 할일을 찾을 수 없습니다.")
        
        # 확장 상태 업데이트
        target_todo.is_expanded = is_expanded
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True    
# 자동 저장 및 백업 관련 메서드들
    
    def enable_auto_save(self) -> None:
        """자동 저장 기능을 활성화합니다."""
        self.storage_service.auto_save_enabled = True
        self.storage_service._start_auto_save()
    
    def disable_auto_save(self) -> None:
        """자동 저장 기능을 비활성화합니다."""
        self.storage_service.auto_save_enabled = False
        if self.storage_service._auto_save_timer is not None:
            self.storage_service._auto_save_timer.cancel()
    
    def force_save(self) -> bool:
        """
        현재 데이터를 강제로 저장합니다.
        
        Returns:
            저장 성공 여부
        """
        todos = self.get_all_todos()
        return self.storage_service.save_todos_with_auto_save(todos)
    
    def create_backup(self, backup_name: str = None) -> bool:
        """
        수동 백업을 생성합니다.
        
        Args:
            backup_name: 백업 파일 이름
            
        Returns:
            백업 생성 성공 여부
        """
        return self.storage_service.create_manual_backup(backup_name)
    
    def list_available_backups(self) -> List[str]:
        """
        사용 가능한 백업 목록을 반환합니다.
        
        Returns:
            백업 파일 경로 목록
        """
        return self.storage_service.list_backups()
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        백업에서 데이터를 복구합니다.
        
        Args:
            backup_path: 복구할 백업 파일 경로
            
        Returns:
            복구 성공 여부
        """
        success = self.storage_service.restore_from_backup_file(backup_path)
        if success:
            # 캐시 무효화하여 새로운 데이터 로드
            self.clear_cache()
        return success
    
    def get_data_status(self) -> Dict[str, Any]:
        """
        데이터 상태 정보를 반환합니다.
        
        Returns:
            데이터 상태 정보
        """
        return self.storage_service.get_data_integrity_status()
    
    def repair_data(self) -> bool:
        """
        데이터 무결성 문제를 복구합니다.
        
        Returns:
            복구 성공 여부
        """
        success = self.storage_service.repair_data_integrity()
        if success:
            # 캐시 무효화하여 복구된 데이터 로드
            self.clear_cache()
        return success
    
    def shutdown(self) -> None:
        """서비스 종료 시 정리 작업을 수행합니다."""
        # 마지막 저장 수행
        self.force_save()
        
        # 스토리지 서비스 종료
        self.storage_service.shutdown()
        
        print("TodoService가 정상적으로 종료되었습니다.")