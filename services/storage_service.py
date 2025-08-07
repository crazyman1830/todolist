import json
import os
from typing import List, Optional
from datetime import datetime
from models.todo import Todo


class StorageService:
    """데이터 저장 및 로드를 담당하는 서비스 클래스"""
    
    def __init__(self, file_path: str):
        """
        StorageService 초기화
        
        Args:
            file_path: 데이터를 저장할 JSON 파일 경로
        """
        self.file_path = file_path
        self.ensure_data_directory()
    
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
                "next_id": 1
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
        
        Args:
            todos: 저장할 할일 목록
            
        Returns:
            저장 성공 여부
        """
        try:
            # 입력 유효성 검사
            if not isinstance(todos, list):
                raise ValueError("todos는 리스트여야 합니다")
            
            # 다음 ID 계산
            next_id = max([todo.id for todo in todos], default=0) + 1
            
            # 데이터 구조 생성
            data = {
                "todos": [todo.to_dict() for todo in todos],
                "next_id": next_id
            }
            
            # 백업 파일 생성 (기존 파일이 있는 경우)
            if self.file_exists():
                self._create_backup()
            
            # 임시 파일에 먼저 저장 (원자적 쓰기)
            temp_file = f"{self.file_path}.tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2, default=str)
                
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