import json
import os
import time
import threading
import hashlib
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from models.todo import Todo
from models.subtask import SubTask


class StorageService:
    """데이터 저장 및 로드를 담당하는 서비스 클래스"""
    
    def __init__(self, file_path: str, auto_save_enabled: bool = True):
        """
        StorageService 초기화
        
        Args:
            file_path: 데이터를 저장할 JSON 파일 경로
            auto_save_enabled: 자동 저장 기능 활성화 여부
        """
        self.file_path = file_path
        self.auto_save_enabled = auto_save_enabled
        self.ensure_data_directory()
        
        # 자동 저장 관련 속성
        self._last_data_hash: Optional[str] = None
        self._auto_save_timer: Optional[threading.Timer] = None
        self._auto_save_interval = 5.0  # 5초마다 자동 저장 체크
        self._pending_save = False
        self._save_lock = threading.Lock()
        self._change_callbacks: List[Callable[[], None]] = []
        
        # 복구 관련 속성
        self._recovery_file = f"{self.file_path}.recovery"
        self._last_save_time = 0
        
        # 프로그램 시작 시 복구 체크
        self._check_recovery_needed()
        
        # 자동 저장 시작
        if self.auto_save_enabled:
            self._start_auto_save()
    
    def ensure_data_directory(self) -> None:
        """데이터 디렉토리가 존재하는지 확인하고 없으면 생성"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def file_exists(self) -> bool:
        """
        데이터 파일이 존재하는지 확인
        
        Returns:
            파일 존재 여부
        """
        return os.path.exists(self.file_path) and os.path.isfile(self.file_path)
    
    def create_empty_file(self) -> bool:
        """
        빈 데이터 파일 생성
        
        Returns:
            파일 생성 성공 여부
        """
        try:
            empty_data = {
                "todos": [],
                "next_id": 1,
                "next_subtask_id": 1
            }
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(empty_data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"빈 파일 생성 중 오류 발생: {e}")
            return False
    
    def save_todos(self, todos: List[Todo]) -> bool:
        """
        할일 목록을 JSON 파일에 저장
        
        Requirements 1.3, 1.4: 새로운 필드들 처리 및 데이터 무결성 보장
        
        Args:
            todos: 저장할 할일 목록
            
        Returns:
            저장 성공 여부
        """
        try:
            # 입력 유효성 검사
            if not isinstance(todos, list):
                raise ValueError("todos는 리스트여야 합니다")
            
            # 목표 날짜 필드 유효성 검사
            validation_result = self.validate_due_date_fields(todos)
            if not validation_result['valid']:
                print("목표 날짜 필드 유효성 검사 실패:")
                for issue in validation_result['issues']:
                    print(f"  - {issue}")
                # 유효성 검사 실패 시에도 복구 시도
                print("데이터 복구를 시도합니다...")
            
            # 데이터 무결성 검사 및 복구
            todos = self._validate_and_repair_data(todos)
            
            # 다음 ID 계산
            next_id = max([todo.id for todo in todos], default=0) + 1
            next_subtask_id = self._calculate_next_subtask_id(todos)
            
            # 현재 설정 로드 (기존 파일에서)
            current_settings = {
                'show_startup_notifications': True,
                'default_due_time': '18:00',
                'date_format': 'relative',
                'auto_backup_enabled': True,
                'backup_retention_days': 30
            }
            
            if self.file_exists():
                try:
                    with open(self.file_path, 'r', encoding='utf-8') as file:
                        existing_data = json.load(file)
                        if 'settings' in existing_data:
                            current_settings.update(existing_data['settings'])
                except Exception:
                    pass  # 기존 설정 로드 실패 시 기본값 사용
            
            # 데이터 구조 생성 (새 필드들 포함)
            data = {
                "todos": [todo.to_dict() for todo in todos],
                "next_id": next_id,
                "next_subtask_id": next_subtask_id,
                "data_version": "2.0",
                "settings": current_settings,
                "last_saved": datetime.now().isoformat()
            }
            
            # 백업 파일 생성 (기존 파일이 있는 경우)
            if self.file_exists():
                self._create_backup()
            
            # 임시 파일에 먼저 저장 (원자적 쓰기)
            temp_file = f"{self.file_path}.tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2, default=str)
                
                # 저장된 데이터 검증
                with open(temp_file, 'r', encoding='utf-8') as file:
                    verification_data = json.load(file)
                    if len(verification_data.get('todos', [])) != len(todos):
                        raise ValueError("저장된 데이터 검증 실패: 할일 개수 불일치")
                
                # 임시 파일을 실제 파일로 이동
                if os.path.exists(self.file_path):
                    os.replace(temp_file, self.file_path)
                else:
                    os.rename(temp_file, self.file_path)
                
            except Exception as e:
                # 임시 파일 정리
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise e
            
            # 저장 후 통계 출력
            stats = validation_result['statistics']
            if stats['todos_with_due_date'] > 0 or stats['subtasks_with_due_date'] > 0:
                print(f"목표 날짜 데이터 저장 완료:")
                print(f"  - 목표 날짜가 있는 할일: {stats['todos_with_due_date']}/{stats['total_todos']}")
                print(f"  - 목표 날짜가 있는 하위작업: {stats['subtasks_with_due_date']}/{stats['total_subtasks']}")
                if stats['overdue_todos'] > 0 or stats['overdue_subtasks'] > 0:
                    print(f"  - 지연된 할일: {stats['overdue_todos']}")
                    print(f"  - 지연된 하위작업: {stats['overdue_subtasks']}")
            
            return True
            
        except (OSError, IOError, PermissionError) as e:
            print(f"데이터 저장 중 파일 시스템 오류 발생: {e}")
            return False
        except (ValueError, TypeError) as e:
            print(f"데이터 저장 중 데이터 오류 발생: {e}")
            return False
        except Exception as e:
            print(f"데이터 저장 중 예상치 못한 오류 발생: {e}")
            return False
    
    def load_todos(self) -> List[Todo]:
        """
        JSON 파일에서 할일 목록을 로드
        
        Returns:
            로드된 할일 목록 (오류 시 빈 목록)
        """
        if not self.file_exists():
            # 파일이 없으면 빈 파일 생성
            if not self.create_empty_file():
                print("경고: 빈 데이터 파일 생성에 실패했습니다. 메모리에서만 작업합니다.")
            return []
        
        try:
            # 파일 크기 확인 (빈 파일이나 너무 큰 파일 처리)
            file_size = os.path.getsize(self.file_path)
            if file_size == 0:
                print("데이터 파일이 비어있습니다. 새로운 파일을 생성합니다.")
                self.create_empty_file()
                return []
            elif file_size > 100 * 1024 * 1024:  # 100MB 제한
                print("경고: 데이터 파일이 너무 큽니다. 백업에서 복구를 시도합니다.")
                return self._restore_from_backup()
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 기존 CLI 데이터 파일 자동 변환
            data = self._migrate_legacy_data(data)
            
            # 데이터 구조 검증
            if not isinstance(data, dict):
                raise ValueError("데이터가 딕셔너리 형태가 아닙니다")
            
            if 'todos' not in data:
                raise ValueError("'todos' 키가 없습니다")
            
            if not isinstance(data['todos'], list):
                raise ValueError("'todos' 값이 리스트가 아닙니다")
            
            todos = []
            invalid_count = 0
            
            for i, todo_data in enumerate(data['todos']):
                try:
                    if not isinstance(todo_data, dict):
                        raise ValueError(f"할일 데이터가 딕셔너리가 아닙니다 (인덱스: {i})")
                    
                    todo = Todo.from_dict(todo_data)
                    todos.append(todo)
                except Exception as e:
                    invalid_count += 1
                    print(f"할일 데이터 파싱 오류 (인덱스 {i}, 건너뜀): {e}")
                    continue
            
            if invalid_count > 0:
                print(f"경고: {invalid_count}개의 잘못된 할일 데이터를 건너뛰었습니다.")
            
            # 데이터 무결성 검사 및 복구
            todos = self._validate_and_repair_data(todos)
            
            return todos
            
        except json.JSONDecodeError as e:
            print(f"JSON 파일이 손상되었습니다 (오류: {e}). 백업에서 복구를 시도합니다.")
            return self._restore_from_backup()
        except (OSError, IOError, PermissionError) as e:
            print(f"데이터 로드 중 파일 시스템 오류 발생: {e}")
            return self._restore_from_backup()
        except (ValueError, TypeError) as e:
            print(f"데이터 로드 중 데이터 구조 오류 발생: {e}")
            return self._restore_from_backup()
        except Exception as e:
            print(f"데이터 로드 중 예상치 못한 오류 발생: {e}")
            return self._restore_from_backup()
    
    def get_next_id(self) -> int:
        """
        다음 할일 ID를 가져옴
        
        Returns:
            다음 사용할 ID
        """
        if not self.file_exists():
            return 1
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data.get('next_id', 1)
        except:
            # 오류 시 현재 할일들의 최대 ID + 1 반환
            todos = self.load_todos()
            return max([todo.id for todo in todos], default=0) + 1
    
    def get_next_subtask_id(self) -> int:
        """
        다음 하위 작업 ID를 가져옴
        
        Returns:
            다음 사용할 하위 작업 ID
        """
        if not self.file_exists():
            return 1
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data.get('next_subtask_id', 1)
        except:
            # 오류 시 현재 하위 작업들의 최대 ID + 1 반환
            todos = self.load_todos()
            return self._calculate_next_subtask_id(todos)   
 
    def _create_backup(self) -> None:
        """현재 데이터 파일의 백업 생성"""
        try:
            backup_path = f"{self.file_path}.backup"
            if os.path.exists(self.file_path):
                # 기존 백업들을 순환시킴 (최대 5개 유지)
                for i in range(4, 0, -1):
                    old_backup = f"{backup_path}.{i}"
                    new_backup = f"{backup_path}.{i+1}"
                    if os.path.exists(old_backup):
                        if os.path.exists(new_backup):
                            os.remove(new_backup)
                        os.rename(old_backup, new_backup)
                
                # 현재 백업을 .1로 이동
                if os.path.exists(backup_path):
                    if os.path.exists(f"{backup_path}.1"):
                        os.remove(f"{backup_path}.1")
                    os.rename(backup_path, f"{backup_path}.1")
                
                # 현재 파일을 백업으로 복사
                import shutil
                shutil.copy2(self.file_path, backup_path)
                
        except Exception as e:
            print(f"백업 생성 중 오류 발생: {e}")
    
    def _restore_from_backup(self) -> List[Todo]:
        """백업 파일에서 데이터 복구 시도"""
        backup_files = [
            f"{self.file_path}.backup",
            f"{self.file_path}.backup.1",
            f"{self.file_path}.backup.2",
            f"{self.file_path}.backup.3",
            f"{self.file_path}.backup.4",
            f"{self.file_path}.backup.5"
        ]
        
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    if isinstance(data, dict) and 'todos' in data:
                        print(f"백업 파일에서 복구 성공: {backup_file}")
                        # 복구된 데이터로 메인 파일 재생성
                        import shutil
                        shutil.copy2(backup_file, self.file_path)
                        
                        todos = []
                        for todo_data in data['todos']:
                            try:
                                todo = Todo.from_dict(todo_data)
                                todos.append(todo)
                            except:
                                continue
                        return todos
                        
                except Exception:
                    continue
        
        # 모든 백업 복구 실패 시 빈 파일 생성
        print("백업 복구 실패. 새로운 빈 파일을 생성합니다.")
        self.create_empty_file()
        return []
    
    def _migrate_legacy_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 데이터 파일을 새로운 형식으로 자동 변환
        
        Requirements 1.3, 1.4: 기존 데이터 호환성 보장 및 자동 마이그레이션
        
        Args:
            data: 로드된 원본 데이터
            
        Returns:
            변환된 데이터
        """
        migrated = False
        migration_log = []
        
        # next_subtask_id 필드가 없으면 추가
        if 'next_subtask_id' not in data:
            data['next_subtask_id'] = 1
            migrated = True
            migration_log.append("next_subtask_id 필드 추가")
        
        # settings 필드가 없으면 기본값으로 추가
        if 'settings' not in data:
            data['settings'] = {
                'show_startup_notifications': True,
                'default_due_time': '18:00',
                'date_format': 'relative',
                'auto_backup_enabled': True,
                'backup_retention_days': 30
            }
            migrated = True
            migration_log.append("settings 필드 추가")
        
        # 각 할일에 필요한 필드들 추가
        if 'todos' in data and isinstance(data['todos'], list):
            for i, todo_data in enumerate(data['todos']):
                if isinstance(todo_data, dict):
                    # subtasks 필드가 없으면 빈 배열 추가
                    if 'subtasks' not in todo_data:
                        todo_data['subtasks'] = []
                        migrated = True
                        migration_log.append(f"할일 {todo_data.get('id', i)}: subtasks 필드 추가")
                    
                    # is_expanded 필드가 없으면 기본값 추가
                    if 'is_expanded' not in todo_data:
                        todo_data['is_expanded'] = True
                        migrated = True
                        migration_log.append(f"할일 {todo_data.get('id', i)}: is_expanded 필드 추가")
                    
                    # due_date 필드가 없으면 null로 추가
                    if 'due_date' not in todo_data:
                        todo_data['due_date'] = None
                        migrated = True
                        migration_log.append(f"할일 {todo_data.get('id', i)}: due_date 필드 추가")
                    
                    # completed_at 필드가 없으면 null로 추가
                    if 'completed_at' not in todo_data:
                        todo_data['completed_at'] = None
                        migrated = True
                        migration_log.append(f"할일 {todo_data.get('id', i)}: completed_at 필드 추가")
                    
                    # 하위 작업들에도 새 필드 추가
                    if 'subtasks' in todo_data and isinstance(todo_data['subtasks'], list):
                        for j, subtask_data in enumerate(todo_data['subtasks']):
                            if isinstance(subtask_data, dict):
                                # due_date 필드가 없으면 null로 추가
                                if 'due_date' not in subtask_data:
                                    subtask_data['due_date'] = None
                                    migrated = True
                                    migration_log.append(f"하위작업 {subtask_data.get('id', j)}: due_date 필드 추가")
                                
                                # completed_at 필드가 없으면 null로 추가
                                if 'completed_at' not in subtask_data:
                                    subtask_data['completed_at'] = None
                                    migrated = True
                                    migration_log.append(f"하위작업 {subtask_data.get('id', j)}: completed_at 필드 추가")
        
        # 데이터 버전 정보 추가
        if 'data_version' not in data:
            data['data_version'] = '2.0'  # 목표 날짜 기능이 추가된 버전
            migrated = True
            migration_log.append("데이터 버전 정보 추가")
        
        # 마이그레이션이 발생했으면 파일에 저장
        if migrated:
            try:
                # 마이그레이션 전 백업 생성
                self._create_migration_backup()
                
                # 마이그레이션된 데이터 저장
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2, default=str)
                
                print("데이터 마이그레이션 완료:")
                for log_entry in migration_log:
                    print(f"  - {log_entry}")
                print("파일이 새로운 형식으로 업데이트되었습니다.")
                
            except Exception as e:
                print(f"마이그레이션된 데이터 저장 중 오류 발생: {e}")
                # 마이그레이션 실패 시 백업에서 복구 시도
                self._restore_migration_backup()
        
        return data
    
    def _validate_and_repair_data(self, todos: List[Todo]) -> List[Todo]:
        """
        데이터 무결성 검사 및 복구
        
        Requirements 1.3, 1.4: 데이터 무결성 검사 및 복구 로직
        
        Args:
            todos: 검사할 할일 목록
            
        Returns:
            복구된 할일 목록
        """
        repaired_todos = []
        repair_count = 0
        repair_log = []
        
        # 할일 ID 중복 제거
        seen_todo_ids = set()
        
        for todo in todos:
            # 할일 ID 중복 검사
            if todo.id in seen_todo_ids:
                # 새로운 ID 할당
                max_id = max(seen_todo_ids) if seen_todo_ids else 0
                old_id = todo.id
                todo.id = max_id + 1
                repair_count += 1
                repair_log.append(f"중복된 할일 ID 수정: {old_id} -> {todo.id}")
            
            seen_todo_ids.add(todo.id)
            
            # 목표 날짜 무결성 검사
            if todo.due_date is not None:
                try:
                    # 목표 날짜가 유효한 datetime 객체인지 확인
                    if not isinstance(todo.due_date, datetime):
                        # 문자열인 경우 datetime으로 변환 시도
                        if isinstance(todo.due_date, str):
                            todo.due_date = datetime.fromisoformat(todo.due_date)
                            repair_count += 1
                            repair_log.append(f"할일 {todo.id}: due_date 형식 수정")
                        else:
                            # 변환할 수 없는 경우 None으로 설정
                            todo.due_date = None
                            repair_count += 1
                            repair_log.append(f"할일 {todo.id}: 잘못된 due_date 제거")
                except Exception:
                    todo.due_date = None
                    repair_count += 1
                    repair_log.append(f"할일 {todo.id}: 손상된 due_date 제거")
            
            # 완료 날짜 무결성 검사
            if todo.completed_at is not None:
                try:
                    if not isinstance(todo.completed_at, datetime):
                        if isinstance(todo.completed_at, str):
                            todo.completed_at = datetime.fromisoformat(todo.completed_at)
                            repair_count += 1
                            repair_log.append(f"할일 {todo.id}: completed_at 형식 수정")
                        else:
                            todo.completed_at = None
                            repair_count += 1
                            repair_log.append(f"할일 {todo.id}: 잘못된 completed_at 제거")
                except Exception:
                    todo.completed_at = None
                    repair_count += 1
                    repair_log.append(f"할일 {todo.id}: 손상된 completed_at 제거")
            
            # 논리적 일관성 검사: 완료된 할일의 경우 completed_at이 있어야 함
            if todo.is_completed() and todo.completed_at is None:
                todo.completed_at = datetime.now()
                repair_count += 1
                repair_log.append(f"할일 {todo.id}: 완료된 할일에 completed_at 추가")
            
            # 하위 작업 무결성 검사
            valid_subtasks = []
            seen_subtask_ids = set()
            
            for subtask in todo.subtasks:
                # 하위 작업의 todo_id가 올바른지 확인
                if subtask.todo_id != todo.id:
                    subtask.todo_id = todo.id
                    repair_count += 1
                    repair_log.append(f"하위 작업 {subtask.id}: todo_id 수정 -> {todo.id}")
                
                # 하위 작업 ID 중복 검사
                if subtask.id in seen_subtask_ids:
                    # 새로운 ID 할당
                    max_subtask_id = max(seen_subtask_ids) if seen_subtask_ids else 0
                    old_id = subtask.id
                    subtask.id = max_subtask_id + 1
                    repair_count += 1
                    repair_log.append(f"중복된 하위 작업 ID 수정: {old_id} -> {subtask.id}")
                
                seen_subtask_ids.add(subtask.id)
                
                # 하위 작업 목표 날짜 무결성 검사
                if subtask.due_date is not None:
                    try:
                        if not isinstance(subtask.due_date, datetime):
                            if isinstance(subtask.due_date, str):
                                subtask.due_date = datetime.fromisoformat(subtask.due_date)
                                repair_count += 1
                                repair_log.append(f"하위작업 {subtask.id}: due_date 형식 수정")
                            else:
                                subtask.due_date = None
                                repair_count += 1
                                repair_log.append(f"하위작업 {subtask.id}: 잘못된 due_date 제거")
                    except Exception:
                        subtask.due_date = None
                        repair_count += 1
                        repair_log.append(f"하위작업 {subtask.id}: 손상된 due_date 제거")
                
                # 하위 작업 완료 날짜 무결성 검사
                if subtask.completed_at is not None:
                    try:
                        if not isinstance(subtask.completed_at, datetime):
                            if isinstance(subtask.completed_at, str):
                                subtask.completed_at = datetime.fromisoformat(subtask.completed_at)
                                repair_count += 1
                                repair_log.append(f"하위작업 {subtask.id}: completed_at 형식 수정")
                            else:
                                subtask.completed_at = None
                                repair_count += 1
                                repair_log.append(f"하위작업 {subtask.id}: 잘못된 completed_at 제거")
                    except Exception:
                        subtask.completed_at = None
                        repair_count += 1
                        repair_log.append(f"하위작업 {subtask.id}: 손상된 completed_at 제거")
                
                # 하위 작업 논리적 일관성 검사
                if subtask.is_completed and subtask.completed_at is None:
                    subtask.completed_at = datetime.now()
                    repair_count += 1
                    repair_log.append(f"하위작업 {subtask.id}: 완료된 작업에 completed_at 추가")
                
                # 목표 날짜 논리적 검사: 하위 작업이 상위 할일보다 늦으면 경고
                if (subtask.due_date is not None and todo.due_date is not None and 
                    subtask.due_date > todo.due_date):
                    repair_log.append(f"경고: 하위작업 {subtask.id}의 목표날짜가 상위 할일보다 늦음")
                
                valid_subtasks.append(subtask)
            
            todo.subtasks = valid_subtasks
            repaired_todos.append(todo)
        
        if repair_count > 0:
            print(f"데이터 무결성 복구 완료: {repair_count}개 항목 수정")
            for log_entry in repair_log:
                print(f"  - {log_entry}")
        
        return repaired_todos
    
    def _calculate_next_subtask_id(self, todos: List[Todo]) -> int:
        """
        모든 하위 작업의 최대 ID + 1을 계산
        
        Args:
            todos: 할일 목록
            
        Returns:
            다음 사용할 하위 작업 ID
        """
        max_subtask_id = 0
        
        for todo in todos:
            for subtask in todo.subtasks:
                if subtask.id > max_subtask_id:
                    max_subtask_id = subtask.id
        
        return max_subtask_id + 1
    
    # 자동 저장 및 백업 시스템 메서드들
    
    def add_change_callback(self, callback: Callable[[], None]) -> None:
        """
        데이터 변경 시 호출될 콜백 함수를 추가합니다.
        
        Args:
            callback: 데이터 변경 시 호출될 함수
        """
        self._change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[], None]) -> None:
        """
        데이터 변경 콜백 함수를 제거합니다.
        
        Args:
            callback: 제거할 콜백 함수
        """
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    def _notify_change(self) -> None:
        """데이터 변경을 모든 콜백에 알립니다."""
        for callback in self._change_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"콜백 실행 중 오류 발생: {e}")
    
    def save_todos_with_auto_save(self, todos: List[Todo]) -> bool:
        """
        자동 저장 기능이 포함된 할일 저장 메서드
        
        Args:
            todos: 저장할 할일 목록
            
        Returns:
            저장 성공 여부
        """
        # 데이터 해시 계산
        current_hash = self._calculate_data_hash(todos)
        
        # 데이터가 변경되지 않았으면 저장하지 않음
        if current_hash == self._last_data_hash:
            return True
        
        # 복구 파일 생성 (저장 시작 전)
        self._create_recovery_file(todos)
        
        # 실제 저장 수행 (재시도 로직 포함)
        success = self._save_with_retry(todos, max_retries=3)
        
        if success:
            self._last_data_hash = current_hash
            self._last_save_time = time.time()
            self._pending_save = False
            
            # 복구 파일 삭제 (저장 성공 시)
            self._cleanup_recovery_file()
            
            # 변경 알림
            self._notify_change()
        
        return success
    
    def _calculate_data_hash(self, todos: List[Todo]) -> str:
        """
        할일 데이터의 해시값을 계산합니다.
        
        Args:
            todos: 할일 목록
            
        Returns:
            데이터의 MD5 해시값
        """
        try:
            # 데이터를 JSON 문자열로 변환
            data = {
                "todos": [todo.to_dict() for todo in todos],
                "next_id": max([todo.id for todo in todos], default=0) + 1,
                "next_subtask_id": self._calculate_next_subtask_id(todos)
            }
            
            json_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(json_str.encode('utf-8')).hexdigest()
        except Exception:
            return ""
    
    def _save_with_retry(self, todos: List[Todo], max_retries: int = 3) -> bool:
        """
        재시도 로직이 포함된 저장 메서드
        
        Args:
            todos: 저장할 할일 목록
            max_retries: 최대 재시도 횟수
            
        Returns:
            저장 성공 여부
        """
        for attempt in range(max_retries + 1):
            try:
                if self.save_todos(todos):
                    if attempt > 0:
                        print(f"데이터 저장 성공 (재시도 {attempt}회 후)")
                    return True
                else:
                    if attempt < max_retries:
                        print(f"데이터 저장 실패, 재시도 중... ({attempt + 1}/{max_retries})")
                        time.sleep(0.5 * (attempt + 1))  # 점진적 지연
                    else:
                        print("데이터 저장 최종 실패")
                        return False
            except Exception as e:
                if attempt < max_retries:
                    print(f"저장 중 오류 발생, 재시도 중... ({attempt + 1}/{max_retries}): {e}")
                    time.sleep(0.5 * (attempt + 1))
                else:
                    print(f"데이터 저장 최종 실패: {e}")
                    return False
        
        return False
    
    def _start_auto_save(self) -> None:
        """자동 저장 타이머를 시작합니다."""
        if self._auto_save_timer is not None:
            self._auto_save_timer.cancel()
        
        self._auto_save_timer = threading.Timer(self._auto_save_interval, self._auto_save_check)
        self._auto_save_timer.daemon = True
        self._auto_save_timer.start()
    
    def _auto_save_check(self) -> None:
        """자동 저장이 필요한지 확인하고 실행합니다."""
        try:
            if self._pending_save:
                # 현재 데이터를 로드하여 저장
                current_todos = self.load_todos()
                if current_todos is not None:
                    self.save_todos_with_auto_save(current_todos)
        except Exception as e:
            print(f"자동 저장 중 오류 발생: {e}")
        finally:
            # 다음 자동 저장 스케줄링
            if self.auto_save_enabled:
                self._start_auto_save()
    
    def mark_data_changed(self) -> None:
        """데이터가 변경되었음을 표시합니다."""
        self._pending_save = True
    
    def _create_recovery_file(self, todos: List[Todo]) -> None:
        """
        복구용 임시 파일을 생성합니다.
        
        Args:
            todos: 저장할 할일 목록
        """
        try:
            recovery_data = {
                "todos": [todo.to_dict() for todo in todos],
                "next_id": max([todo.id for todo in todos], default=0) + 1,
                "next_subtask_id": self._calculate_next_subtask_id(todos),
                "timestamp": time.time(),
                "original_file": self.file_path
            }
            
            with open(self._recovery_file, 'w', encoding='utf-8') as file:
                json.dump(recovery_data, file, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            print(f"복구 파일 생성 중 오류 발생: {e}")
    
    def _cleanup_recovery_file(self) -> None:
        """복구 파일을 삭제합니다."""
        try:
            if os.path.exists(self._recovery_file):
                os.remove(self._recovery_file)
        except Exception as e:
            print(f"복구 파일 삭제 중 오류 발생: {e}")
    
    def _check_recovery_needed(self) -> None:
        """프로그램 시작 시 복구가 필요한지 확인합니다."""
        if not os.path.exists(self._recovery_file):
            return
        
        try:
            with open(self._recovery_file, 'r', encoding='utf-8') as file:
                recovery_data = json.load(file)
            
            # 복구 파일의 타임스탬프 확인
            recovery_time = recovery_data.get('timestamp', 0)
            
            # 메인 파일이 없거나 복구 파일이 더 최신인 경우
            if not self.file_exists() or (self.file_exists() and 
                os.path.getmtime(self.file_path) < recovery_time):
                
                print("비정상 종료가 감지되었습니다. 데이터를 복구합니다...")
                
                # 복구 데이터로 메인 파일 생성
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    main_data = {
                        "todos": recovery_data["todos"],
                        "next_id": recovery_data["next_id"],
                        "next_subtask_id": recovery_data["next_subtask_id"]
                    }
                    json.dump(main_data, file, ensure_ascii=False, indent=2, default=str)
                
                print("데이터 복구가 완료되었습니다.")
            
            # 복구 파일 삭제
            self._cleanup_recovery_file()
            
        except Exception as e:
            print(f"복구 과정 중 오류 발생: {e}")
            # 복구 파일 삭제 시도
            self._cleanup_recovery_file()
    
    def create_manual_backup(self, backup_name: str = None) -> bool:
        """
        수동으로 백업을 생성합니다.
        
        Args:
            backup_name: 백업 파일 이름 (None이면 타임스탬프 사용)
            
        Returns:
            백업 생성 성공 여부
        """
        if not self.file_exists():
            print("백업할 파일이 존재하지 않습니다.")
            return False
        
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"manual_backup_{timestamp}"
            
            backup_path = f"{self.file_path}.{backup_name}"
            
            import shutil
            shutil.copy2(self.file_path, backup_path)
            
            print(f"수동 백업이 생성되었습니다: {backup_path}")
            return True
            
        except Exception as e:
            print(f"수동 백업 생성 중 오류 발생: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """
        사용 가능한 백업 파일 목록을 반환합니다.
        
        Returns:
            백업 파일 경로 목록
        """
        backup_files = []
        directory = os.path.dirname(self.file_path) or "."
        filename = os.path.basename(self.file_path)
        
        try:
            for file in os.listdir(directory):
                if file.startswith(f"{filename}.backup"):
                    backup_files.append(os.path.join(directory, file))
            
            # 수정 시간 순으로 정렬 (최신 순)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
        except Exception as e:
            print(f"백업 파일 목록 조회 중 오류 발생: {e}")
        
        return backup_files
    
    def restore_from_backup_file(self, backup_path: str) -> bool:
        """
        특정 백업 파일에서 데이터를 복구합니다.
        
        Args:
            backup_path: 복구할 백업 파일 경로
            
        Returns:
            복구 성공 여부
        """
        if not os.path.exists(backup_path):
            print(f"백업 파일이 존재하지 않습니다: {backup_path}")
            return False
        
        try:
            # 백업 파일 유효성 검사
            with open(backup_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, dict) or 'todos' not in data:
                print("백업 파일 형식이 올바르지 않습니다.")
                return False
            
            # 현재 파일을 백업으로 저장
            if self.file_exists():
                self._create_backup()
            
            # 백업 파일을 메인 파일로 복사
            import shutil
            shutil.copy2(backup_path, self.file_path)
            
            print(f"백업에서 복구가 완료되었습니다: {backup_path}")
            return True
            
        except Exception as e:
            print(f"백업 복구 중 오류 발생: {e}")
            return False
    
    def get_data_integrity_status(self) -> Dict[str, Any]:
        """
        데이터 무결성 상태를 반환합니다.
        
        Returns:
            무결성 상태 정보
        """
        status = {
            "file_exists": self.file_exists(),
            "file_size": 0,
            "last_modified": None,
            "backup_count": 0,
            "data_valid": False,
            "todo_count": 0,
            "subtask_count": 0,
            "integrity_issues": []
        }
        
        try:
            if self.file_exists():
                status["file_size"] = os.path.getsize(self.file_path)
                status["last_modified"] = datetime.fromtimestamp(
                    os.path.getmtime(self.file_path)
                ).isoformat()
                
                # 데이터 유효성 검사
                todos = self.load_todos()
                if todos is not None:
                    status["data_valid"] = True
                    status["todo_count"] = len(todos)
                    status["subtask_count"] = sum(len(todo.subtasks) for todo in todos)
                    
                    # 무결성 검사
                    issues = self._check_data_integrity_issues(todos)
                    status["integrity_issues"] = issues
            
            # 백업 파일 개수
            status["backup_count"] = len(self.list_backups())
            
        except Exception as e:
            status["integrity_issues"].append(f"상태 확인 중 오류: {e}")
        
        return status
    
    def _check_data_integrity_issues(self, todos: List[Todo]) -> List[str]:
        """
        데이터 무결성 문제를 확인합니다.
        
        Args:
            todos: 검사할 할일 목록
            
        Returns:
            발견된 문제 목록
        """
        issues = []
        
        try:
            # 할일 ID 중복 검사
            todo_ids = [todo.id for todo in todos]
            if len(todo_ids) != len(set(todo_ids)):
                issues.append("중복된 할일 ID가 발견되었습니다")
            
            # 하위 작업 무결성 검사
            for todo in todos:
                subtask_ids = [subtask.id for subtask in todo.subtasks]
                
                # 하위 작업 ID 중복 검사
                if len(subtask_ids) != len(set(subtask_ids)):
                    issues.append(f"할일 {todo.id}에 중복된 하위 작업 ID가 있습니다")
                
                # 하위 작업의 todo_id 검사
                for subtask in todo.subtasks:
                    if subtask.todo_id != todo.id:
                        issues.append(f"하위 작업 {subtask.id}의 todo_id가 올바르지 않습니다")
            
        except Exception as e:
            issues.append(f"무결성 검사 중 오류: {e}")
        
        return issues
    
    def repair_data_integrity(self) -> bool:
        """
        데이터 무결성 문제를 자동으로 복구합니다.
        
        Returns:
            복구 성공 여부
        """
        try:
            todos = self.load_todos()
            if not todos:
                return True
            
            # 기존 복구 로직 사용
            repaired_todos = self._validate_and_repair_data(todos)
            
            # 복구된 데이터 저장
            return self.save_todos(repaired_todos)
            
        except Exception as e:
            print(f"데이터 무결성 복구 중 오류 발생: {e}")
            return False
    
    def _create_migration_backup(self) -> None:
        """
        마이그레이션 전 백업 생성
        
        Requirements 1.4: 백업 및 복원 기능에 새 필드 포함
        """
        try:
            if os.path.exists(self.file_path):
                migration_backup_path = f"{self.file_path}.migration_backup"
                import shutil
                shutil.copy2(self.file_path, migration_backup_path)
                print(f"마이그레이션 백업 생성: {migration_backup_path}")
        except Exception as e:
            print(f"마이그레이션 백업 생성 중 오류 발생: {e}")
    
    def _restore_migration_backup(self) -> None:
        """
        마이그레이션 백업에서 복구
        
        Requirements 1.4: 백업 및 복원 기능
        """
        try:
            migration_backup_path = f"{self.file_path}.migration_backup"
            if os.path.exists(migration_backup_path):
                import shutil
                shutil.copy2(migration_backup_path, self.file_path)
                print("마이그레이션 백업에서 복구 완료")
                # 백업 파일 삭제
                os.remove(migration_backup_path)
        except Exception as e:
            print(f"마이그레이션 백업 복구 중 오류 발생: {e}")
    
    def validate_due_date_fields(self, todos: List[Todo]) -> Dict[str, Any]:
        """
        목표 날짜 필드의 유효성을 검사
        
        Requirements 1.3: 데이터 무결성 검사
        
        Args:
            todos: 검사할 할일 목록
            
        Returns:
            검사 결과 딕셔너리
        """
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'statistics': {
                'total_todos': len(todos),
                'todos_with_due_date': 0,
                'overdue_todos': 0,
                'total_subtasks': 0,
                'subtasks_with_due_date': 0,
                'overdue_subtasks': 0
            }
        }
        
        now = datetime.now()
        
        for todo in todos:
            # 할일 목표 날짜 검사
            if todo.due_date is not None:
                validation_result['statistics']['todos_with_due_date'] += 1
                
                # 목표 날짜 타입 검사
                if not isinstance(todo.due_date, datetime):
                    validation_result['valid'] = False
                    validation_result['issues'].append(
                        f"할일 {todo.id}: due_date가 datetime 타입이 아님"
                    )
                else:
                    # 지연 여부 확인
                    if todo.due_date < now and not todo.is_completed():
                        validation_result['statistics']['overdue_todos'] += 1
            
            # 완료 날짜 검사
            if todo.completed_at is not None:
                if not isinstance(todo.completed_at, datetime):
                    validation_result['valid'] = False
                    validation_result['issues'].append(
                        f"할일 {todo.id}: completed_at이 datetime 타입이 아님"
                    )
                elif todo.due_date is not None and todo.completed_at > todo.due_date:
                    validation_result['warnings'].append(
                        f"할일 {todo.id}: 목표날짜 이후에 완료됨"
                    )
            
            # 하위 작업 검사
            for subtask in todo.subtasks:
                validation_result['statistics']['total_subtasks'] += 1
                
                if subtask.due_date is not None:
                    validation_result['statistics']['subtasks_with_due_date'] += 1
                    
                    # 하위 작업 목표 날짜 타입 검사
                    if not isinstance(subtask.due_date, datetime):
                        validation_result['valid'] = False
                        validation_result['issues'].append(
                            f"하위작업 {subtask.id}: due_date가 datetime 타입이 아님"
                        )
                    else:
                        # 지연 여부 확인
                        if subtask.due_date < now and not subtask.is_completed:
                            validation_result['statistics']['overdue_subtasks'] += 1
                        
                        # 상위 할일과의 일관성 검사
                        if (todo.due_date is not None and 
                            subtask.due_date > todo.due_date):
                            validation_result['warnings'].append(
                                f"하위작업 {subtask.id}: 상위 할일보다 늦은 목표날짜"
                            )
                
                # 하위 작업 완료 날짜 검사
                if subtask.completed_at is not None:
                    if not isinstance(subtask.completed_at, datetime):
                        validation_result['valid'] = False
                        validation_result['issues'].append(
                            f"하위작업 {subtask.id}: completed_at이 datetime 타입이 아님"
                        )
        
        return validation_result
    
    def export_data_with_due_dates(self, export_path: str, todos: List[Todo]) -> bool:
        """
        목표 날짜 필드를 포함한 데이터 내보내기
        
        Requirements 1.4: 백업 및 복원 기능에 새 필드 포함
        
        Args:
            export_path: 내보낼 파일 경로
            todos: 내보낼 할일 목록
            
        Returns:
            내보내기 성공 여부
        """
        try:
            # 내보내기 데이터 구성
            export_data = {
                'export_info': {
                    'version': '2.0',
                    'export_date': datetime.now().isoformat(),
                    'total_todos': len(todos),
                    'total_subtasks': sum(len(todo.subtasks) for todo in todos)
                },
                'todos': [todo.to_dict() for todo in todos],
                'next_id': max([todo.id for todo in todos], default=0) + 1,
                'next_subtask_id': self._calculate_next_subtask_id(todos),
                'settings': {
                    'show_startup_notifications': True,
                    'default_due_time': '18:00',
                    'date_format': 'relative'
                }
            }
            
            # 파일에 저장
            with open(export_path, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, ensure_ascii=False, indent=2, default=str)
            
            print(f"데이터 내보내기 완료: {export_path}")
            return True
            
        except Exception as e:
            print(f"데이터 내보내기 중 오류 발생: {e}")
            return False
    
    def import_data_with_due_dates(self, import_path: str) -> List[Todo]:
        """
        목표 날짜 필드를 포함한 데이터 가져오기
        
        Requirements 1.4: 백업 및 복원 기능에 새 필드 포함
        
        Args:
            import_path: 가져올 파일 경로
            
        Returns:
            가져온 할일 목록
        """
        try:
            if not os.path.exists(import_path):
                print(f"가져올 파일이 존재하지 않습니다: {import_path}")
                return []
            
            with open(import_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 데이터 구조 검증
            if not isinstance(data, dict) or 'todos' not in data:
                print("가져올 파일의 형식이 올바르지 않습니다.")
                return []
            
            # 마이그레이션 적용
            data = self._migrate_legacy_data(data)
            
            # Todo 객체로 변환
            todos = []
            for todo_data in data['todos']:
                try:
                    todo = Todo.from_dict(todo_data)
                    todos.append(todo)
                except Exception as e:
                    print(f"할일 데이터 변환 중 오류 (건너뜀): {e}")
                    continue
            
            # 데이터 무결성 검사 및 복구
            todos = self._validate_and_repair_data(todos)
            
            print(f"데이터 가져오기 완료: {len(todos)}개 할일")
            return todos
            
        except Exception as e:
            print(f"데이터 가져오기 중 오류 발생: {e}")
            return []
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """
        오래된 백업 파일들을 정리
        
        Requirements 1.4: 백업 관리 기능
        
        Args:
            retention_days: 보관할 일수
            
        Returns:
            삭제된 백업 파일 수
        """
        deleted_count = 0
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        try:
            directory = os.path.dirname(self.file_path) or "."
            filename = os.path.basename(self.file_path)
            
            for file in os.listdir(directory):
                if (file.startswith(f"{filename}.backup") or 
                    file.startswith(f"{filename}.manual_backup")):
                    
                    file_path = os.path.join(directory, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"오래된 백업 파일 삭제: {file}")
                        except Exception as e:
                            print(f"백업 파일 삭제 중 오류: {file}, {e}")
            
            if deleted_count > 0:
                print(f"총 {deleted_count}개의 오래된 백업 파일을 삭제했습니다.")
                
        except Exception as e:
            print(f"백업 정리 중 오류 발생: {e}")
        
        return deleted_count
    
    def shutdown(self) -> None:
        """서비스 종료 시 정리 작업을 수행합니다."""
        # 자동 저장 타이머 중지
        if self._auto_save_timer is not None:
            self._auto_save_timer.cancel()
            self._auto_save_timer = None
        
        # 대기 중인 저장 작업 완료
        if self._pending_save:
            try:
                current_todos = self.load_todos()
                if current_todos is not None:
                    self.save_todos_with_auto_save(current_todos)
            except Exception as e:
                print(f"종료 시 저장 중 오류 발생: {e}")
        
        # 복구 파일 정리
        self._cleanup_recovery_file()
        
        # 오래된 백업 정리 (30일 이상)
        try:
            self.cleanup_old_backups(30)
        except Exception as e:
            print(f"백업 정리 중 오류 발생: {e}")
        
        print("StorageService가 정상적으로 종료되었습니다.")