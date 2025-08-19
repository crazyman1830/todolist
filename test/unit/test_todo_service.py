"""
TodoService 단위 테스트

할일 비즈니스 로직 서비스의 모든 기능을 테스트합니다.
"""

import unittest
import tempfile
import shutil
import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestTodoService(unittest.TestCase):
    """TodoService 테스트 클래스"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "test_folders")
        
        # 서비스 인스턴스 생성
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트용 할일 데이터
        self.sample_todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path=os.path.join(self.folders_dir, "todo_1_테스트_할일")
        )
    
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_todo_success(self):
        """할일 추가 성공 테스트"""
        title = "새로운 할일"
        
        # 할일 추가
        todo = self.todo_service.add_todo(title)
        
        # 검증
        self.assertIsInstance(todo, Todo)
        self.assertEqual(todo.title, title)
        self.assertEqual(todo.id, 1)
        self.assertTrue(os.path.exists(todo.folder_path))
        
        # 저장된 데이터 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, title)
    
    def test_add_todo_invalid_title(self):
        """유효하지 않은 제목으로 할일 추가 테스트"""
        invalid_titles = ["", "   ", None]
        
        for title in invalid_titles:
            with self.assertRaises(ValueError):
                self.todo_service.add_todo(title)
    
    def test_add_todo_folder_creation_failure(self):
        """폴더 생성 실패 시 할일 추가 테스트"""
        # FileService의 create_todo_folder 메서드를 모킹하여 예외 발생시킴
        with patch.object(self.file_service, 'create_todo_folder', side_effect=OSError("폴더 생성 실패")):
            with self.assertRaises(RuntimeError):
                self.todo_service.add_todo("테스트 할일")
    
    def test_add_todo_storage_failure(self):
        """저장 실패 시 할일 추가 테스트"""
        # StorageService의 save_todos 메서드를 모킹하여 False 반환
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            with patch.object(self.file_service, 'delete_todo_folder') as mock_delete:
                with self.assertRaises(RuntimeError):
                    self.todo_service.add_todo("테스트 할일")
                # 폴더 삭제가 호출되었는지 확인
                mock_delete.assert_called_once()
    
    def test_get_all_todos_empty(self):
        """빈 할일 목록 조회 테스트"""
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 0)
        self.assertIsInstance(todos, list)
    
    def test_get_all_todos_with_data(self):
        """데이터가 있는 할일 목록 조회 테스트"""
        # 할일 추가
        self.todo_service.add_todo("첫 번째 할일")
        self.todo_service.add_todo("두 번째 할일")
        
        # 조회
        todos = self.todo_service.get_all_todos()
        
        # 검증
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0].title, "첫 번째 할일")
        self.assertEqual(todos[1].title, "두 번째 할일")
        
        # 생성 시간 순으로 정렬되었는지 확인
        self.assertLessEqual(todos[0].created_at, todos[1].created_at)
    
    def test_get_all_todos_caching(self):
        """할일 목록 캐싱 테스트"""
        # 첫 번째 호출
        todos1 = self.todo_service.get_all_todos()
        
        # StorageService의 load_todos를 모킹
        with patch.object(self.storage_service, 'load_todos') as mock_load:
            # 두 번째 호출 (캐시 사용)
            todos2 = self.todo_service.get_all_todos()
            
            # load_todos가 호출되지 않았는지 확인 (캐시 사용)
            mock_load.assert_not_called()
            
            # 결과가 동일한지 확인
            self.assertEqual(len(todos1), len(todos2))
    
    def test_update_todo_success(self):
        """할일 수정 성공 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("원래 제목")
        
        # 수정
        new_title = "수정된 제목"
        result = self.todo_service.update_todo(todo.id, new_title)
        
        # 검증
        self.assertTrue(result)
        
        # 수정된 내용 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertIsNotNone(updated_todo)
        self.assertEqual(updated_todo.title, new_title)
    
    def test_update_todo_invalid_title(self):
        """유효하지 않은 제목으로 할일 수정 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("원래 제목")
        
        # 유효하지 않은 제목으로 수정 시도
        with self.assertRaises(ValueError):
            self.todo_service.update_todo(todo.id, "")
        
        with self.assertRaises(ValueError):
            self.todo_service.update_todo(todo.id, "   ")
    
    def test_update_todo_not_found(self):
        """존재하지 않는 할일 수정 테스트"""
        with self.assertRaises(ValueError):
            self.todo_service.update_todo(999, "새 제목")
    
    def test_update_todo_storage_failure(self):
        """저장 실패 시 할일 수정 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("원래 제목")
        original_title = todo.title
        
        # StorageService의 save_todos 메서드를 모킹하여 False 반환
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            result = self.todo_service.update_todo(todo.id, "새 제목")
            
            # 수정 실패 확인
            self.assertFalse(result)
            
            # 원래 제목이 유지되었는지 확인
            todo_after = self.todo_service.get_todo_by_id(todo.id)
            self.assertEqual(todo_after.title, original_title)
    
    def test_delete_todo_success_without_folder(self):
        """폴더 삭제 없이 할일 삭제 성공 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("삭제할 할일")
        folder_path = todo.folder_path
        
        # 삭제 (폴더는 유지)
        result = self.todo_service.delete_todo(todo.id, delete_folder=False)
        
        # 검증
        self.assertTrue(result)
        
        # 할일이 삭제되었는지 확인
        deleted_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertIsNone(deleted_todo)
        
        # 폴더는 여전히 존재하는지 확인
        self.assertTrue(os.path.exists(folder_path))
    
    def test_delete_todo_success_with_folder(self):
        """폴더와 함께 할일 삭제 성공 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("삭제할 할일")
        folder_path = todo.folder_path
        
        # 삭제 (폴더도 삭제)
        result = self.todo_service.delete_todo(todo.id, delete_folder=True)
        
        # 검증
        self.assertTrue(result)
        
        # 할일이 삭제되었는지 확인
        deleted_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertIsNone(deleted_todo)
        
        # 폴더도 삭제되었는지 확인
        self.assertFalse(os.path.exists(folder_path))
    
    def test_delete_todo_not_found(self):
        """존재하지 않는 할일 삭제 테스트"""
        with self.assertRaises(ValueError):
            self.todo_service.delete_todo(999)
    
    def test_delete_todo_storage_failure(self):
        """저장 실패 시 할일 삭제 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("삭제할 할일")
        
        # StorageService의 save_todos 메서드를 모킹하여 False 반환
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            result = self.todo_service.delete_todo(todo.id)
            
            # 삭제 실패 확인
            self.assertFalse(result)
            
            # 할일이 여전히 존재하는지 확인
            existing_todo = self.todo_service.get_todo_by_id(todo.id)
            self.assertIsNotNone(existing_todo)
    
    def test_delete_todo_folder_deletion_failure(self):
        """폴더 삭제 실패 시 할일 삭제 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("삭제할 할일")
        
        # FileService의 delete_todo_folder 메서드를 모킹하여 False 반환
        with patch.object(self.file_service, 'delete_todo_folder', return_value=False):
            with patch('builtins.print') as mock_print:
                result = self.todo_service.delete_todo(todo.id, delete_folder=True)
                
                # 할일 삭제는 성공
                self.assertTrue(result)
                
                # 경고 메시지가 출력되었는지 확인
                mock_print.assert_called_once()
                self.assertIn("경고", mock_print.call_args[0][0])
    
    def test_get_todo_by_id_found(self):
        """ID로 할일 검색 성공 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("검색할 할일")
        
        # 검색
        found_todo = self.todo_service.get_todo_by_id(todo.id)
        
        # 검증
        self.assertIsNotNone(found_todo)
        self.assertEqual(found_todo.id, todo.id)
        self.assertEqual(found_todo.title, todo.title)
    
    def test_get_todo_by_id_not_found(self):
        """ID로 할일 검색 실패 테스트"""
        found_todo = self.todo_service.get_todo_by_id(999)
        self.assertIsNone(found_todo)
    
    def test_get_max_todo_id_empty(self):
        """빈 목록에서 최대 ID 조회 테스트"""
        max_id = self.todo_service.get_max_todo_id()
        self.assertEqual(max_id, 0)
    
    def test_get_max_todo_id_with_data(self):
        """데이터가 있는 상태에서 최대 ID 조회 테스트"""
        # 여러 할일 추가
        self.todo_service.add_todo("첫 번째")
        self.todo_service.add_todo("두 번째")
        self.todo_service.add_todo("세 번째")
        
        max_id = self.todo_service.get_max_todo_id()
        self.assertEqual(max_id, 3)
    
    def test_clear_cache(self):
        """캐시 무효화 테스트"""
        # 할일 추가하여 캐시 생성
        self.todo_service.add_todo("테스트 할일")
        todos1 = self.todo_service.get_all_todos()
        
        # 캐시 무효화
        self.todo_service.clear_cache()
        
        # StorageService의 load_todos를 모킹
        with patch.object(self.storage_service, 'load_todos', return_value=[]) as mock_load:
            todos2 = self.todo_service.get_all_todos()
            
            # load_todos가 호출되었는지 확인 (캐시가 무효화됨)
            mock_load.assert_called_once()
    
    def test_cache_invalidation_on_add(self):
        """할일 추가 시 캐시 무효화 테스트"""
        # 첫 번째 할일 추가
        self.todo_service.add_todo("첫 번째")
        todos1 = self.todo_service.get_all_todos()
        
        # 두 번째 할일 추가 (캐시 무효화됨)
        self.todo_service.add_todo("두 번째")
        todos2 = self.todo_service.get_all_todos()
        
        # 캐시가 무효화되어 새로운 데이터가 반영되었는지 확인
        self.assertEqual(len(todos1), 1)
        self.assertEqual(len(todos2), 2)
    
    def test_cache_invalidation_on_update(self):
        """할일 수정 시 캐시 무효화 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("원래 제목")
        
        # 첫 번째 조회로 캐시 생성
        todos1 = self.todo_service.get_all_todos()
        original_title = todos1[0].title
        
        # 할일 수정 (캐시 무효화됨)
        self.todo_service.update_todo(todo.id, "수정된 제목")
        
        # 두 번째 조회 (새로운 데이터)
        todos2 = self.todo_service.get_all_todos()
        
        # 캐시가 무효화되어 수정된 데이터가 반영되었는지 확인
        self.assertEqual(original_title, "원래 제목")
        self.assertEqual(todos2[0].title, "수정된 제목")
    
    def test_cache_invalidation_on_delete(self):
        """할일 삭제 시 캐시 무효화 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("삭제할 할일")
        todos1 = self.todo_service.get_all_todos()
        
        # 할일 삭제 (캐시 무효화됨)
        self.todo_service.delete_todo(todo.id)
        todos2 = self.todo_service.get_all_todos()
        
        # 캐시가 무효화되어 삭제된 데이터가 반영되었는지 확인
        self.assertEqual(len(todos1), 1)
        self.assertEqual(len(todos2), 0)


if __name__ == '__main__':
    unittest.main()