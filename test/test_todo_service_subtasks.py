"""
TodoService 하위 작업 기능 단위 테스트

하위 작업 추가, 수정, 삭제, 완료 상태 토글, 조회 기능을 테스트합니다.
"""

import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestTodoServiceSubtasks(unittest.TestCase):
    """TodoService 하위 작업 기능 테스트 클래스"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # 임시 파일 생성
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # 서비스 인스턴스 생성
        self.storage_service = StorageService(self.temp_file.name)
        self.file_service = Mock(spec=FileService)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트용 할일 생성
        self.test_todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder",
            subtasks=[],
            is_expanded=True
        )
        
        # 초기 데이터 저장
        self.storage_service.save_todos([self.test_todo])
    
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        # 임시 파일 삭제
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_subtask_success(self):
        """하위 작업 추가 성공 테스트"""
        # Given
        subtask_title = "테스트 하위 작업"
        
        # When
        result = self.todo_service.add_subtask(self.test_todo.id, subtask_title)
        
        # Then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, SubTask)
        self.assertEqual(result.title, subtask_title)
        self.assertEqual(result.todo_id, self.test_todo.id)
        self.assertFalse(result.is_completed)
        
        # 할일에 하위 작업이 추가되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
        self.assertEqual(len(updated_todo.subtasks), 1)
        self.assertEqual(updated_todo.subtasks[0].title, subtask_title)
    
    def test_add_subtask_invalid_title(self):
        """잘못된 제목으로 하위 작업 추가 시 오류 테스트"""
        # Given
        invalid_titles = ["", "   ", None]
        
        for invalid_title in invalid_titles:
            with self.subTest(title=invalid_title):
                # When & Then
                with self.assertRaises(ValueError) as context:
                    self.todo_service.add_subtask(self.test_todo.id, invalid_title)
                
                self.assertIn("하위 작업 제목이 유효하지 않습니다", str(context.exception))
    
    def test_add_subtask_nonexistent_todo(self):
        """존재하지 않는 할일에 하위 작업 추가 시 오류 테스트"""
        # Given
        nonexistent_todo_id = 999
        subtask_title = "테스트 하위 작업"
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.add_subtask(nonexistent_todo_id, subtask_title)
        
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_update_subtask_success(self):
        """하위 작업 수정 성공 테스트"""
        # Given
        subtask = self.todo_service.add_subtask(self.test_todo.id, "원래 제목")
        new_title = "수정된 제목"
        
        # When
        result = self.todo_service.update_subtask(self.test_todo.id, subtask.id, new_title)
        
        # Then
        self.assertTrue(result)
        
        # 제목이 수정되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
        updated_subtask = updated_todo.subtasks[0]
        self.assertEqual(updated_subtask.title, new_title)
    
    def test_update_subtask_invalid_title(self):
        """잘못된 제목으로 하위 작업 수정 시 오류 테스트"""
        # Given
        subtask = self.todo_service.add_subtask(self.test_todo.id, "원래 제목")
        invalid_titles = ["", "   ", None]
        
        for invalid_title in invalid_titles:
            with self.subTest(title=invalid_title):
                # When & Then
                with self.assertRaises(ValueError) as context:
                    self.todo_service.update_subtask(self.test_todo.id, subtask.id, invalid_title)
                
                self.assertIn("하위 작업 제목이 유효하지 않습니다", str(context.exception))
    
    def test_update_subtask_nonexistent_todo(self):
        """존재하지 않는 할일의 하위 작업 수정 시 오류 테스트"""
        # Given
        nonexistent_todo_id = 999
        subtask_id = 1
        new_title = "수정된 제목"
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.update_subtask(nonexistent_todo_id, subtask_id, new_title)
        
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_update_subtask_nonexistent_subtask(self):
        """존재하지 않는 하위 작업 수정 시 오류 테스트"""
        # Given
        nonexistent_subtask_id = 999
        new_title = "수정된 제목"
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.update_subtask(self.test_todo.id, nonexistent_subtask_id, new_title)
        
        self.assertIn("해당 하위 작업을 찾을 수 없습니다", str(context.exception))
    
    def test_delete_subtask_success(self):
        """하위 작업 삭제 성공 테스트"""
        # Given
        subtask = self.todo_service.add_subtask(self.test_todo.id, "삭제할 하위 작업")
        
        # When
        result = self.todo_service.delete_subtask(self.test_todo.id, subtask.id)
        
        # Then
        self.assertTrue(result)
        
        # 하위 작업이 삭제되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
        self.assertEqual(len(updated_todo.subtasks), 0)
    
    def test_delete_subtask_nonexistent_todo(self):
        """존재하지 않는 할일의 하위 작업 삭제 시 오류 테스트"""
        # Given
        nonexistent_todo_id = 999
        subtask_id = 1
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.delete_subtask(nonexistent_todo_id, subtask_id)
        
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_delete_subtask_nonexistent_subtask(self):
        """존재하지 않는 하위 작업 삭제 시 오류 테스트"""
        # Given
        nonexistent_subtask_id = 999
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.delete_subtask(self.test_todo.id, nonexistent_subtask_id)
        
        self.assertIn("해당 하위 작업을 찾을 수 없습니다", str(context.exception))
    
    def test_toggle_subtask_completion_success(self):
        """하위 작업 완료 상태 토글 성공 테스트"""
        # Given
        subtask = self.todo_service.add_subtask(self.test_todo.id, "토글할 하위 작업")
        initial_completion = subtask.is_completed
        
        # When
        result = self.todo_service.toggle_subtask_completion(self.test_todo.id, subtask.id)
        
        # Then
        self.assertTrue(result)
        
        # 완료 상태가 토글되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
        updated_subtask = updated_todo.subtasks[0]
        self.assertEqual(updated_subtask.is_completed, not initial_completion)
        
        # 다시 토글해서 원래 상태로 돌아가는지 확인
        result2 = self.todo_service.toggle_subtask_completion(self.test_todo.id, subtask.id)
        self.assertTrue(result2)
        
        updated_todo2 = self.todo_service.get_todo_by_id(self.test_todo.id)
        updated_subtask2 = updated_todo2.subtasks[0]
        self.assertEqual(updated_subtask2.is_completed, initial_completion)
    
    def test_toggle_subtask_completion_nonexistent_todo(self):
        """존재하지 않는 할일의 하위 작업 토글 시 오류 테스트"""
        # Given
        nonexistent_todo_id = 999
        subtask_id = 1
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.toggle_subtask_completion(nonexistent_todo_id, subtask_id)
        
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_toggle_subtask_completion_nonexistent_subtask(self):
        """존재하지 않는 하위 작업 토글 시 오류 테스트"""
        # Given
        nonexistent_subtask_id = 999
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.toggle_subtask_completion(self.test_todo.id, nonexistent_subtask_id)
        
        self.assertIn("해당 하위 작업을 찾을 수 없습니다", str(context.exception))
    
    def test_get_subtasks_success(self):
        """하위 작업 목록 조회 성공 테스트"""
        # Given
        subtask1 = self.todo_service.add_subtask(self.test_todo.id, "첫 번째 하위 작업")
        subtask2 = self.todo_service.add_subtask(self.test_todo.id, "두 번째 하위 작업")
        
        # When
        result = self.todo_service.get_subtasks(self.test_todo.id)
        
        # Then
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], SubTask)
        self.assertIsInstance(result[1], SubTask)
        
        # 생성 순서대로 정렬되어 있는지 확인
        self.assertTrue(result[0].created_at <= result[1].created_at)
    
    def test_get_subtasks_empty_list(self):
        """하위 작업이 없는 할일의 하위 작업 목록 조회 테스트"""
        # When
        result = self.todo_service.get_subtasks(self.test_todo.id)
        
        # Then
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)
    
    def test_get_subtasks_nonexistent_todo(self):
        """존재하지 않는 할일의 하위 작업 목록 조회 시 오류 테스트"""
        # Given
        nonexistent_todo_id = 999
        
        # When & Then
        with self.assertRaises(ValueError) as context:
            self.todo_service.get_subtasks(nonexistent_todo_id)
        
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_filter_todos_with_search_term(self):
        """검색어로 할일 필터링 테스트"""
        # Given
        # 두 번째 할일 추가
        todo2 = Todo(
            id=2,
            title="다른 할일",
            created_at=datetime.now(),
            folder_path="test_folder2",
            subtasks=[],
            is_expanded=True
        )
        
        # 할일 목록 업데이트 (먼저 todo2를 저장)
        todos = [self.test_todo, todo2]
        self.storage_service.save_todos(todos)
        self.todo_service.clear_cache()
        
        # 하위 작업 추가
        self.todo_service.add_subtask(self.test_todo.id, "검색될 하위작업")
        self.todo_service.add_subtask(2, "일반 하위작업")
        
        # When
        result = self.todo_service.filter_todos(search_term="검색될")
        
        # Then
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.test_todo.id)
    
    def test_filter_todos_show_completed_false(self):
        """완료된 할일 숨기기 필터링 테스트"""
        # Given
        # 하위 작업 추가하고 완료 처리
        subtask = self.todo_service.add_subtask(self.test_todo.id, "완료할 하위작업")
        self.todo_service.toggle_subtask_completion(self.test_todo.id, subtask.id)
        
        # 완료되지 않은 할일 추가
        todo2 = Todo(
            id=2,
            title="미완료 할일",
            created_at=datetime.now(),
            folder_path="test_folder2",
            subtasks=[],
            is_expanded=True
        )
        
        todos = self.todo_service.get_all_todos() + [todo2]
        self.storage_service.save_todos(todos)
        self.todo_service.clear_cache()
        
        # When
        result = self.todo_service.filter_todos(show_completed=False)
        
        # Then
        # 완료된 할일(test_todo)은 제외되고 미완료 할일(todo2)만 포함
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 2)
    
    def test_sort_todos_by_title(self):
        """제목으로 할일 정렬 테스트"""
        # Given
        todo_b = Todo(id=2, title="B 할일", created_at=datetime.now(), folder_path="b")
        todo_a = Todo(id=3, title="A 할일", created_at=datetime.now(), folder_path="a")
        todos = [self.test_todo, todo_b, todo_a]  # "테스트 할일", "B 할일", "A 할일"
        
        # When
        result = self.todo_service.sort_todos(todos, sort_by="title")
        
        # Then
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].title, "A 할일")
        self.assertEqual(result[1].title, "B 할일")
        self.assertEqual(result[2].title, "테스트 할일")
    
    def test_sort_todos_by_completion_rate(self):
        """완료율로 할일 정렬 테스트"""
        # Given
        # 첫 번째 할일: 50% 완료 (1/2)
        self.todo_service.add_subtask(self.test_todo.id, "완료된 작업")
        self.todo_service.add_subtask(self.test_todo.id, "미완료 작업")
        subtasks = self.todo_service.get_subtasks(self.test_todo.id)
        self.todo_service.toggle_subtask_completion(self.test_todo.id, subtasks[0].id)
        
        # 두 번째 할일: 100% 완료 (1/1)
        todo2 = Todo(id=2, title="완료된 할일", created_at=datetime.now(), folder_path="b")
        todos = self.todo_service.get_all_todos() + [todo2]
        self.storage_service.save_todos(todos)
        self.todo_service.clear_cache()
        
        subtask2 = self.todo_service.add_subtask(2, "완료된 작업")
        self.todo_service.toggle_subtask_completion(2, subtask2.id)
        
        # 세 번째 할일: 0% 완료 (하위작업 없음)
        todo3 = Todo(id=3, title="미완료 할일", created_at=datetime.now(), folder_path="c")
        todos = self.todo_service.get_all_todos() + [todo3]
        self.storage_service.save_todos(todos)
        self.todo_service.clear_cache()
        
        all_todos = self.todo_service.get_all_todos()
        
        # When
        result = self.todo_service.sort_todos(all_todos, sort_by="completion_rate")
        
        # Then
        self.assertEqual(len(result), 3)
        # 완료율 높은 순으로 정렬 (100%, 50%, 0%)
        self.assertEqual(result[0].id, 2)  # 100% 완료
        self.assertEqual(result[1].id, 1)  # 50% 완료
        self.assertEqual(result[2].id, 3)  # 0% 완료
    
    @patch.object(StorageService, 'save_todos')
    def test_add_subtask_storage_failure(self, mock_save):
        """저장 실패 시 하위 작업 추가 롤백 테스트"""
        # Given
        mock_save.return_value = False
        subtask_title = "저장 실패 테스트"
        
        # When
        result = self.todo_service.add_subtask(self.test_todo.id, subtask_title)
        
        # Then
        self.assertIsNone(result)
        
        # 할일에 하위 작업이 추가되지 않았는지 확인
        updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
        self.assertEqual(len(updated_todo.subtasks), 0)
    
    def test_update_subtask_storage_failure(self):
        """저장 실패 시 하위 작업 수정 롤백 테스트"""
        # Given
        subtask = self.todo_service.add_subtask(self.test_todo.id, "원래 제목")
        original_title = subtask.title
        new_title = "수정된 제목"
        
        # Mock the save_todos method to return False
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            # When
            result = self.todo_service.update_subtask(self.test_todo.id, subtask.id, new_title)
            
            # Then
            self.assertFalse(result)
            
            # 제목이 원래대로 복원되었는지 확인 (메모리에서)
            updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
            updated_subtask = updated_todo.subtasks[0]
            self.assertEqual(updated_subtask.title, original_title)
    
    def test_toggle_subtask_completion_storage_failure(self):
        """저장 실패 시 하위 작업 완료 상태 토글 롤백 테스트"""
        # Given
        subtask = self.todo_service.add_subtask(self.test_todo.id, "토글 테스트")
        original_completion = subtask.is_completed
        
        # Mock the save_todos method to return False
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            # When
            result = self.todo_service.toggle_subtask_completion(self.test_todo.id, subtask.id)
            
            # Then
            self.assertFalse(result)
            
            # 완료 상태가 원래대로 복원되었는지 확인 (메모리에서)
            updated_todo = self.todo_service.get_todo_by_id(self.test_todo.id)
            updated_subtask = updated_todo.subtasks[0]
            self.assertEqual(updated_subtask.is_completed, original_completion)


if __name__ == '__main__':
    unittest.main()