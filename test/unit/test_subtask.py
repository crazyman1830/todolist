import unittest
import os
import sys
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.subtask import SubTask


class TestSubTask(unittest.TestCase):
    """SubTask 모델 단위 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_datetime = datetime(2025, 1, 8, 10, 30, 0)
        self.subtask = SubTask(
            id=1,
            todo_id=5,
            title="테스트 하위 작업",
            is_completed=False,
            created_at=self.test_datetime
        )
    
    def test_subtask_creation_with_all_fields(self):
        """모든 필드를 지정하여 SubTask 생성 테스트"""
        subtask = SubTask(
            id=2,
            todo_id=10,
            title="완전한 하위 작업",
            is_completed=True,
            created_at=self.test_datetime
        )
        
        self.assertEqual(subtask.id, 2)
        self.assertEqual(subtask.todo_id, 10)
        self.assertEqual(subtask.title, "완전한 하위 작업")
        self.assertTrue(subtask.is_completed)
        self.assertEqual(subtask.created_at, self.test_datetime)
    
    def test_subtask_creation_with_defaults(self):
        """기본값을 사용하여 SubTask 생성 테스트"""
        subtask = SubTask(id=3, todo_id=15, title="기본값 하위 작업")
        
        self.assertEqual(subtask.id, 3)
        self.assertEqual(subtask.todo_id, 15)
        self.assertEqual(subtask.title, "기본값 하위 작업")
        self.assertFalse(subtask.is_completed)  # 기본값은 False
        self.assertIsInstance(subtask.created_at, datetime)
    
    def test_to_dict_serialization(self):
        """SubTask 객체의 딕셔너리 직렬화 테스트"""
        result = self.subtask.to_dict()
        
        expected = {
            'id': 1,
            'todo_id': 5,
            'title': "테스트 하위 작업",
            'is_completed': False,
            'created_at': self.test_datetime.isoformat(),
            'due_date': None,
            'completed_at': None
        }
        
        self.assertEqual(result, expected)
    
    def test_to_dict_with_completed_subtask(self):
        """완료된 SubTask의 딕셔너리 직렬화 테스트"""
        self.subtask.is_completed = True
        result = self.subtask.to_dict()
        
        self.assertTrue(result['is_completed'])
    
    def test_from_dict_deserialization(self):
        """딕셔너리에서 SubTask 객체로 역직렬화 테스트"""
        data = {
            'id': 7,
            'todo_id': 20,
            'title': "역직렬화 테스트",
            'is_completed': True,
            'created_at': self.test_datetime.isoformat()
        }
        
        subtask = SubTask.from_dict(data)
        
        self.assertEqual(subtask.id, 7)
        self.assertEqual(subtask.todo_id, 20)
        self.assertEqual(subtask.title, "역직렬화 테스트")
        self.assertTrue(subtask.is_completed)
        self.assertEqual(subtask.created_at, self.test_datetime)
    
    def test_serialization_roundtrip(self):
        """직렬화 후 역직렬화 라운드트립 테스트"""
        # 직렬화
        data = self.subtask.to_dict()
        
        # 역직렬화
        restored_subtask = SubTask.from_dict(data)
        
        # 원본과 복원된 객체 비교
        self.assertEqual(self.subtask.id, restored_subtask.id)
        self.assertEqual(self.subtask.todo_id, restored_subtask.todo_id)
        self.assertEqual(self.subtask.title, restored_subtask.title)
        self.assertEqual(self.subtask.is_completed, restored_subtask.is_completed)
        self.assertEqual(self.subtask.created_at, restored_subtask.created_at)
    
    def test_toggle_completion_from_false_to_true(self):
        """완료 상태를 False에서 True로 토글 테스트"""
        self.assertFalse(self.subtask.is_completed)
        
        self.subtask.toggle_completion()
        
        self.assertTrue(self.subtask.is_completed)
    
    def test_toggle_completion_from_true_to_false(self):
        """완료 상태를 True에서 False로 토글 테스트"""
        self.subtask.is_completed = True
        self.assertTrue(self.subtask.is_completed)
        
        self.subtask.toggle_completion()
        
        self.assertFalse(self.subtask.is_completed)
    
    def test_multiple_toggle_completion(self):
        """여러 번 토글 테스트"""
        original_state = self.subtask.is_completed
        
        # 첫 번째 토글
        self.subtask.toggle_completion()
        self.assertEqual(self.subtask.is_completed, not original_state)
        
        # 두 번째 토글 (원래 상태로 복원)
        self.subtask.toggle_completion()
        self.assertEqual(self.subtask.is_completed, original_state)
    
    def test_subtask_with_empty_title(self):
        """빈 제목으로 SubTask 생성 테스트"""
        subtask = SubTask(id=8, todo_id=25, title="")
        
        self.assertEqual(subtask.title, "")
        self.assertEqual(subtask.id, 8)
        self.assertEqual(subtask.todo_id, 25)
    
    def test_subtask_with_special_characters_in_title(self):
        """특수문자가 포함된 제목으로 SubTask 생성 테스트"""
        special_title = "테스트 & 검증 (중요!) - 완료 필요"
        subtask = SubTask(id=9, todo_id=30, title=special_title)
        
        self.assertEqual(subtask.title, special_title)
        
        # 직렬화/역직렬화 테스트
        data = subtask.to_dict()
        restored = SubTask.from_dict(data)
        self.assertEqual(restored.title, special_title)
    
    def test_subtask_datetime_handling(self):
        """다양한 datetime 형식 처리 테스트"""
        # 현재 시간으로 생성
        subtask1 = SubTask(id=10, todo_id=35, title="현재 시간")
        self.assertIsInstance(subtask1.created_at, datetime)
        
        # 특정 시간으로 생성
        specific_time = datetime(2025, 12, 25, 15, 30, 45)
        subtask2 = SubTask(id=11, todo_id=40, title="특정 시간", created_at=specific_time)
        self.assertEqual(subtask2.created_at, specific_time)
    
    def test_subtask_equality_comparison(self):
        """SubTask 객체 동등성 비교 테스트"""
        subtask1 = SubTask(
            id=12,
            todo_id=45,
            title="동등성 테스트",
            is_completed=False,
            created_at=self.test_datetime
        )
        
        subtask2 = SubTask(
            id=12,
            todo_id=45,
            title="동등성 테스트",
            is_completed=False,
            created_at=self.test_datetime
        )
        
        # dataclass는 자동으로 __eq__ 메서드를 생성
        self.assertEqual(subtask1, subtask2)
    
    def test_subtask_different_objects_inequality(self):
        """다른 SubTask 객체 비동등성 테스트"""
        subtask1 = SubTask(id=13, todo_id=50, title="첫 번째")
        subtask2 = SubTask(id=14, todo_id=50, title="두 번째")
        
        self.assertNotEqual(subtask1, subtask2)
    
    def test_subtask_creation_with_due_date(self):
        """목표 날짜가 포함된 SubTask 생성 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        subtask = SubTask(
            id=15,
            todo_id=55,
            title="목표 날짜 하위 작업",
            due_date=due_date
        )
        
        self.assertEqual(subtask.due_date, due_date)
        self.assertIsNone(subtask.completed_at)
    
    def test_to_dict_with_due_date(self):
        """목표 날짜가 포함된 SubTask의 딕셔너리 직렬화 테스트"""
        due_date = datetime(2025, 1, 15, 18, 0, 0)
        self.subtask.due_date = due_date
        
        result = self.subtask.to_dict()
        
        self.assertEqual(result['due_date'], "2025-01-15T18:00:00")
        self.assertIsNone(result['completed_at'])
    
    def test_to_dict_without_due_date(self):
        """목표 날짜가 없는 SubTask의 딕셔너리 직렬화 테스트"""
        result = self.subtask.to_dict()
        
        self.assertIsNone(result['due_date'])
        self.assertIsNone(result['completed_at'])
    
    def test_from_dict_with_due_date(self):
        """목표 날짜가 포함된 딕셔너리에서 SubTask 객체 역직렬화 테스트"""
        data = {
            'id': 16,
            'todo_id': 60,
            'title': "목표 날짜 테스트",
            'is_completed': False,
            'created_at': self.test_datetime.isoformat(),
            'due_date': "2025-01-15T18:00:00",
            'completed_at': None
        }
        
        subtask = SubTask.from_dict(data)
        
        self.assertEqual(subtask.due_date, datetime(2025, 1, 15, 18, 0, 0))
        self.assertIsNone(subtask.completed_at)
    
    def test_from_dict_with_completed_at(self):
        """완료 날짜가 포함된 딕셔너리에서 SubTask 객체 역직렬화 테스트"""
        data = {
            'id': 17,
            'todo_id': 65,
            'title': "완료 날짜 테스트",
            'is_completed': True,
            'created_at': self.test_datetime.isoformat(),
            'due_date': "2025-01-15T18:00:00",
            'completed_at': "2025-01-14T16:30:00"
        }
        
        subtask = SubTask.from_dict(data)
        
        self.assertEqual(subtask.due_date, datetime(2025, 1, 15, 18, 0, 0))
        self.assertEqual(subtask.completed_at, datetime(2025, 1, 14, 16, 30, 0))
    
    def test_from_dict_backward_compatibility(self):
        """기존 데이터 구조와의 하위 호환성 테스트 (due_date, completed_at 필드 없음)"""
        data = {
            'id': 18,
            'todo_id': 70,
            'title': "기존 하위 작업",
            'is_completed': False,
            'created_at': self.test_datetime.isoformat()
        }
        
        subtask = SubTask.from_dict(data)
        
        self.assertEqual(subtask.id, 18)
        self.assertEqual(subtask.title, "기존 하위 작업")
        self.assertIsNone(subtask.due_date)
        self.assertIsNone(subtask.completed_at)
    
    def test_from_dict_null_due_date(self):
        """null 값의 목표 날짜 처리 테스트"""
        data = {
            'id': 19,
            'todo_id': 75,
            'title': "null 목표 날짜 테스트",
            'is_completed': False,
            'created_at': self.test_datetime.isoformat(),
            'due_date': None,
            'completed_at': None
        }
        
        subtask = SubTask.from_dict(data)
        
        self.assertIsNone(subtask.due_date)
        self.assertIsNone(subtask.completed_at)
    
    def test_serialization_roundtrip_with_due_date(self):
        """목표 날짜가 포함된 직렬화 후 역직렬화 라운드트립 테스트"""
        due_date = datetime(2025, 1, 20, 14, 30, 0)
        completed_at = datetime(2025, 1, 19, 10, 15, 0)
        
        self.subtask.due_date = due_date
        self.subtask.completed_at = completed_at
        
        # 직렬화
        data = self.subtask.to_dict()
        
        # 역직렬화
        restored_subtask = SubTask.from_dict(data)
        
        # 원본과 복원된 객체 비교
        self.assertEqual(self.subtask.id, restored_subtask.id)
        self.assertEqual(self.subtask.todo_id, restored_subtask.todo_id)
        self.assertEqual(self.subtask.title, restored_subtask.title)
        self.assertEqual(self.subtask.is_completed, restored_subtask.is_completed)
        self.assertEqual(self.subtask.created_at, restored_subtask.created_at)
        self.assertEqual(self.subtask.due_date, restored_subtask.due_date)
        self.assertEqual(self.subtask.completed_at, restored_subtask.completed_at)


if __name__ == '__main__':
    unittest.main()