"""
목표 날짜 필터링 및 정렬 기능 테스트

Requirements 4.1, 4.2, 4.3, 4.4: 목표 날짜 기반 필터링 및 정렬
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestDueDateFiltering(unittest.TestCase):
    """목표 날짜 필터링 및 정렬 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, "test_todos.json")
        
        # 서비스 초기화
        self.file_service = FileService()
        self.storage_service = StorageService(self.data_file)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트 데이터 생성
        self._create_test_data()
    
    def tearDown(self):
        """테스트 정리"""
        import shutil
        # 임시 디렉토리 전체 삭제
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_test_data(self):
        """테스트용 할일 데이터 생성"""
        now = datetime.now()
        
        # 1. 지연된 할일 - 임시로 유효성 검사 우회
        overdue_todo = self.todo_service.add_todo("지연된 할일")
        # 직접 데이터 조작으로 과거 날짜 설정
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            if todo.id == overdue_todo.id:
                todo.due_date = now - timedelta(days=1)
                break
        self.storage_service.save_todos_with_auto_save(todos)
        self.todo_service.clear_cache()
        
        # 2. 오늘 마감 할일
        today_todo = self.todo_service.add_todo("오늘 마감 할일")
        today_due = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if today_due > now:  # 미래 시간인 경우만 설정
            self.todo_service.set_todo_due_date(today_todo.id, today_due)
        else:  # 이미 지난 시간이면 내일로 설정
            today_due = (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
            self.todo_service.set_todo_due_date(today_todo.id, today_due)
        
        # 3. 이번 주 마감 할일 (3일 후)
        this_week_todo = self.todo_service.add_todo("이번 주 마감 할일")
        self.todo_service.set_todo_due_date(this_week_todo.id, now + timedelta(days=3))
        
        # 4. 다음 주 마감 할일 (10일 후)
        next_week_todo = self.todo_service.add_todo("다음 주 마감 할일")
        self.todo_service.set_todo_due_date(next_week_todo.id, now + timedelta(days=10))
        
        # 5. 목표 날짜 없는 할일
        no_due_todo = self.todo_service.add_todo("목표 날짜 없는 할일")
        
        # 6. 완료된 할일 - 직접 데이터 조작으로 과거 날짜 설정
        completed_todo = self.todo_service.add_todo("완료된 할일")
        # 하위 작업 추가하고 완료 처리
        subtask = self.todo_service.add_subtask(completed_todo.id, "완료된 하위작업")
        self.todo_service.toggle_subtask_completion(completed_todo.id, subtask.id)
        
        # 완료된 할일에 과거 날짜 설정
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            if todo.id == completed_todo.id:
                todo.due_date = now - timedelta(days=2)
                break
        self.storage_service.save_todos_with_auto_save(todos)
        self.todo_service.clear_cache()
        
        self.overdue_todo_id = overdue_todo.id
        self.today_todo_id = today_todo.id
        self.this_week_todo_id = this_week_todo.id
        self.next_week_todo_id = next_week_todo.id
        self.no_due_todo_id = no_due_todo.id
        self.completed_todo_id = completed_todo.id
    
    def test_filter_due_today(self):
        """오늘 마감 필터 테스트 - Requirements 4.2"""
        filtered_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="due_today",
            show_completed=True
        )
        
        # 오늘 마감인 할일만 포함되어야 함
        todo_ids = [todo.id for todo in filtered_todos]
        self.assertIn(self.today_todo_id, todo_ids)
        self.assertNotIn(self.overdue_todo_id, todo_ids)
        self.assertNotIn(self.this_week_todo_id, todo_ids)
        self.assertNotIn(self.no_due_todo_id, todo_ids)
    
    def test_filter_overdue(self):
        """지연된 할일 필터 테스트 - Requirements 4.3"""
        filtered_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="overdue",
            show_completed=False  # 완료된 할일 제외
        )
        
        # 지연된 미완료 할일만 포함되어야 함
        todo_ids = [todo.id for todo in filtered_todos]
        self.assertIn(self.overdue_todo_id, todo_ids)
        self.assertNotIn(self.today_todo_id, todo_ids)
        self.assertNotIn(self.completed_todo_id, todo_ids)  # 완료된 할일 제외
        self.assertNotIn(self.no_due_todo_id, todo_ids)
    
    def test_filter_this_week(self):
        """이번 주 필터 테스트 - Requirements 4.4"""
        filtered_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="this_week",
            show_completed=True
        )
        
        # 이번 주 마감인 할일들이 포함되어야 함
        todo_ids = [todo.id for todo in filtered_todos]
        self.assertIn(self.today_todo_id, todo_ids)  # 오늘도 이번 주
        self.assertIn(self.this_week_todo_id, todo_ids)
        self.assertNotIn(self.next_week_todo_id, todo_ids)  # 다음 주는 제외
        self.assertNotIn(self.no_due_todo_id, todo_ids)
    
    def test_sort_by_due_date_ascending(self):
        """목표 날짜순 정렬 테스트 (오름차순) - Requirements 4.1"""
        sorted_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="all",
            sort_by="due_date",
            show_completed=True
        )
        
        # 목표 날짜가 있는 할일들이 날짜순으로 정렬되어야 함
        due_dates = []
        for todo in sorted_todos:
            if todo.due_date is not None:
                due_dates.append(todo.due_date)
        
        # 날짜가 오름차순으로 정렬되었는지 확인
        self.assertEqual(due_dates, sorted(due_dates))
        
        # 목표 날짜가 있는 할일들 중에서 가장 이른 날짜가 첫 번째여야 함
        todos_with_due_date = [todo for todo in sorted_todos if todo.due_date is not None]
        self.assertTrue(len(todos_with_due_date) > 0)
        
        # 완료된 할일이 가장 이른 날짜를 가지므로 첫 번째가 될 수 있음
        earliest_due_date = min(due_dates)
        self.assertEqual(todos_with_due_date[0].due_date, earliest_due_date)
    
    def test_sort_by_due_date_descending(self):
        """목표 날짜순 정렬 테스트 (내림차순)"""
        sorted_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="all",
            sort_by="due_date",
            show_completed=True
        )
        
        # 내림차순으로 뒤집기
        sorted_todos.reverse()
        
        # 목표 날짜가 있는 할일들이 역순으로 정렬되어야 함
        due_dates = []
        for todo in sorted_todos:
            if todo.due_date is not None:
                due_dates.append(todo.due_date)
        
        # 날짜가 내림차순으로 정렬되었는지 확인
        self.assertEqual(due_dates, sorted(due_dates, reverse=True))
    
    def test_combined_filter_and_sort(self):
        """필터링과 정렬 조합 테스트"""
        # 지연된 할일을 목표 날짜순으로 정렬
        filtered_todos = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="overdue",
            sort_by="due_date",
            show_completed=False
        )
        
        # 지연된 미완료 할일만 있어야 함
        self.assertTrue(len(filtered_todos) >= 1)
        for todo in filtered_todos:
            self.assertIsNotNone(todo.due_date)
            self.assertTrue(todo.is_overdue())
            self.assertFalse(todo.is_completed())
    
    def test_show_completed_filter(self):
        """완료된 할일 표시 필터 테스트"""
        # 완료된 할일 포함
        with_completed = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="all",
            show_completed=True
        )
        
        # 완료된 할일 제외
        without_completed = self.todo_service.get_filtered_and_sorted_todos(
            filter_type="all",
            show_completed=False
        )
        
        # 완료된 할일 포함 시 더 많은 할일이 있어야 함
        self.assertGreater(len(with_completed), len(without_completed))
        
        # 완료된 할일 제외 시 완료된 할일이 없어야 함
        for todo in without_completed:
            self.assertFalse(todo.is_completed())
    
    def test_no_due_date_todos_placement(self):
        """목표 날짜 없는 할일의 정렬 위치 테스트"""
        sorted_todos = self.todo_service.sort_todos_by_due_date(
            self.todo_service.get_all_todos()
        )
        
        # 목표 날짜 없는 할일은 맨 뒤에 위치해야 함
        no_due_todos = [todo for todo in sorted_todos if todo.due_date is None]
        due_todos = [todo for todo in sorted_todos if todo.due_date is not None]
        
        # 목표 날짜 있는 할일들이 앞에, 없는 할일들이 뒤에 와야 함
        for i, todo in enumerate(sorted_todos):
            if todo.due_date is None:
                # 이후 모든 할일도 목표 날짜가 없어야 함
                for j in range(i, len(sorted_todos)):
                    self.assertIsNone(sorted_todos[j].due_date)
                break


if __name__ == '__main__':
    unittest.main()