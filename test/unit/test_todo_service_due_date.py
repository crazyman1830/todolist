"""
TodoService의 목표 날짜 관련 기능 테스트

Task 5: TodoService에 목표 날짜 관련 비즈니스 로직 추가 검증
"""

import unittest
from datetime import datetime, timedelta
import tempfile
import os
import shutil
import sys

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from models.todo import Todo
from models.subtask import SubTask


class TestTodoServiceDueDate(unittest.TestCase):
    """TodoService 목표 날짜 관련 기능 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, "test_todos.json")
        self.todo_folders_dir = os.path.join(self.test_dir, "todo_folders")
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.todo_folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트용 할일 생성
        self.todo1 = self.todo_service.add_todo("테스트 할일 1")
        self.todo2 = self.todo_service.add_todo("테스트 할일 2")
        
        # 하위 작업 추가
        self.subtask1 = self.todo_service.add_subtask(self.todo1.id, "하위 작업 1")
        self.subtask2 = self.todo_service.add_subtask(self.todo1.id, "하위 작업 2")
    
    def tearDown(self):
        """테스트 환경 정리"""
        self.todo_service.shutdown()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_set_todo_due_date(self):
        """할일 목표 날짜 설정 테스트"""
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=3)
        result = self.todo_service.set_todo_due_date(self.todo1.id, due_date)
        
        self.assertTrue(result)
        
        # 설정된 목표 날짜 확인
        updated_todo = self.todo_service.get_todo_by_id(self.todo1.id)
        self.assertIsNotNone(updated_todo.due_date)
        self.assertEqual(updated_todo.due_date, due_date)
    
    def test_set_todo_due_date_remove(self):
        """할일 목표 날짜 제거 테스트"""
        # 먼저 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=3)
        self.todo_service.set_todo_due_date(self.todo1.id, due_date)
        
        # 목표 날짜 제거
        result = self.todo_service.set_todo_due_date(self.todo1.id, None)
        
        self.assertTrue(result)
        
        # 목표 날짜가 제거되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(self.todo1.id)
        self.assertIsNone(updated_todo.due_date)
    
    def test_set_todo_due_date_invalid_id(self):
        """존재하지 않는 할일 ID로 목표 날짜 설정 시 오류 테스트"""
        due_date = datetime.now() + timedelta(days=3)
        
        with self.assertRaises(ValueError) as context:
            self.todo_service.set_todo_due_date(999, due_date)
        
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_set_subtask_due_date(self):
        """하위 작업 목표 날짜 설정 테스트"""
        # 상위 할일에 목표 날짜 설정
        parent_due_date = datetime.now() + timedelta(days=5)
        self.todo_service.set_todo_due_date(self.todo1.id, parent_due_date)
        
        # 하위 작업에 목표 날짜 설정 (상위 할일보다 빠른 날짜)
        subtask_due_date = datetime.now() + timedelta(days=3)
        result = self.todo_service.set_subtask_due_date(
            self.todo1.id, self.subtask1.id, subtask_due_date
        )
        
        self.assertTrue(result)
        
        # 설정된 목표 날짜 확인
        updated_todo = self.todo_service.get_todo_by_id(self.todo1.id)
        updated_subtask = None
        for subtask in updated_todo.subtasks:
            if subtask.id == self.subtask1.id:
                updated_subtask = subtask
                break
        
        self.assertIsNotNone(updated_subtask)
        self.assertIsNotNone(updated_subtask.due_date)
        self.assertEqual(updated_subtask.due_date, subtask_due_date)
    
    def test_set_subtask_due_date_validation_error(self):
        """하위 작업 목표 날짜 유효성 검사 오류 테스트"""
        # 상위 할일에 목표 날짜 설정
        parent_due_date = datetime.now() + timedelta(days=3)
        self.todo_service.set_todo_due_date(self.todo1.id, parent_due_date)
        
        # 하위 작업에 상위 할일보다 늦은 목표 날짜 설정 시도
        subtask_due_date = datetime.now() + timedelta(days=5)
        
        with self.assertRaises(ValueError) as context:
            self.todo_service.set_subtask_due_date(
                self.todo1.id, self.subtask1.id, subtask_due_date
            )
        
        self.assertIn("상위 할일의 목표 날짜", str(context.exception))
    
    def test_get_overdue_todos(self):
        """지연된 할일 조회 테스트"""
        # 지연된 할일 생성 (30분 전 - 유효성 검사 통과)
        overdue_date = datetime.now() - timedelta(minutes=30)
        self.todo_service.set_todo_due_date(self.todo1.id, overdue_date)
        
        # 정상 할일 생성
        normal_date = datetime.now() + timedelta(days=3)
        self.todo_service.set_todo_due_date(self.todo2.id, normal_date)
        
        # 지연된 할일 조회
        overdue_todos = self.todo_service.get_overdue_todos()
        
        self.assertEqual(len(overdue_todos), 1)
        self.assertEqual(overdue_todos[0].id, self.todo1.id)
    
    def test_get_urgent_todos(self):
        """긴급한 할일 조회 테스트"""
        # 긴급한 할일 생성 (12시간 후)
        urgent_date = datetime.now() + timedelta(hours=12)
        self.todo_service.set_todo_due_date(self.todo1.id, urgent_date)
        
        # 정상 할일 생성 (3일 후)
        normal_date = datetime.now() + timedelta(days=3)
        self.todo_service.set_todo_due_date(self.todo2.id, normal_date)
        
        # 긴급한 할일 조회 (24시간 기준)
        urgent_todos = self.todo_service.get_urgent_todos(24)
        
        self.assertEqual(len(urgent_todos), 1)
        self.assertEqual(urgent_todos[0].id, self.todo1.id)
    
    def test_get_due_today_todos(self):
        """오늘 마감 할일 조회 테스트"""
        # 오늘 마감 할일 생성
        today_date = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        self.todo_service.set_todo_due_date(self.todo1.id, today_date)
        
        # 내일 마감 할일 생성
        tomorrow_date = datetime.now() + timedelta(days=1)
        self.todo_service.set_todo_due_date(self.todo2.id, tomorrow_date)
        
        # 오늘 마감 할일 조회
        due_today_todos = self.todo_service.get_due_today_todos()
        
        self.assertEqual(len(due_today_todos), 1)
        self.assertEqual(due_today_todos[0].id, self.todo1.id)
    
    def test_sort_todos_by_due_date(self):
        """목표 날짜순 정렬 테스트"""
        # 할일들에 다른 목표 날짜 설정
        date1 = datetime.now() + timedelta(days=5)  # 늦은 날짜
        date2 = datetime.now() + timedelta(days=2)  # 빠른 날짜
        
        self.todo_service.set_todo_due_date(self.todo1.id, date1)
        self.todo_service.set_todo_due_date(self.todo2.id, date2)
        
        # 업데이트된 할일들을 서비스에서 가져오기
        updated_todo1 = self.todo_service.get_todo_by_id(self.todo1.id)
        updated_todo2 = self.todo_service.get_todo_by_id(self.todo2.id)
        todos = [updated_todo1, updated_todo2]
        
        # 오름차순 정렬 (빠른 날짜부터)
        sorted_todos = self.todo_service.sort_todos_by_due_date(todos, ascending=True)
        
        self.assertEqual(sorted_todos[0].id, self.todo2.id)  # 빠른 날짜가 먼저
        self.assertEqual(sorted_todos[1].id, self.todo1.id)  # 늦은 날짜가 나중
        
        # 내림차순 정렬 (늦은 날짜부터)
        sorted_todos = self.todo_service.sort_todos_by_due_date(todos, ascending=False)
        
        self.assertEqual(sorted_todos[0].id, self.todo1.id)  # 늦은 날짜가 먼저
        self.assertEqual(sorted_todos[1].id, self.todo2.id)  # 빠른 날짜가 나중
    
    def test_get_filtered_and_sorted_todos(self):
        """통합 필터링 및 정렬 테스트"""
        # 다양한 목표 날짜 설정
        # 내일과 모레 날짜로 설정하여 테스트
        tomorrow = datetime.now() + timedelta(days=1)
        day_after_tomorrow = datetime.now() + timedelta(days=2)
        
        self.todo_service.set_todo_due_date(self.todo1.id, tomorrow)
        self.todo_service.set_todo_due_date(self.todo2.id, day_after_tomorrow)
        
        # 전체 할일 필터링 (목표 날짜순 정렬)
        all_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="all", sort_by="due_date"
        )
        
        # 목표 날짜가 있는 할일들이 날짜순으로 정렬되어 있는지 확인
        todos_with_due_date = [todo for todo in all_todos if todo.due_date is not None]
        self.assertGreaterEqual(len(todos_with_due_date), 2)
        
        # 첫 번째 할일이 더 빠른 날짜를 가지는지 확인
        if len(todos_with_due_date) >= 2:
            self.assertLessEqual(todos_with_due_date[0].due_date, todos_with_due_date[1].due_date)
    
    def test_validate_subtask_due_date(self):
        """하위 작업 목표 날짜 유효성 검사 테스트"""
        # 상위 할일에 목표 날짜 설정
        parent_due_date = datetime.now() + timedelta(days=5)
        self.todo_service.set_todo_due_date(self.todo1.id, parent_due_date)
        
        # 유효한 날짜 (상위 할일보다 빠름)
        valid_date = datetime.now() + timedelta(days=3)
        is_valid, error_msg = self.todo_service.validate_subtask_due_date(
            self.todo1.id, valid_date
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
        
        # 무효한 날짜 (상위 할일보다 늦음)
        invalid_date = datetime.now() + timedelta(days=7)
        is_valid, error_msg = self.todo_service.validate_subtask_due_date(
            self.todo1.id, invalid_date
        )
        
        self.assertFalse(is_valid)
        self.assertIn("상위 할일의 목표 날짜", error_msg)
    
    def test_get_todos_with_overdue_subtasks(self):
        """지연된 하위 작업이 있는 할일 조회 테스트"""
        # 하위 작업에 지연된 목표 날짜 설정 (30분 전)
        overdue_date = datetime.now() - timedelta(minutes=30)
        self.todo_service.set_subtask_due_date(
            self.todo1.id, self.subtask1.id, overdue_date
        )
        
        # 지연된 하위 작업이 있는 할일 조회
        todos_with_overdue_subtasks = self.todo_service.get_todos_with_overdue_subtasks()
        
        self.assertEqual(len(todos_with_overdue_subtasks), 1)
        self.assertEqual(todos_with_overdue_subtasks[0].id, self.todo1.id)


if __name__ == '__main__':
    unittest.main()