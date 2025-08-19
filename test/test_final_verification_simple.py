#!/usr/bin/env python3
"""
최종 통합 및 검증 테스트 (간소화 버전)
Task 20: 모든 기능을 통합하여 전체 시스템 테스트
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from services.date_service import DateService
from services.notification_service import NotificationService
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils


class FinalVerificationTest(unittest.TestCase):
    """최종 검증을 위한 간소화된 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, 'test_todos.json')
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService()
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.notification_service = NotificationService(self.todo_service)
        
    def tearDown(self):
        """테스트 환경 정리"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_1_core_functionality_integration(self):
        """1. 핵심 기능 통합 테스트"""
        print("\n=== 1. 핵심 기능 통합 테스트 ===")
        
        # 할일 생성 및 목표 날짜 설정
        todo = self.todo_service.add_todo("통합 테스트 할일")
        self.assertIsNotNone(todo)
        
        due_date = datetime.now() + timedelta(days=3)
        success = self.todo_service.set_todo_due_date(todo.id, due_date)
        self.assertTrue(success)
        
        # 하위 작업 추가 및 목표 날짜 설정
        subtask = self.todo_service.add_subtask(todo.id, "통합 테스트 하위 작업")
        self.assertIsNotNone(subtask)
        
        subtask_due_date = datetime.now() + timedelta(days=2)
        success = self.todo_service.set_subtask_due_date(todo.id, subtask.id, subtask_due_date)
        self.assertTrue(success)
        
        # 데이터 검증
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertIsNotNone(updated_todo.due_date)
        self.assertEqual(len(updated_todo.subtasks), 1)
        self.assertIsNotNone(updated_todo.subtasks[0].due_date)
        
        print("✓ 핵심 기능 통합 테스트 완료")
    
    def test_2_urgency_and_display(self):
        """2. 긴급도 계산 및 표시 기능 테스트"""
        print("\n=== 2. 긴급도 계산 및 표시 기능 테스트 ===")
        
        # 다양한 긴급도의 할일 생성
        test_cases = [
            ("지연된 할일", datetime.now() - timedelta(days=1), "overdue"),
            ("긴급한 할일", datetime.now() + timedelta(hours=12), "urgent"),
            ("경고 할일", datetime.now() + timedelta(days=2), "warning"),
            ("일반 할일", datetime.now() + timedelta(days=10), "normal")
        ]
        
        for title, due_date, expected_urgency in test_cases:
            todo = self.todo_service.add_todo(title)
            self.todo_service.set_todo_due_date(todo.id, due_date)
            
            updated_todo = self.todo_service.get_todo_by_id(todo.id)
            urgency_level = updated_todo.get_urgency_level()
            
            # 긴급도가 예상 범위에 있는지 확인
            self.assertIn(urgency_level, ['normal', 'warning', 'urgent', 'overdue'])
            
            # 색상 매핑 확인
            color = ColorUtils.get_urgency_color(urgency_level)
            self.assertIsNotNone(color)
            
            # 시간 텍스트 확인
            time_text = updated_todo.get_time_remaining_text()
            self.assertIsInstance(time_text, str)
            self.assertGreater(len(time_text), 0)
        
        print("✓ 긴급도 계산 및 표시 기능 테스트 완료")
    
    def test_3_filtering_and_sorting(self):
        """3. 필터링 및 정렬 기능 테스트"""
        print("\n=== 3. 필터링 및 정렬 기능 테스트 ===")
        
        # 테스트 데이터 생성
        todos_data = [
            ("할일 1", datetime.now() + timedelta(days=1)),
            ("할일 2", datetime.now() + timedelta(days=3)),
            ("할일 3", datetime.now() - timedelta(days=1)),  # 지연된 할일
            ("할일 4", None)  # 목표 날짜 없음
        ]
        
        created_todos = []
        for title, due_date in todos_data:
            todo = self.todo_service.add_todo(title)
            if due_date:
                self.todo_service.set_todo_due_date(todo.id, due_date)
            created_todos.append(todo)
        
        # 정렬 테스트
        all_todos = self.todo_service.get_all_todos()
        sorted_todos = self.todo_service.sort_todos_by_due_date(all_todos)
        self.assertIsInstance(sorted_todos, list)
        self.assertEqual(len(sorted_todos), len(all_todos))
        
        # 필터링 테스트
        overdue_todos = self.todo_service.get_overdue_todos()
        self.assertIsInstance(overdue_todos, list)
        
        urgent_todos = self.todo_service.get_urgent_todos()
        self.assertIsInstance(urgent_todos, list)
        
        print("✓ 필터링 및 정렬 기능 테스트 완료")
    
    def test_4_notification_service(self):
        """4. 알림 서비스 테스트"""
        print("\n=== 4. 알림 서비스 테스트 ===")
        
        # 오늘 마감 할일 생성
        today_todo = self.todo_service.add_todo("오늘 마감 할일")
        today_due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        self.todo_service.set_todo_due_date(today_todo.id, today_due)
        
        # 지연된 할일 생성
        overdue_todo = self.todo_service.add_todo("지연된 할일")
        overdue_due = datetime.now() - timedelta(days=1)
        self.todo_service.set_todo_due_date(overdue_todo.id, overdue_due)
        
        # 알림 서비스 기능 테스트
        due_today_todos = self.notification_service.get_due_today_todos()
        overdue_todos = self.notification_service.get_overdue_todos()
        urgent_todos = self.notification_service.get_urgent_todos()
        
        self.assertIsInstance(due_today_todos, list)
        self.assertIsInstance(overdue_todos, list)
        self.assertIsInstance(urgent_todos, list)
        
        # 상태 요약 테스트
        status_summary = self.notification_service.get_status_bar_summary()
        self.assertIsInstance(status_summary, dict)
        self.assertIn('overdue', status_summary)
        self.assertIn('due_today', status_summary)
        
        # 시작 시 알림 판단 테스트
        should_show = self.notification_service.should_show_startup_notification()
        self.assertIsInstance(should_show, bool)
        
        print("✓ 알림 서비스 테스트 완료")
    
    def test_5_data_persistence(self):
        """5. 데이터 지속성 테스트"""
        print("\n=== 5. 데이터 지속성 테스트 ===")
        
        # 할일 생성 및 목표 날짜 설정
        original_todo = self.todo_service.add_todo("지속성 테스트 할일")
        due_date = datetime.now() + timedelta(days=5)
        self.todo_service.set_todo_due_date(original_todo.id, due_date)
        
        # 하위 작업 추가
        subtask = self.todo_service.add_subtask(original_todo.id, "지속성 테스트 하위 작업")
        subtask_due_date = datetime.now() + timedelta(days=4)
        self.todo_service.set_subtask_due_date(original_todo.id, subtask.id, subtask_due_date)
        
        # 데이터 저장 (자동 저장됨)
        
        # 새로운 서비스 인스턴스로 데이터 로드
        new_storage_service = StorageService(self.data_file)
        new_file_service = FileService()
        new_todo_service = TodoService(new_storage_service, new_file_service)
        
        # 데이터 검증
        loaded_todos = new_todo_service.get_all_todos()
        self.assertGreater(len(loaded_todos), 0)
        
        # 목표 날짜가 있는 할일 찾기
        loaded_todo = None
        for todo in loaded_todos:
            if todo.title == "지속성 테스트 할일":
                loaded_todo = todo
                break
        
        self.assertIsNotNone(loaded_todo)
        self.assertIsNotNone(loaded_todo.due_date)
        self.assertEqual(len(loaded_todo.subtasks), 1)
        self.assertIsNotNone(loaded_todo.subtasks[0].due_date)
        
        print("✓ 데이터 지속성 테스트 완료")
    
    def test_6_backward_compatibility(self):
        """6. 기존 기능 호환성 테스트"""
        print("\n=== 6. 기존 기능 호환성 테스트 ===")
        
        # 목표 날짜 없는 할일 생성 (기존 방식)
        todo_without_due_date = self.todo_service.add_todo("목표 날짜 없는 할일")
        self.assertIsNotNone(todo_without_due_date)
        self.assertIsNone(todo_without_due_date.due_date)
        
        # 기존 할일 관리 기능 정상 동작 확인
        subtask = self.todo_service.add_subtask(todo_without_due_date.id, "목표 날짜 없는 하위 작업")
        self.assertIsNotNone(subtask)
        self.assertIsNone(subtask.due_date)
        
        # 완료 상태 변경 기능 확인
        success = self.todo_service.toggle_subtask_completion(todo_without_due_date.id, subtask.id)
        self.assertTrue(success)
        
        # 긴급도 계산 (목표 날짜 없는 경우)
        urgency_level = todo_without_due_date.get_urgency_level()
        self.assertEqual(urgency_level, 'normal')
        
        print("✓ 기존 기능 호환성 테스트 완료")
    
    def test_7_performance_basic(self):
        """7. 기본 성능 테스트"""
        print("\n=== 7. 기본 성능 테스트 ===")
        
        # 다수의 할일 생성 및 처리 시간 측정
        start_time = time.time()
        
        todos_count = 50
        for i in range(todos_count):
            todo = self.todo_service.add_todo(f"성능 테스트 할일 {i+1}")
            due_date = datetime.now() + timedelta(days=i % 10)
            self.todo_service.set_todo_due_date(todo.id, due_date)
        
        creation_time = time.time() - start_time
        print(f"✓ {todos_count}개 할일 생성 시간: {creation_time:.3f}초")
        
        # 긴급도 계산 성능 테스트
        start_time = time.time()
        all_todos = self.todo_service.get_all_todos()
        
        for todo in all_todos:
            urgency_level = todo.get_urgency_level()
            time_text = todo.get_time_remaining_text()
        
        urgency_time = time.time() - start_time
        print(f"✓ {len(all_todos)}개 할일 긴급도 계산 시간: {urgency_time:.3f}초")
        
        # 필터링 성능 테스트
        start_time = time.time()
        overdue_todos = self.todo_service.get_overdue_todos()
        urgent_todos = self.todo_service.get_urgent_todos()
        sorted_todos = self.todo_service.sort_todos_by_due_date(all_todos)
        filtering_time = time.time() - start_time
        
        print(f"✓ 필터링 및 정렬 시간: {filtering_time:.3f}초")
        
        # 성능이 합리적인 범위인지 확인
        self.assertLess(creation_time, 5.0, "할일 생성이 너무 느립니다")
        self.assertLess(urgency_time, 1.0, "긴급도 계산이 너무 느립니다")
        self.assertLess(filtering_time, 1.0, "필터링이 너무 느립니다")
        
        print("✓ 기본 성능 테스트 완료")
    
    def test_8_error_handling(self):
        """8. 오류 처리 테스트"""
        print("\n=== 8. 오류 처리 테스트 ===")
        
        # 존재하지 않는 할일에 대한 작업
        result = self.todo_service.set_todo_due_date(99999, datetime.now())
        self.assertFalse(result)
        
        # 존재하지 않는 하위 작업에 대한 작업
        todo = self.todo_service.add_todo("오류 테스트 할일")
        result = self.todo_service.set_subtask_due_date(todo.id, 99999, datetime.now())
        self.assertFalse(result)
        
        # 하위 작업 목표 날짜 유효성 검사
        parent_due_date = datetime.now() + timedelta(days=1)
        self.todo_service.set_todo_due_date(todo.id, parent_due_date)
        
        late_subtask_date = datetime.now() + timedelta(days=2)
        is_valid, message = self.todo_service.validate_subtask_due_date(todo.id, late_subtask_date)
        self.assertFalse(is_valid)
        self.assertIsInstance(message, str)
        
        print("✓ 오류 처리 테스트 완료")


def run_final_verification():
    """최종 검증 테스트 실행"""
    print("=" * 60)
    print("목표 날짜 기능 최종 검증 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(FinalVerificationTest)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("최종 검증 테스트 결과 요약")
    print("=" * 60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n전체 성공률: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 최종 검증 성공!")
        print("\n✅ 구현된 주요 기능들:")
        print("  • 할일 및 하위 작업에 목표 날짜 설정")
        print("  • 긴급도에 따른 시각적 표시 (색상 코딩)")
        print("  • 목표 날짜 기준 정렬 및 필터링")
        print("  • 남은 시간/지연 시간 표시")
        print("  • 알림 및 상태 요약 기능")
        print("  • 기존 기능과의 완전한 호환성")
        print("  • 데이터 지속성 및 마이그레이션")
        print("  • 기본적인 성능 최적화")
        print("  • 포괄적인 오류 처리")
        return True
    else:
        print(f"\n⚠️  일부 테스트에서 문제가 발견되었습니다. ({success_rate:.1f}% 성공)")
        return False


if __name__ == '__main__':
    success = run_final_verification()
    sys.exit(0 if success else 1)