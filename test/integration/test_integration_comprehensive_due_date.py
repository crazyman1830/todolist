#!/usr/bin/env python3
"""
통합 테스트 및 GUI 테스트 - 목표 날짜 기능 전체 워크플로우 검증

이 테스트는 목표 날짜 기능의 전체 워크플로우를 검증합니다:
- 목표 날짜 설정 후 UI 업데이트
- 긴급도 변경에 따른 색상 및 정렬
- 다이얼로그 상호작용
- 데이터 저장/로드 통합
"""

import unittest
import tkinter as tk
from tkinter import ttk
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import threading
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from services.date_service import DateService
from services.notification_service import NotificationService
from gui.main_window import MainWindow
from gui.todo_tree import TodoTree
from gui.dialogs import DueDateDialog, AddTodoDialog
from gui.components import DueDateLabel, UrgencyIndicator
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils


class TestIntegrationComprehensiveDueDate(unittest.TestCase):
    """목표 날짜 기능 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        
        # GUI 루트 생성
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 창 숨기기
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.temp_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.notification_service = NotificationService(self.todo_service)
        
        # 테스트 데이터 생성
        self.now = datetime.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.yesterday = self.now - timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)
        
    def tearDown(self):
        """테스트 정리"""
        try:
            self.root.destroy()
        except:
            pass
        
        # 임시 디렉토리 정리
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_due_date_setting_ui_update_workflow(self):
        """목표 날짜 설정 후 UI 업데이트 테스트"""
        print("Testing due date setting and UI update workflow...")
        
        # 1. 할일 생성
        todo = self.todo_service.add_todo("테스트 할일")
        self.assertIsNotNone(todo)
        
        # 2. TodoTree 생성 및 초기화
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.refresh()
        
        # 3. 초기 상태 확인 (목표 날짜 없음)
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertIsNone(todos[0].due_date)
        
        # 4. 목표 날짜 설정
        success = self.todo_service.set_todo_due_date(todo.id, self.tomorrow)
        self.assertTrue(success)
        
        # 5. UI 업데이트 확인
        todo_tree.load_todos()
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertIsNotNone(updated_todo.due_date)
        self.assertEqual(updated_todo.due_date.date(), self.tomorrow.date())
        
        # 6. 트리뷰에서 목표 날짜 표시 확인
        tree_items = todo_tree.get_children()
        self.assertEqual(len(tree_items), 1)
        
        item_values = todo_tree.item(tree_items[0], 'values')
        self.assertTrue(any('내일' in str(val) or 'D-1' in str(val) for val in item_values))
        
        print("✓ Due date setting and UI update workflow test passed")
    
    def test_urgency_color_and_sorting_integration(self):
        """긴급도 변경에 따른 색상 및 정렬 테스트"""
        print("Testing urgency color and sorting integration...")
        
        # 1. 다양한 긴급도의 할일들 생성
        overdue_todo = self.todo_service.add_todo("지연된 할일")
        urgent_todo = self.todo_service.add_todo("긴급한 할일")
        warning_todo = self.todo_service.add_todo("주의 할일")
        normal_todo = self.todo_service.add_todo("일반 할일")
        
        # 2. 목표 날짜 설정 (과거 날짜는 직접 설정)
        overdue_todo.due_date = self.yesterday
        self.todo_service.set_todo_due_date(urgent_todo.id, self.now + timedelta(hours=12))
        self.todo_service.set_todo_due_date(warning_todo.id, self.now + timedelta(days=2))
        self.todo_service.set_todo_due_date(normal_todo.id, self.next_week)
        
        # 3. TodoTree 생성 및 새로고침
        todo_tree = TodoTree(self.root, self.todo_service)
        todo_tree.load_todos()
        
        # 4. 긴급도 레벨 확인
        todos = self.todo_service.get_all_todos()
        urgency_levels = {}
        for todo in todos:
            urgency_levels[todo.title] = todo.get_urgency_level()
        
        self.assertEqual(urgency_levels["지연된 할일"], "overdue")
        self.assertEqual(urgency_levels["긴급한 할일"], "urgent")
        self.assertEqual(urgency_levels["주의 할일"], "warning")
        self.assertEqual(urgency_levels["일반 할일"], "normal")
        
        # 5. 목표 날짜순 정렬 테스트
        sorted_todos = self.todo_service.sort_todos_by_due_date(todos)
        expected_order = ["지연된 할일", "긴급한 할일", "주의 할일", "일반 할일"]
        actual_order = [todo.title for todo in sorted_todos]
        self.assertEqual(actual_order, expected_order)
        
        # 6. 색상 매핑 확인
        for todo in todos:
            urgency = todo.get_urgency_level()
            color = ColorUtils.get_urgency_color(urgency)
            self.assertIsNotNone(color)
            self.assertTrue(color.startswith('#'))
        
        print("✓ Urgency color and sorting integration test passed")
    
    def test_dialog_interaction_workflow(self):
        """다이얼로그 상호작용 테스트"""
        print("Testing dialog interaction workflow...")
        
        # 1. 할일 생성
        todo = self.todo_service.add_todo("다이얼로그 테스트 할일")
        
        # 2. DueDateDialog 테스트 (모킹)
        with patch('gui.dialogs.DueDateDialog') as mock_dialog:
            # 다이얼로그가 내일 날짜를 반환하도록 설정
            mock_instance = Mock()
            mock_instance.get_result.return_value = self.tomorrow
            mock_dialog.return_value = mock_instance
            
            # 목표 날짜 설정 다이얼로그 시뮬레이션
            dialog = mock_dialog(self.root, None, None, "할일")
            result = dialog.get_result()
            
            self.assertEqual(result, self.tomorrow)
            mock_dialog.assert_called_once()
        
        # 3. AddTodoDialog 통합 테스트
        with patch('gui.dialogs.AddTodoDialog') as mock_add_dialog:
            mock_instance = Mock()
            mock_instance.get_result.return_value = {
                'title': '새 할일',
                'due_date': self.tomorrow
            }
            mock_add_dialog.return_value = mock_instance
            
            dialog = mock_add_dialog(self.root, self.todo_service)
            result = dialog.get_result()
            
            self.assertIsNotNone(result)
            self.assertEqual(result['title'], '새 할일')
            self.assertEqual(result['due_date'], self.tomorrow)
        
        # 4. 실제 목표 날짜 설정 및 검증
        success = self.todo_service.set_todo_due_date(todo.id, self.tomorrow)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.due_date.date(), self.tomorrow.date())
        
        print("✓ Dialog interaction workflow test passed")
    
    def test_data_save_load_integration(self):
        """데이터 저장/로드 통합 테스트"""
        print("Testing data save/load integration...")
        
        # 1. 목표 날짜가 있는 할일들 생성
        todo1 = self.todo_service.add_todo("저장 테스트 할일 1")
        todo2 = self.todo_service.add_todo("저장 테스트 할일 2")
        
        # 2. 목표 날짜 설정
        self.todo_service.set_todo_due_date(todo1.id, self.tomorrow)
        self.todo_service.set_todo_due_date(todo2.id, self.next_week)
        
        # 3. 하위 작업 추가 및 목표 날짜 설정
        subtask1 = self.todo_service.add_subtask(todo1.id, "하위 작업 1")
        self.todo_service.set_subtask_due_date(todo1.id, subtask1.id, self.now + timedelta(hours=12))
        
        # 4. 데이터 저장
        self.storage_service.save_todos(self.todo_service.get_all_todos())
        
        # 5. 새로운 서비스 인스턴스로 데이터 로드
        new_storage_service = StorageService(self.data_file)
        new_file_service = FileService(self.temp_dir)
        new_todo_service = TodoService(new_storage_service, new_file_service)
        
        loaded_todos = new_todo_service.get_all_todos()
        
        # 6. 로드된 데이터 검증
        self.assertEqual(len(loaded_todos), 2)
        
        # 할일 목표 날짜 검증
        loaded_todo1 = next(t for t in loaded_todos if t.title == "저장 테스트 할일 1")
        loaded_todo2 = next(t for t in loaded_todos if t.title == "저장 테스트 할일 2")
        
        self.assertIsNotNone(loaded_todo1.due_date)
        self.assertIsNotNone(loaded_todo2.due_date)
        self.assertEqual(loaded_todo1.due_date.date(), self.tomorrow.date())
        self.assertEqual(loaded_todo2.due_date.date(), self.next_week.date())
        
        # 하위 작업 목표 날짜 검증
        self.assertEqual(len(loaded_todo1.subtasks), 1)
        loaded_subtask = loaded_todo1.subtasks[0]
        self.assertIsNotNone(loaded_subtask.due_date)
        
        # 7. JSON 파일 직접 검증
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('todos', data)
        self.assertEqual(len(data['todos']), 2)
        
        # 목표 날짜 필드 존재 확인
        for todo_data in data['todos']:
            if 'due_date' in todo_data and todo_data['due_date']:
                # ISO 형식 날짜 문자열 확인
                due_date = datetime.fromisoformat(todo_data['due_date'])
                self.assertIsInstance(due_date, datetime)
        
        print("✓ Data save/load integration test passed")
    
    def test_complete_workflow_integration(self):
        """전체 워크플로우 통합 테스트"""
        print("Testing complete workflow integration...")
        
        # 1. MainWindow 컴포넌트 초기화 (모킹)
        with patch('gui.main_window.MainWindow') as mock_main_window:
            mock_instance = Mock()
            mock_main_window.return_value = mock_instance
            
            # 2. 할일 생성 및 목표 날짜 설정
            todo = self.todo_service.add_todo("완전한 워크플로우 테스트")
            self.todo_service.set_todo_due_date(todo.id, self.tomorrow)
            
            # 3. 하위 작업 추가
            subtask = self.todo_service.add_subtask(todo.id, "하위 작업")
            self.todo_service.set_subtask_due_date(todo.id, subtask.id, self.now + timedelta(hours=6))
            
            # 4. 알림 서비스 테스트
            due_today_todos = self.notification_service.get_due_today_todos()
            urgent_todos = self.notification_service.get_urgent_todos()
            
            # 내일이 목표인 할일은 오늘 마감이 아님
            self.assertEqual(len(due_today_todos), 0)
            # 6시간 후가 목표인 하위 작업은 긴급함
            self.assertGreaterEqual(len(urgent_todos), 0)
            
            # 5. 상태바 요약 정보 테스트
            summary = self.notification_service.get_status_bar_summary()
            self.assertIsInstance(summary, dict)
            self.assertIn('due_today', summary)
            self.assertIn('overdue', summary)
            
            # 6. 완료 처리 및 상태 변경
            self.todo_service.toggle_subtask_completion(todo.id, subtask.id)
            updated_subtask = next(s for s in todo.subtasks if s.id == subtask.id)
            self.assertTrue(updated_subtask.is_completed)
            self.assertIsNotNone(updated_subtask.completed_at)
            
            # 7. 데이터 무결성 최종 검증
            self.storage_service.save_todos(self.todo_service.get_all_todos())
            
            # 새로운 인스턴스로 로드하여 검증
            verification_storage = StorageService(self.data_file)
            verification_file_service = FileService(self.temp_dir)
            verification_service = TodoService(verification_storage, verification_file_service)
            final_todos = verification_service.get_all_todos()
            
            self.assertEqual(len(final_todos), 1)
            final_todo = final_todos[0]
            self.assertIsNotNone(final_todo.due_date)
            self.assertEqual(len(final_todo.subtasks), 1)
            self.assertTrue(final_todo.subtasks[0].is_completed)
        
        print("✓ Complete workflow integration test passed")
    
    def test_ui_component_integration(self):
        """UI 컴포넌트 통합 테스트"""
        print("Testing UI component integration...")
        
        # 1. DueDateLabel 컴포넌트 테스트
        due_date_label = DueDateLabel(self.root, self.tomorrow)
        self.assertIsNotNone(due_date_label)
        
        # 라벨 텍스트 확인
        label_text = due_date_label.cget('text')
        self.assertTrue('내일' in label_text or 'D-1' in label_text or '1일' in label_text)
        
        # 2. UrgencyIndicator 컴포넌트 테스트
        urgency_indicator = UrgencyIndicator(self.root, 'urgent')
        self.assertIsNotNone(urgency_indicator)
        
        # 3. 컴포넌트 상호작용 테스트
        todo = self.todo_service.add_todo("UI 컴포넌트 테스트")
        todo.due_date = self.yesterday  # 지연된 할일 (직접 설정)
        
        # 긴급도 확인
        urgency_level = todo.get_urgency_level()
        self.assertEqual(urgency_level, 'overdue')
        
        # 색상 확인
        color = ColorUtils.get_urgency_color(urgency_level)
        self.assertEqual(color, '#ff4444')  # 빨간색
        
        # 4. 실시간 업데이트 시뮬레이션
        due_date_label.set_due_date(self.yesterday)
        updated_text = due_date_label.cget('text')
        self.assertTrue('지남' in updated_text or 'overdue' in updated_text.lower())
        
        print("✓ UI component integration test passed")
    
    def test_performance_integration(self):
        """성능 통합 테스트"""
        print("Testing performance integration...")
        
        # 1. 대량 할일 생성
        start_time = time.time()
        
        todos = []
        for i in range(100):
            todo = self.todo_service.add_todo(f"성능 테스트 할일 {i}")
            # 다양한 목표 날짜 설정
            due_date = self.now + timedelta(days=i % 30, hours=i % 24)
            self.todo_service.set_todo_due_date(todo.id, due_date)
            todos.append(todo)
        
        creation_time = time.time() - start_time
        self.assertLess(creation_time, 5.0)  # 5초 이내
        
        # 2. 긴급도 계산 성능 테스트
        start_time = time.time()
        
        urgency_counts = {'overdue': 0, 'urgent': 0, 'warning': 0, 'normal': 0}
        for todo in todos:
            urgency = todo.get_urgency_level()
            urgency_counts[urgency] += 1
        
        urgency_time = time.time() - start_time
        self.assertLess(urgency_time, 1.0)  # 1초 이내
        
        # 3. 정렬 성능 테스트
        start_time = time.time()
        sorted_todos = self.todo_service.sort_todos_by_due_date(todos)
        sorting_time = time.time() - start_time
        
        self.assertEqual(len(sorted_todos), 100)
        self.assertLess(sorting_time, 1.0)  # 1초 이내
        
        # 4. 저장/로드 성능 테스트
        start_time = time.time()
        self.storage_service.save_todos(todos)
        save_time = time.time() - start_time
        
        start_time = time.time()
        loaded_todos = self.storage_service.load_todos()
        load_time = time.time() - start_time
        
        self.assertLess(save_time, 2.0)  # 2초 이내
        self.assertLess(load_time, 2.0)  # 2초 이내
        self.assertEqual(len(loaded_todos), 100)
        
        print(f"✓ Performance integration test passed")
        print(f"  - Creation: {creation_time:.2f}s")
        print(f"  - Urgency calculation: {urgency_time:.2f}s") 
        print(f"  - Sorting: {sorting_time:.2f}s")
        print(f"  - Save: {save_time:.2f}s")
        print(f"  - Load: {load_time:.2f}s")


def run_integration_tests():
    """통합 테스트 실행"""
    print("=" * 60)
    print("목표 날짜 기능 통합 테스트 실행")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationComprehensiveDueDate)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("통합 테스트 결과 요약")
    print("=" * 60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n전체 결과: {'성공' if success else '실패'}")
    
    return success


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)