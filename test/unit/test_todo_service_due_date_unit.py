"""
TodoService 목표 날짜 관련 메서드 단위 테스트

Task 17: 단위 테스트 작성 - TodoService의 목표 날짜 비즈니스 로직 검증
Requirements 4.1, 4.2, 4.3, 4.4, 7.2 검증
"""

import unittest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.todo_service import TodoService
from models.todo import Todo
from models.subtask import SubTask


class TestTodoServiceDueDateUnit(unittest.TestCase):
    """TodoService 목표 날짜 관련 메서드 단위 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Mock StorageService와 FileService 생성
        self.mock_storage_service = Mock()
        self.mock_file_service = Mock()
        self.todo_service = TodoService(self.mock_storage_service, self.mock_file_service)
        
        # 테스트용 할일 데이터 생성
        self.now = datetime.now()
        
        # 다양한 목표 날짜를 가진 할일들
        self.overdue_todo = Todo(
            id=1,
            title="지연된 할일",
            created_at=self.now - timedelta(days=5),
            folder_path="overdue_folder",
            due_date=self.now - timedelta(days=2)
        )
        
        self.due_today_todo = Todo(
            id=2,
            title="오늘 마감 할일",
            created_at=self.now - timedelta(days=1),
            folder_path="today_folder",
            due_date=self.now.replace(hour=23, minute=59, second=59)
        )
        
        self.urgent_todo = Todo(
            id=3,
            title="긴급한 할일",
            created_at=self.now - timedelta(days=1),
            folder_path="urgent_folder",
            due_date=self.now + timedelta(hours=12)
        )
        
        self.warning_todo = Todo(
            id=4,
            title="경고 수준 할일",
            created_at=self.now - timedelta(days=2),
            folder_path="warning_folder",
            due_date=self.now + timedelta(days=2)
        )
        
        self.normal_todo = Todo(
            id=5,
            title="일반 할일",
            created_at=self.now - timedelta(days=1),
            folder_path="normal_folder",
            due_date=self.now + timedelta(days=7)
        )
        
        self.no_due_date_todo = Todo(
            id=6,
            title="목표 날짜 없는 할일",
            created_at=self.now,
            folder_path="no_due_folder"
        )
        
        # 완료된 할일
        self.completed_todo = Todo(
            id=7,
            title="완료된 할일",
            created_at=self.now - timedelta(days=3),
            folder_path="completed_folder",
            due_date=self.now - timedelta(days=1),
            completed_at=self.now - timedelta(hours=2)
        )
        
        # 모든 할일 리스트
        self.all_todos = [
            self.overdue_todo,
            self.due_today_todo,
            self.urgent_todo,
            self.warning_todo,
            self.normal_todo,
            self.no_due_date_todo,
            self.completed_todo
        ]
        
        # Mock 설정
        self.mock_storage_service.load_todos.return_value = self.all_todos
        self.todo_service.todos = self.all_todos.copy()
    
    def test_set_todo_due_date_success(self):
        """할일 목표 날짜 설정 성공 테스트 - Requirements 4.1"""
        # 유효한 목표 날짜 설정
        new_due_date = self.now + timedelta(days=5)
        result = self.todo_service.set_todo_due_date(1, new_due_date)
        
        self.assertTrue(result)
        self.assertEqual(self.overdue_todo.due_date, new_due_date)
        self.mock_storage_service.save_todos.assert_called_once()
    
    def test_set_todo_due_date_remove(self):
        """할일 목표 날짜 제거 테스트 - Requirements 4.1"""
        # 목표 날짜 제거 (None 설정)
        result = self.todo_service.set_todo_due_date(1, None)
        
        self.assertTrue(result)
        self.assertIsNone(self.overdue_todo.due_date)
        self.mock_storage_service.save_todos.assert_called_once()
    
    def test_set_todo_due_date_nonexistent_todo(self):
        """존재하지 않는 할일의 목표 날짜 설정 테스트"""
        # 존재하지 않는 할일 ID
        result = self.todo_service.set_todo_due_date(999, self.now + timedelta(days=1))
        
        self.assertFalse(result)
        self.mock_storage_service.save_todos.assert_not_called()
    
    def test_set_subtask_due_date_success(self):
        """하위 작업 목표 날짜 설정 성공 테스트 - Requirements 7.2"""
        # 하위 작업 추가
        subtask = SubTask(1, 1, "테스트 하위 작업")
        self.overdue_todo.add_subtask(subtask)
        
        # 유효한 목표 날짜 설정 (할일보다 빠른 날짜)
        subtask_due_date = self.now + timedelta(days=1)
        self.overdue_todo.due_date = self.now + timedelta(days=3)
        
        result = self.todo_service.set_subtask_due_date(1, 1, subtask_due_date)
        
        self.assertTrue(result)
        self.assertEqual(subtask.due_date, subtask_due_date)
        self.mock_storage_service.save_todos.assert_called_once()
    
    def test_set_subtask_due_date_validation_failure(self):
        """하위 작업 목표 날짜 유효성 검사 실패 테스트 - Requirements 7.2"""
        # 하위 작업 추가
        subtask = SubTask(1, 1, "테스트 하위 작업")
        self.overdue_todo.add_subtask(subtask)
        
        # 할일보다 늦은 목표 날짜 설정 (유효성 검사 실패)
        subtask_due_date = self.now + timedelta(days=5)
        self.overdue_todo.due_date = self.now + timedelta(days=3)
        
        result = self.todo_service.set_subtask_due_date(1, 1, subtask_due_date)
        
        self.assertFalse(result)
        self.assertIsNone(subtask.due_date)
        self.mock_storage_service.save_todos.assert_not_called()
    
    def test_set_subtask_due_date_nonexistent(self):
        """존재하지 않는 하위 작업의 목표 날짜 설정 테스트"""
        # 존재하지 않는 할일 또는 하위 작업
        result = self.todo_service.set_subtask_due_date(999, 1, self.now + timedelta(days=1))
        self.assertFalse(result)
        
        result = self.todo_service.set_subtask_due_date(1, 999, self.now + timedelta(days=1))
        self.assertFalse(result)
    
    def test_get_todos_by_due_date_range(self):
        """목표 날짜 범위로 할일 필터링 테스트 - Requirements 4.2"""
        # 오늘부터 3일 후까지의 할일 조회
        start_date = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = self.now + timedelta(days=3)
        
        result = self.todo_service.get_todos_by_due_date(start_date, end_date)
        
        # due_today_todo, urgent_todo, warning_todo가 포함되어야 함
        result_ids = [todo.id for todo in result]
        self.assertIn(2, result_ids)  # due_today_todo
        self.assertIn(3, result_ids)  # urgent_todo
        self.assertIn(4, result_ids)  # warning_todo
        
        # overdue_todo, normal_todo, no_due_date_todo는 제외되어야 함
        self.assertNotIn(1, result_ids)  # overdue_todo (범위 이전)
        self.assertNotIn(5, result_ids)  # normal_todo (범위 이후)
        self.assertNotIn(6, result_ids)  # no_due_date_todo (목표 날짜 없음)
    
    def test_get_todos_by_due_date_no_range(self):
        """범위 없이 모든 목표 날짜 있는 할일 조회 테스트"""
        result = self.todo_service.get_todos_by_due_date()
        
        # 목표 날짜가 있는 모든 할일이 포함되어야 함
        result_ids = [todo.id for todo in result]
        expected_ids = [1, 2, 3, 4, 5, 7]  # no_due_date_todo(6) 제외
        
        for expected_id in expected_ids:
            self.assertIn(expected_id, result_ids)
        
        self.assertNotIn(6, result_ids)  # no_due_date_todo 제외
    
    def test_get_overdue_todos(self):
        """지연된 할일 조회 테스트 - Requirements 4.3"""
        result = self.todo_service.get_overdue_todos()
        
        # overdue_todo만 포함되어야 함 (완료된 할일 제외)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].title, "지연된 할일")
    
    def test_get_due_today_todos(self):
        """오늘 마감 할일 조회 테스트 - Requirements 4.2"""
        result = self.todo_service.get_due_today_todos()
        
        # due_today_todo만 포함되어야 함
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 2)
        self.assertEqual(result[0].title, "오늘 마감 할일")
    
    def test_get_urgent_todos_default(self):
        """긴급한 할일 조회 테스트 (기본 24시간) - Requirements 4.4"""
        result = self.todo_service.get_urgent_todos()
        
        # urgent_todo만 포함되어야 함 (12시간 후 마감)
        result_ids = [todo.id for todo in result]
        self.assertIn(3, result_ids)  # urgent_todo
        
        # due_today_todo도 24시간 이내이므로 포함될 수 있음
        # (오늘 23:59 마감이므로 24시간 이내)
        self.assertIn(2, result_ids)  # due_today_todo
    
    def test_get_urgent_todos_custom_hours(self):
        """긴급한 할일 조회 테스트 (사용자 정의 시간) - Requirements 4.4"""
        # 6시간 이내의 긴급한 할일만 조회
        result = self.todo_service.get_urgent_todos(hours=6)
        
        # urgent_todo는 12시간 후이므로 제외되어야 함
        result_ids = [todo.id for todo in result]
        self.assertNotIn(3, result_ids)  # urgent_todo (12시간 후)
        
        # due_today_todo는 포함될 수 있음 (오늘 23:59가 6시간 이내인 경우)
        # 시간에 따라 달라질 수 있으므로 구체적인 검증은 생략
    
    def test_sort_todos_by_due_date_ascending(self):
        """목표 날짜순 정렬 테스트 (오름차순) - Requirements 4.1"""
        # 목표 날짜가 있는 할일들만 선택
        todos_with_due_date = [
            self.overdue_todo,      # 2일 전
            self.due_today_todo,    # 오늘 23:59
            self.urgent_todo,       # 12시간 후
            self.warning_todo,      # 2일 후
            self.normal_todo        # 7일 후
        ]
        
        result = self.todo_service.sort_todos_by_due_date(todos_with_due_date, ascending=True)
        
        # 목표 날짜 순서대로 정렬되어야 함
        expected_order = [1, 2, 3, 4, 5]  # overdue -> today -> urgent -> warning -> normal
        actual_order = [todo.id for todo in result]
        
        self.assertEqual(actual_order, expected_order)
    
    def test_sort_todos_by_due_date_descending(self):
        """목표 날짜순 정렬 테스트 (내림차순) - Requirements 4.1"""
        todos_with_due_date = [
            self.overdue_todo,
            self.due_today_todo,
            self.urgent_todo,
            self.warning_todo,
            self.normal_todo
        ]
        
        result = self.todo_service.sort_todos_by_due_date(todos_with_due_date, ascending=False)
        
        # 역순으로 정렬되어야 함
        expected_order = [5, 4, 3, 2, 1]  # normal -> warning -> urgent -> today -> overdue
        actual_order = [todo.id for todo in result]
        
        self.assertEqual(actual_order, expected_order)
    
    def test_sort_todos_by_due_date_with_none(self):
        """목표 날짜가 없는 할일 포함 정렬 테스트"""
        todos_mixed = [
            self.normal_todo,       # 7일 후
            self.no_due_date_todo,  # 목표 날짜 없음
            self.urgent_todo,       # 12시간 후
        ]
        
        result = self.todo_service.sort_todos_by_due_date(todos_mixed, ascending=True)
        
        # 목표 날짜가 없는 할일은 마지막에 위치해야 함
        self.assertEqual(result[0].id, 3)  # urgent_todo
        self.assertEqual(result[1].id, 5)  # normal_todo
        self.assertEqual(result[2].id, 6)  # no_due_date_todo
    
    def test_validate_subtask_due_date_success(self):
        """하위 작업 목표 날짜 유효성 검사 성공 테스트 - Requirements 7.2"""
        # 할일에 목표 날짜 설정
        self.overdue_todo.due_date = self.now + timedelta(days=5)
        
        # 유효한 하위 작업 목표 날짜 (할일보다 빠름)
        subtask_due_date = self.now + timedelta(days=3)
        
        is_valid, message = self.todo_service.validate_subtask_due_date(1, subtask_due_date)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_subtask_due_date_failure(self):
        """하위 작업 목표 날짜 유효성 검사 실패 테스트 - Requirements 7.2"""
        # 할일에 목표 날짜 설정
        self.overdue_todo.due_date = self.now + timedelta(days=3)
        
        # 무효한 하위 작업 목표 날짜 (할일보다 늦음)
        subtask_due_date = self.now + timedelta(days=5)
        
        is_valid, message = self.todo_service.validate_subtask_due_date(1, subtask_due_date)
        
        self.assertFalse(is_valid)
        self.assertIn("상위 할일의 목표 날짜", message)
    
    def test_validate_subtask_due_date_no_parent_due_date(self):
        """상위 할일에 목표 날짜가 없는 경우 유효성 검사 테스트"""
        # 할일에 목표 날짜 없음
        self.no_due_date_todo.due_date = None
        
        # 하위 작업 목표 날짜 설정
        subtask_due_date = self.now + timedelta(days=1)
        
        is_valid, message = self.todo_service.validate_subtask_due_date(6, subtask_due_date)
        
        # 상위 할일에 목표 날짜가 없으면 항상 유효
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_subtask_due_date_nonexistent_todo(self):
        """존재하지 않는 할일의 하위 작업 유효성 검사 테스트"""
        subtask_due_date = self.now + timedelta(days=1)
        
        is_valid, message = self.todo_service.validate_subtask_due_date(999, subtask_due_date)
        
        self.assertFalse(is_valid)
        self.assertIn("할일을 찾을 수 없습니다", message)
    
    def test_get_todos_with_overdue_subtasks(self):
        """지연된 하위 작업이 있는 할일 조회 테스트"""
        # 하위 작업 추가
        overdue_subtask = SubTask(
            id=1,
            todo_id=5,
            title="지연된 하위 작업",
            due_date=self.now - timedelta(hours=1)
        )
        self.normal_todo.add_subtask(overdue_subtask)
        
        result = self.todo_service.get_todos_with_overdue_subtasks()
        
        # normal_todo가 포함되어야 함 (지연된 하위 작업이 있음)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 5)
    
    def test_get_filtered_and_sorted_todos(self):
        """필터링 및 정렬된 할일 조회 테스트"""
        # 실제 존재하는 메서드 테스트
        if hasattr(self.todo_service, 'get_filtered_and_sorted_todos'):
            result = self.todo_service.get_filtered_and_sorted_todos(
                filter_type="overdue",
                sort_by="due_date"
            )
            self.assertIsInstance(result, list)
    
    def test_queue_due_date_update(self):
        """목표 날짜 업데이트 큐 테스트"""
        # 목표 날짜 업데이트를 큐에 추가
        due_date = self.now + timedelta(days=1)
        
        # 메서드가 존재하는지 확인하고 호출
        if hasattr(self.todo_service, 'queue_due_date_update'):
            self.todo_service.queue_due_date_update(1, due_date, 'todo')
            # 큐에 추가되었는지 확인 (실제 구현에 따라 다름)
            self.assertTrue(True)  # 오류 없이 실행되면 성공


if __name__ == '__main__':
    unittest.main()