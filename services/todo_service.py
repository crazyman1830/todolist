"""
할일 비즈니스 로직 서비스

할일 추가, 조회, 수정, 삭제 등의 핵심 비즈니스 로직을 처리합니다.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from models.todo import Todo
from models.subtask import SubTask
from services.storage_service import StorageService
from services.file_service import FileService
from utils.validators import TodoValidator
from utils.performance_utils import get_performance_optimizer, batch_update


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
        self.performance_optimizer = get_performance_optimizer()
        
        # 배치 업데이트 콜백 등록
        self._register_batch_callbacks()
    
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
    
    # 목표 날짜 관련 비즈니스 로직 메서드들
    
    def set_todo_due_date(self, todo_id: int, due_date: Optional[datetime]) -> bool:
        """
        할일의 목표 날짜 설정
        
        Requirements 4.1: 목표 날짜 기준 할일 관리
        
        Args:
            todo_id: 목표 날짜를 설정할 할일의 ID
            due_date: 설정할 목표 날짜 (None이면 목표 날짜 제거)
            
        Returns:
            bool: 설정 성공 여부
            
        Raises:
            ValueError: 할일을 찾을 수 없거나 날짜가 유효하지 않은 경우
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
        
        # 목표 날짜 유효성 검사 (설정하는 경우에만)
        if due_date is not None:
            from services.date_service import DateService
            is_valid, error_msg = DateService.validate_due_date(due_date)
            if not is_valid:
                raise ValueError(error_msg)
        
        # 목표 날짜 설정
        old_due_date = target_todo.due_date
        target_todo.set_due_date(due_date)
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            # 저장 실패 시 원래 날짜로 복원
            target_todo.set_due_date(old_due_date)
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def set_subtask_due_date(self, todo_id: int, subtask_id: int, 
                            due_date: Optional[datetime]) -> bool:
        """
        하위 작업의 목표 날짜 설정
        
        Requirements 7.1, 7.2: 하위 작업 목표 날짜 설정 및 유효성 검사
        
        Args:
            todo_id: 할일 ID
            subtask_id: 하위 작업 ID
            due_date: 설정할 목표 날짜 (None이면 목표 날짜 제거)
            
        Returns:
            bool: 설정 성공 여부
            
        Raises:
            ValueError: 할일이나 하위작업을 찾을 수 없거나 날짜가 유효하지 않은 경우
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
        
        # 목표 날짜 유효성 검사 (설정하는 경우에만)
        if due_date is not None:
            is_valid, error_msg = self.validate_subtask_due_date(todo_id, due_date)
            if not is_valid:
                raise ValueError(error_msg)
        
        # 목표 날짜 설정
        old_due_date = target_subtask.due_date
        target_subtask.set_due_date(due_date)
        
        # 저장 (자동 저장 기능 사용)
        if not self.storage_service.save_todos_with_auto_save(todos):
            # 저장 실패 시 원래 날짜로 복원
            target_subtask.set_due_date(old_due_date)
            return False
        
        # 캐시 무효화
        self._todos_cache = None
        
        return True
    
    def get_todos_by_due_date(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> List[Todo]:
        """
        목표 날짜 범위로 할일 필터링
        
        Requirements 4.2, 4.3, 4.4: 목표 날짜 기준 필터링
        
        Args:
            start_date: 시작 날짜 (None이면 제한 없음)
            end_date: 종료 날짜 (None이면 제한 없음)
            
        Returns:
            List[Todo]: 필터링된 할일 목록
        """
        todos = self.get_all_todos()
        filtered_todos = []
        
        for todo in todos:
            # 목표 날짜가 없는 할일은 제외
            if todo.due_date is None:
                continue
            
            # 시작 날짜 체크
            if start_date is not None and todo.due_date < start_date:
                continue
            
            # 종료 날짜 체크
            if end_date is not None and todo.due_date > end_date:
                continue
            
            filtered_todos.append(todo)
        
        return filtered_todos
    
    def get_overdue_todos(self) -> List[Todo]:
        """
        지연된 할일들 반환
        
        Requirements 4.3: 지연된 할일 조회
        
        Returns:
            List[Todo]: 목표 날짜가 지난 미완료 할일 목록
        """
        todos = self.get_all_todos()
        overdue_todos = []
        
        now = datetime.now()
        
        for todo in todos:
            # 목표 날짜가 있고, 지났으며, 완료되지 않은 할일
            if (todo.due_date is not None and 
                todo.due_date < now and 
                not todo.is_completed()):
                overdue_todos.append(todo)
        
        return overdue_todos
    
    def get_urgent_todos(self, hours: int = 24) -> List[Todo]:
        """
        긴급한 할일들 반환
        
        Requirements 4.3: 긴급한 할일 조회
        
        Args:
            hours: 긴급 기준 시간 (기본 24시간)
            
        Returns:
            List[Todo]: 지정된 시간 내에 마감인 미완료 할일 목록
        """
        todos = self.get_all_todos()
        urgent_todos = []
        
        now = datetime.now()
        urgent_threshold = now + timedelta(hours=hours)
        
        for todo in todos:
            # 목표 날짜가 있고, 긴급 기준 시간 내이며, 완료되지 않은 할일
            if (todo.due_date is not None and 
                now <= todo.due_date <= urgent_threshold and 
                not todo.is_completed()):
                urgent_todos.append(todo)
        
        return urgent_todos
    
    def get_due_today_todos(self) -> List[Todo]:
        """
        오늘 마감인 할일들 반환
        
        Requirements 4.2: 오늘 마감 할일 조회
        
        Returns:
            List[Todo]: 오늘 마감인 미완료 할일 목록
        """
        from services.date_service import DateService
        
        date_ranges = DateService.get_date_filter_ranges()
        today_start, today_end = date_ranges["오늘"]
        
        return self.get_todos_by_due_date(today_start, today_end)
    
    def get_due_this_week_todos(self) -> List[Todo]:
        """
        이번 주 마감인 할일들 반환
        
        Requirements 4.4: 이번 주 할일 조회
        
        Returns:
            List[Todo]: 이번 주 마감인 할일 목록
        """
        from services.date_service import DateService
        
        date_ranges = DateService.get_date_filter_ranges()
        week_start, week_end = date_ranges["이번 주"]
        
        return self.get_todos_by_due_date(week_start, week_end)
    
    def sort_todos_by_due_date(self, todos: List[Todo], 
                              ascending: bool = True) -> List[Todo]:
        """
        목표 날짜순으로 할일 정렬
        
        Requirements 4.1: 목표 날짜순 정렬
        
        Args:
            todos: 정렬할 할일 목록
            ascending: 오름차순 정렬 여부 (True: 빠른 날짜부터, False: 늦은 날짜부터)
            
        Returns:
            List[Todo]: 목표 날짜순으로 정렬된 할일 목록
        """
        def sort_key(todo: Todo):
            # 목표 날짜가 없는 할일은 맨 뒤로
            if todo.due_date is None:
                return datetime.max if ascending else datetime.min
            return todo.due_date
        
        return sorted(todos, key=sort_key, reverse=not ascending)
    
    def validate_subtask_due_date(self, todo_id: int, 
                                 subtask_due_date: datetime) -> Tuple[bool, str]:
        """
        하위 작업 목표 날짜 유효성 검사
        
        Requirements 7.2: 하위 작업 목표 날짜 유효성 검사
        
        Args:
            todo_id: 할일 ID
            subtask_due_date: 검사할 하위 작업의 목표 날짜
            
        Returns:
            Tuple[bool, str]: (유효성 여부, 오류 메시지)
        """
        # 해당 할일 찾기
        target_todo = self.get_todo_by_id(todo_id)
        
        if target_todo is None:
            return False, "해당 할일을 찾을 수 없습니다."
        
        # DateService를 사용하여 유효성 검사
        from services.date_service import DateService
        return DateService.validate_due_date(subtask_due_date, target_todo.due_date)
    
    def get_todos_with_overdue_subtasks(self) -> List[Todo]:
        """
        지연된 하위 작업이 있는 할일들 반환
        
        Requirements 7.3: 하위 작업 지연 상태 관리
        
        Returns:
            List[Todo]: 지연된 하위 작업이 있는 할일 목록
        """
        todos = self.get_all_todos()
        todos_with_overdue_subtasks = []
        
        for todo in todos:
            if todo.has_overdue_subtasks():
                todos_with_overdue_subtasks.append(todo)
        
        return todos_with_overdue_subtasks
    
    def _register_batch_callbacks(self) -> None:
        """배치 업데이트 콜백 등록"""
        batch_manager = self.performance_optimizer.batch_manager
        
        # 할일 업데이트 배치 콜백
        batch_manager.register_update_callback('todo_update', self._batch_update_todos)
        
        # 하위작업 업데이트 배치 콜백
        batch_manager.register_update_callback('subtask_update', self._batch_update_subtasks)
        
        # 목표 날짜 업데이트 배치 콜백
        batch_manager.register_update_callback('due_date_update', self._batch_update_due_dates)
    
    def _batch_update_todos(self, updates: List[Dict[str, Any]]) -> None:
        """할일 배치 업데이트 처리"""
        try:
            todos = self.get_all_todos()
            updated_todos = set()
            
            for update in updates:
                todo_id = update['item_id']
                data = update['data']
                
                # 해당 할일 찾기
                for todo in todos:
                    if todo.id == todo_id:
                        # 데이터 업데이트
                        if 'title' in data:
                            todo.title = data['title']
                        if 'due_date' in data:
                            todo.set_due_date(data['due_date'])
                        if 'completed_at' in data:
                            todo.completed_at = data['completed_at']
                        
                        updated_todos.add(todo_id)
                        break
            
            # 배치로 저장
            if updated_todos:
                self.storage_service.save_todos_with_auto_save(todos)
                self._todos_cache = None  # 캐시 무효화
                
                print(f"배치 업데이트 완료: {len(updated_todos)}개 할일")
                
        except Exception as e:
            print(f"할일 배치 업데이트 실패: {e}")
    
    def _batch_update_subtasks(self, updates: List[Dict[str, Any]]) -> None:
        """하위작업 배치 업데이트 처리"""
        try:
            todos = self.get_all_todos()
            updated_count = 0
            
            for update in updates:
                subtask_id = update['item_id']
                data = update['data']
                
                # 해당 하위작업 찾기
                for todo in todos:
                    for subtask in todo.subtasks:
                        if subtask.id == subtask_id:
                            # 데이터 업데이트
                            if 'title' in data:
                                subtask.title = data['title']
                            if 'is_completed' in data:
                                subtask.is_completed = data['is_completed']
                                if data['is_completed']:
                                    subtask.completed_at = datetime.now()
                                else:
                                    subtask.completed_at = None
                            if 'due_date' in data:
                                subtask.set_due_date(data['due_date'])
                            
                            updated_count += 1
                            break
            
            # 배치로 저장
            if updated_count > 0:
                self.storage_service.save_todos_with_auto_save(todos)
                self._todos_cache = None  # 캐시 무효화
                
                print(f"배치 업데이트 완료: {updated_count}개 하위작업")
                
        except Exception as e:
            print(f"하위작업 배치 업데이트 실패: {e}")
    
    def _batch_update_due_dates(self, updates: List[Dict[str, Any]]) -> None:
        """목표 날짜 배치 업데이트 처리"""
        try:
            todos = self.get_all_todos()
            updated_count = 0
            
            for update in updates:
                item_id = update['item_id']
                data = update['data']
                item_type = data.get('type', 'todo')
                
                if item_type == 'todo':
                    # 할일 목표 날짜 업데이트
                    for todo in todos:
                        if todo.id == item_id:
                            todo.set_due_date(data.get('due_date'))
                            updated_count += 1
                            break
                elif item_type == 'subtask':
                    # 하위작업 목표 날짜 업데이트
                    for todo in todos:
                        for subtask in todo.subtasks:
                            if subtask.id == item_id:
                                subtask.set_due_date(data.get('due_date'))
                                updated_count += 1
                                break
            
            # 배치로 저장
            if updated_count > 0:
                self.storage_service.save_todos_with_auto_save(todos)
                self._todos_cache = None  # 캐시 무효화
                
                print(f"목표 날짜 배치 업데이트 완료: {updated_count}개 항목")
                
        except Exception as e:
            print(f"목표 날짜 배치 업데이트 실패: {e}")
    
    def queue_todo_update(self, todo_id: int, data: Dict[str, Any]) -> None:
        """할일 업데이트를 배치 큐에 추가"""
        self.performance_optimizer.batch_manager.queue_update('todo_update', todo_id, data)
    
    def queue_subtask_update(self, subtask_id: int, data: Dict[str, Any]) -> None:
        """하위작업 업데이트를 배치 큐에 추가"""
        self.performance_optimizer.batch_manager.queue_update('subtask_update', subtask_id, data)
    
    def queue_due_date_update(self, item_id: int, due_date: Optional[datetime], item_type: str = 'todo') -> None:
        """목표 날짜 업데이트를 배치 큐에 추가"""
        data = {
            'due_date': due_date,
            'type': item_type
        }
        self.performance_optimizer.batch_manager.queue_update('due_date_update', item_id, data)
    
    def get_filtered_and_sorted_todos(self, 
                                     filter_type: str = "all",
                                     sort_by: str = "created_at",
                                     show_completed: bool = True) -> List[Todo]:
        """
        필터링과 정렬을 통합한 할일 조회
        
        Requirements 4.1, 4.2, 4.3, 4.4: 통합 필터링 및 정렬
        
        Args:
            filter_type: 필터 타입 ("all", "due_today", "overdue", "urgent", "this_week")
            sort_by: 정렬 기준 ("created_at", "title", "progress", "due_date")
            show_completed: 완료된 할일 표시 여부
            
        Returns:
            List[Todo]: 필터링 및 정렬된 할일 목록
        """
        # 필터링
        if filter_type == "due_today":
            todos = self.get_due_today_todos()
        elif filter_type == "overdue":
            todos = self.get_overdue_todos()
        elif filter_type == "urgent":
            todos = self.get_urgent_todos()
        elif filter_type == "this_week":
            todos = self.get_due_this_week_todos()
        else:  # "all"
            todos = self.get_all_todos()
        
        # 완료된 할일 필터링
        if not show_completed:
            todos = [todo for todo in todos if not todo.is_completed()]
        
        # 정렬
        if sort_by == "due_date":
            todos = self.sort_todos_by_due_date(todos)
        else:
            todos = self.sort_todos(todos, sort_by)
        
        return todos

    def shutdown(self) -> None:
        """서비스 종료 시 정리 작업을 수행합니다."""
        # 배치 업데이트 강제 플러시
        self.performance_optimizer.batch_manager.force_flush()
        
        # 마지막 저장 수행
        self.force_save()
        
        # 스토리지 서비스 종료
        self.storage_service.shutdown()
        
        # 성능 최적화기 종료
        self.performance_optimizer.shutdown()
        
        print("TodoService가 정상적으로 종료되었습니다.")