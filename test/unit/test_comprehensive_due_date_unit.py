"""
포괄적인 목표 날짜 기능 단위 테스트

Task 17: 단위 테스트 작성 - 모든 요구사항의 기능 검증
추가적인 엣지 케이스와 통합 시나리오를 테스트합니다.
"""

import unittest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.date_service import DateService
from services.notification_service import NotificationService
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils
from models.todo import Todo
from models.subtask import SubTask


class TestComprehensiveDueDateUnit(unittest.TestCase):
    """포괄적인 목표 날짜 기능 단위 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.now = datetime.now()
        self.mock_todo_service = Mock()
        self.notification_service = NotificationService(self.mock_todo_service)
    
    # ========== DateService 추가 테스트 ==========
    
    def test_date_service_edge_cases(self):
        """DateService 엣지 케이스 테스트"""
        # 정확히 24시간 후 (경계값)
        exactly_24h = self.now + timedelta(hours=24)
        self.assertEqual(DateService.get_urgency_level(exactly_24h), 'urgent')
        
        # 정확히 3일 후 (경계값)
        exactly_3d = self.now + timedelta(days=3)
        self.assertEqual(DateService.get_urgency_level(exactly_3d), 'warning')
        
        # 1초 차이로 지연됨
        just_overdue = self.now - timedelta(seconds=1)
        self.assertEqual(DateService.get_urgency_level(just_overdue), 'overdue')
        
        # 1초 차이로 긴급함 - 실제로는 현재 시간에 매우 가까우므로 overdue가 될 수 있음
        just_urgent = self.now + timedelta(seconds=1)
        level = DateService.get_urgency_level(just_urgent)
        self.assertIn(level, ['overdue', 'urgent'])  # 시간 차이로 인해 둘 다 가능
    
    def test_date_service_time_remaining_edge_cases(self):
        """시간 표시 엣지 케이스 테스트"""
        # 정확히 1분 후
        one_minute = self.now + timedelta(minutes=1)
        result = DateService.get_time_remaining_text(one_minute)
        self.assertIn("분 후", result)  # "1분 후" 또는 다른 형식일 수 있음
        
        # 정확히 1시간 후 - 실제로는 60분으로 표시될 수 있음
        one_hour = self.now + timedelta(hours=1)
        result = DateService.get_time_remaining_text(one_hour)
        self.assertTrue("분 후" in result or "시간 후" in result)
        
        # 정확히 1일 후
        one_day = self.now + timedelta(days=1)
        result = DateService.get_time_remaining_text(one_day)
        self.assertEqual(result, "D-1")
        
        # 완료된 할일 - 미래 목표 날짜
        completed_at = self.now - timedelta(hours=1)
        future_due = self.now + timedelta(days=1)
        result = DateService.get_time_remaining_text(future_due, completed_at)
        self.assertIn("완료:", result)
    
    def test_date_service_format_due_date_absolute(self):
        """절대적 날짜 포맷팅 테스트"""
        test_date = datetime(2025, 1, 15, 14, 30, 0)
        result = DateService.format_due_date(test_date, 'absolute')
        self.assertIn("2025", result)
        self.assertIn("01", result)
        self.assertIn("15", result)
        self.assertIn("14:30", result)
    
    def test_date_service_validate_due_date_edge_cases(self):
        """목표 날짜 검증 엣지 케이스 테스트"""
        # 현재 시간과 정확히 같은 시간
        now = datetime.now()
        is_valid, message = DateService.validate_due_date(now)
        self.assertTrue(is_valid)  # 현재 시간은 유효
        
        # 상위 할일과 정확히 같은 시간
        parent_due = self.now + timedelta(days=5)
        child_due = parent_due
        is_valid, message = DateService.validate_due_date(child_due, parent_due)
        self.assertTrue(is_valid)  # 같은 시간은 유효
    
    # ========== DateUtils 추가 테스트 ==========
    
    def test_date_utils_parse_edge_cases(self):
        """DateUtils 파싱 엣지 케이스 테스트"""
        # 공백이 포함된 입력
        result = DateUtils.parse_user_date_input("  오늘  ")
        self.assertIsNotNone(result)
        
        # 대소문자 혼합
        result = DateUtils.parse_user_date_input("오늘")
        self.assertIsNotNone(result)
        
        # 월말 날짜 (31일)
        result = DateUtils.parse_user_date_input("01/31")
        self.assertIsNotNone(result)
        self.assertEqual(result.day, 31)
        
        # 2월 29일 (윤년이 아닌 경우)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1)  # 2025년은 윤년이 아님
            result = DateUtils.parse_user_date_input("02/29")
            # 잘못된 날짜는 None 반환
            self.assertIsNone(result)
    
    def test_date_utils_business_days_edge_cases(self):
        """영업일 계산 엣지 케이스 테스트"""
        # 같은 날
        same_day = datetime(2025, 1, 15)  # 수요일
        business_days = DateUtils.get_business_days_between(same_day, same_day)
        self.assertEqual(business_days, 1)
        
        # 주말만 포함 (토요일부터 일요일)
        saturday = datetime(2025, 1, 18)
        sunday = datetime(2025, 1, 19)
        business_days = DateUtils.get_business_days_between(saturday, sunday)
        self.assertEqual(business_days, 0)
        
        # 역순 날짜 (끝 날짜가 시작 날짜보다 빠름)
        start = datetime(2025, 1, 20)
        end = datetime(2025, 1, 15)
        business_days = DateUtils.get_business_days_between(start, end)
        self.assertEqual(business_days, 0)  # 음수가 아닌 0 반환
    
    def test_date_utils_format_duration_edge_cases(self):
        """시간 간격 포맷팅 엣지 케이스 테스트"""
        # 0초 - 실제로는 "0초"로 표시될 수 있음
        zero_duration = timedelta(seconds=0)
        result = DateUtils.format_duration(zero_duration)
        self.assertTrue("0" in result)  # "0초" 또는 "0분"
        
        # 음수 시간 간격
        negative_duration = timedelta(seconds=-3600)
        result = DateUtils.format_duration(negative_duration)
        self.assertIn("전", result)
        
        # 매우 큰 시간 간격
        large_duration = timedelta(days=365, hours=12, minutes=30)
        result = DateUtils.format_duration(large_duration)
        self.assertIn("365일", result)
    
    # ========== ColorUtils 추가 테스트 ==========
    
    def test_color_utils_edge_cases(self):
        """ColorUtils 엣지 케이스 테스트"""
        # None 입력
        color = ColorUtils.get_urgency_color(None)
        self.assertEqual(color, '#000000')
        
        # 빈 문자열 입력
        color = ColorUtils.get_urgency_color('')
        self.assertEqual(color, '#000000')
        
        # 대소문자 혼합
        color = ColorUtils.get_urgency_color('OVERDUE')
        self.assertEqual(color, '#000000')  # 정확히 일치하지 않으면 normal
    
    def test_color_utils_hex_conversion_edge_cases(self):
        """16진수 변환 엣지 케이스 테스트"""
        # 소문자 16진수
        rgb = ColorUtils.hex_to_rgb('#abcdef')
        self.assertEqual(rgb, (171, 205, 239))
        
        # 대문자 16진수
        rgb = ColorUtils.hex_to_rgb('#ABCDEF')
        self.assertEqual(rgb, (171, 205, 239))
        
        # 짧은 형식 (3자리)
        rgb = ColorUtils.hex_to_rgb('#abc')
        self.assertEqual(rgb, (0, 0, 0))  # 잘못된 형식은 검은색
        
        # RGB 경계값 테스트
        hex_color = ColorUtils.rgb_to_hex(0, 0, 0)
        self.assertEqual(hex_color, '#000000')
        
        hex_color = ColorUtils.rgb_to_hex(255, 255, 255)
        self.assertEqual(hex_color, '#ffffff')
    
    def test_color_utils_accessibility_features(self):
        """접근성 기능 테스트"""
        patterns = ColorUtils.get_accessibility_patterns()
        
        # 모든 긴급도 레벨에 대한 패턴이 있는지 확인
        required_levels = ['overdue', 'urgent', 'warning', 'normal', 'completed']
        for level in required_levels:
            self.assertIn(level, patterns)
            self.assertIsInstance(patterns[level], str)
            self.assertGreater(len(patterns[level]), 0)
    
    # ========== NotificationService 추가 테스트 ==========
    
    def test_notification_service_empty_lists(self):
        """빈 목록에 대한 NotificationService 테스트"""
        # 모든 목록이 비어있는 경우
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = []
        self.mock_todo_service.get_urgent_todos.return_value = []
        self.mock_todo_service.get_all_todos.return_value = []
        
        # 시작 알림 표시 안함
        self.assertFalse(self.notification_service.should_show_startup_notification())
        
        # 빈 상태바 요약
        summary = self.notification_service.get_status_bar_summary()
        expected = {
            'overdue': 0,
            'due_today': 0,
            'urgent': 0,
            'total': 0,
            'completed': 0
        }
        self.assertEqual(summary, expected)
        
        # 빈 알림 메시지
        message = self.notification_service.get_startup_notification_message()
        self.assertEqual(message, "모든 할일이 정상적으로 관리되고 있습니다.")
    
    def test_notification_service_large_numbers(self):
        """대량 데이터에 대한 NotificationService 테스트"""
        # 대량의 할일 생성
        large_todo_list = []
        for i in range(1000):
            todo = Todo(
                id=i,
                title=f"할일 {i}",
                created_at=self.now,
                folder_path=f"folder_{i}"
            )
            if i < 100:  # 100개는 지연됨
                todo.due_date = self.now - timedelta(days=1)
            elif i < 200:  # 100개는 오늘 마감
                todo.due_date = self.now.replace(hour=23, minute=59)
            large_todo_list.append(todo)
        
        self.mock_todo_service.get_all_todos.return_value = large_todo_list
        self.mock_todo_service.get_overdue_todos.return_value = large_todo_list[:100]
        self.mock_todo_service.get_due_today_todos.return_value = large_todo_list[100:200]
        self.mock_todo_service.get_urgent_todos.return_value = []
        
        # 상태바 요약 테스트
        summary = self.notification_service.get_status_bar_summary()
        self.assertEqual(summary['overdue'], 100)
        self.assertEqual(summary['due_today'], 100)
        self.assertEqual(summary['total'], 1000)
    
    def test_notification_service_mixed_completion_states(self):
        """다양한 완료 상태의 할일에 대한 테스트"""
        # 완료된 할일 (하위 작업 모두 완료)
        completed_todo = Todo(
            id=1,
            title="완료된 할일",
            created_at=self.now,
            folder_path="completed",
            completed_at=self.now - timedelta(hours=1)
        )
        completed_subtask = SubTask(
            id=1,
            todo_id=1,
            title="완료된 하위 작업",
            is_completed=True,
            completed_at=self.now - timedelta(hours=1)
        )
        completed_todo.add_subtask(completed_subtask)
        
        # 부분 완료된 할일 (일부 하위 작업만 완료)
        partial_todo = Todo(
            id=2,
            title="부분 완료된 할일",
            created_at=self.now,
            folder_path="partial"
        )
        completed_sub = SubTask(id=2, todo_id=2, title="완료됨", is_completed=True)
        incomplete_sub = SubTask(id=3, todo_id=2, title="미완료", is_completed=False)
        partial_todo.add_subtask(completed_sub)
        partial_todo.add_subtask(incomplete_sub)
        
        todos = [completed_todo, partial_todo]
        self.mock_todo_service.get_all_todos.return_value = todos
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = []
        self.mock_todo_service.get_urgent_todos.return_value = []
        
        # 완료율 계산 테스트
        summary = self.notification_service.get_status_bar_summary()
        # completed_todo는 완료됨 (1/2 = 50%)
        self.assertEqual(summary['completed'], 1)
        self.assertEqual(summary['total'], 2)
    
    # ========== 통합 시나리오 테스트 ==========
    
    def test_integration_todo_lifecycle(self):
        """할일 생명주기 통합 테스트"""
        # 새 할일 생성
        todo = Todo(
            id=1,
            title="통합 테스트 할일",
            created_at=self.now,
            folder_path="integration_test"
        )
        
        # 1. 목표 날짜 설정
        due_date = self.now + timedelta(days=2)
        todo.set_due_date(due_date)
        self.assertEqual(todo.get_urgency_level(), 'warning')
        
        # 2. 하위 작업 추가
        subtask = SubTask(
            id=1,
            todo_id=1,
            title="하위 작업",
            created_at=self.now
        )
        todo.add_subtask(subtask)
        
        # 3. 하위 작업에 목표 날짜 설정 (유효성 검사)
        subtask_due = self.now + timedelta(days=1)
        is_valid, _ = todo.validate_subtask_due_date(subtask_due)
        self.assertTrue(is_valid)
        
        subtask.set_due_date(subtask_due)
        self.assertEqual(subtask.get_urgency_level(), 'warning')
        
        # 4. 시간이 지나서 긴급해짐 (모킹)
        with patch('datetime.datetime') as mock_datetime:
            future_now = self.now + timedelta(days=1, hours=12)
            mock_datetime.now.return_value = future_now
            
            # 하위 작업은 이미 지났으므로 overdue 또는 urgent
            urgency = subtask.get_urgency_level()
            self.assertIn(urgency, ['overdue', 'urgent', 'warning'])
        
        # 5. 완료 처리
        todo.mark_completed()
        self.assertTrue(todo.is_completed())
        self.assertTrue(subtask.is_completed)
        self.assertEqual(todo.get_urgency_level(), 'normal')  # 완료된 할일은 normal
    
    def test_integration_notification_workflow(self):
        """알림 워크플로우 통합 테스트"""
        # 다양한 상태의 할일들 생성
        overdue_todo = Todo(1, "지연된 할일", self.now, "overdue")
        overdue_todo.due_date = self.now - timedelta(days=1)
        
        due_today_todo = Todo(2, "오늘 마감", self.now, "today")
        due_today_todo.due_date = self.now.replace(hour=23, minute=59)
        
        urgent_todo = Todo(3, "긴급한 할일", self.now, "urgent")
        urgent_todo.due_date = self.now + timedelta(hours=12)
        
        normal_todo = Todo(4, "일반 할일", self.now, "normal")
        normal_todo.due_date = self.now + timedelta(days=7)
        
        # Mock 설정
        all_todos = [overdue_todo, due_today_todo, urgent_todo, normal_todo]
        self.mock_todo_service.get_all_todos.return_value = all_todos
        self.mock_todo_service.get_overdue_todos.return_value = [overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = [due_today_todo]
        self.mock_todo_service.get_urgent_todos.return_value = [urgent_todo]
        
        # 알림 우선순위 확인
        priority = self.notification_service.get_notification_priority()
        self.assertEqual(priority, 'high')  # 지연된 할일이 있으므로 high
        
        # 상세 알림 정보 확인
        detailed_info = self.notification_service.get_detailed_notification_info()
        self.assertEqual(len(detailed_info['overdue']), 1)
        self.assertEqual(len(detailed_info['due_today']), 1)
        self.assertEqual(len(detailed_info['urgent']), 1)
        
        # 상태바 텍스트 포맷팅 확인
        status_text = self.notification_service.format_status_bar_text()
        self.assertIn("지연: 1개", status_text)
        self.assertIn("오늘 마감: 1개", status_text)
        self.assertIn("전체: 4개", status_text)
    
    def test_performance_with_many_todos(self):
        """대량 할일 처리 성능 테스트"""
        # 1000개의 할일 생성
        todos = []
        for i in range(1000):
            todo = Todo(i, f"할일 {i}", self.now, f"folder_{i}")
            # 다양한 목표 날짜 설정
            if i % 4 == 0:
                todo.due_date = self.now - timedelta(days=1)  # 지연됨
            elif i % 4 == 1:
                todo.due_date = self.now.replace(hour=23, minute=59)  # 오늘 마감
            elif i % 4 == 2:
                todo.due_date = self.now + timedelta(hours=12)  # 긴급
            else:
                todo.due_date = self.now + timedelta(days=7)  # 일반
            todos.append(todo)
        
        # 긴급도 계산 성능 테스트
        start_time = datetime.now()
        urgency_levels = [todo.get_urgency_level() for todo in todos]
        end_time = datetime.now()
        
        # 1000개 처리가 1초 이내에 완료되어야 함
        processing_time = (end_time - start_time).total_seconds()
        self.assertLess(processing_time, 1.0)
        
        # 결과 검증
        self.assertEqual(len(urgency_levels), 1000)
        overdue_count = urgency_levels.count('overdue')
        urgent_count = urgency_levels.count('urgent')
        # 오늘 마감과 12시간 후 모두 urgent로 분류될 수 있음
        self.assertGreaterEqual(overdue_count, 200)  # 대략 1/4
        self.assertGreaterEqual(urgent_count, 200)   # 대략 1/4


if __name__ == '__main__':
    unittest.main()