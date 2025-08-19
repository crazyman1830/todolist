"""
SubTask 목표 날짜 기능 데모

Requirements 7.1, 7.4, 5.4 기능 시연:
- 하위 작업에 목표 날짜 설정
- 완료 상태 변경 시 completed_at 필드 업데이트
- 긴급도 및 시간 표시 메서드 구현
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from models.subtask import SubTask


def demo_subtask_due_date():
    """SubTask 목표 날짜 기능 데모"""
    print("=== SubTask 목표 날짜 기능 데모 ===\n")
    
    # 1. SubTask 생성
    subtask = SubTask(
        id=1,
        todo_id=1,
        title="프로젝트 문서 검토",
        is_completed=False,
        created_at=datetime.now()
    )
    
    print(f"1. 생성된 하위 작업: {subtask.title}")
    print(f"   완료 상태: {subtask.is_completed}")
    print(f"   목표 날짜: {subtask.get_due_date()}")
    print(f"   시간 표시: '{subtask.get_time_remaining_text()}'")
    print(f"   긴급도: {subtask.get_urgency_level()}\n")
    
    # 2. 목표 날짜 설정 (3일 후)
    due_date = datetime.now() + timedelta(days=3, hours=2)
    subtask.set_due_date(due_date)
    
    print(f"2. 목표 날짜 설정 (3일 후): {due_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   목표 날짜: {subtask.get_due_date().strftime('%Y-%m-%d %H:%M')}")
    print(f"   지연 상태: {subtask.is_overdue()}")
    print(f"   시간 표시: '{subtask.get_time_remaining_text()}'")
    print(f"   긴급도: {subtask.get_urgency_level()}\n")
    
    # 3. 긴급한 목표 날짜로 변경 (12시간 후)
    urgent_date = datetime.now() + timedelta(hours=12)
    subtask.set_due_date(urgent_date)
    
    print(f"3. 긴급한 목표 날짜로 변경 (12시간 후): {urgent_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   지연 상태: {subtask.is_overdue()}")
    print(f"   시간 표시: '{subtask.get_time_remaining_text()}'")
    print(f"   긴급도: {subtask.get_urgency_level()}\n")
    
    # 4. 지연된 목표 날짜로 변경 (2시간 전)
    overdue_date = datetime.now() - timedelta(hours=2)
    subtask.set_due_date(overdue_date)
    
    print(f"4. 지연된 목표 날짜로 변경 (2시간 전): {overdue_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   지연 상태: {subtask.is_overdue()}")
    print(f"   시간 표시: '{subtask.get_time_remaining_text()}'")
    print(f"   긴급도: {subtask.get_urgency_level()}\n")
    
    # 5. 작업 완료 처리
    print("5. 작업 완료 처리")
    print(f"   완료 전 - 완료 상태: {subtask.is_completed}, 완료 시간: {subtask.completed_at}")
    
    subtask.mark_completed()
    
    print(f"   완료 후 - 완료 상태: {subtask.is_completed}, 완료 시간: {subtask.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   지연 상태: {subtask.is_overdue()}")  # 완료된 작업은 지연되지 않음
    print(f"   시간 표시: '{subtask.get_time_remaining_text()}'")
    print(f"   긴급도: {subtask.get_urgency_level()}\n")  # 완료된 작업은 normal
    
    # 6. 작업 미완료로 변경
    print("6. 작업 미완료로 변경")
    subtask.mark_uncompleted()
    
    print(f"   완료 상태: {subtask.is_completed}, 완료 시간: {subtask.completed_at}")
    print(f"   지연 상태: {subtask.is_overdue()}")  # 다시 지연 상태
    print(f"   긴급도: {subtask.get_urgency_level()}\n")
    
    # 7. 토글 기능 테스트
    print("7. 토글 기능 테스트")
    print(f"   토글 전: 완료={subtask.is_completed}, 완료시간={subtask.completed_at}")
    
    subtask.toggle_completion()
    print(f"   토글 후: 완료={subtask.is_completed}, 완료시간={subtask.completed_at.strftime('%H:%M:%S') if subtask.completed_at else None}")
    
    subtask.toggle_completion()
    print(f"   재토글 후: 완료={subtask.is_completed}, 완료시간={subtask.completed_at}\n")
    
    # 8. 직렬화/역직렬화 테스트
    print("8. 직렬화/역직렬화 테스트")
    subtask.set_due_date(datetime.now() + timedelta(days=1))
    subtask.mark_completed()
    
    # 직렬화
    data = subtask.to_dict()
    print(f"   직렬화된 데이터: due_date={data['due_date']}, completed_at={data['completed_at']}")
    
    # 역직렬화
    restored_subtask = SubTask.from_dict(data)
    print(f"   복원된 SubTask: 제목='{restored_subtask.title}', 완료={restored_subtask.is_completed}")
    print(f"   목표 날짜: {restored_subtask.get_due_date().strftime('%Y-%m-%d %H:%M')}")
    print(f"   시간 표시: '{restored_subtask.get_time_remaining_text()}'")
    
    print("\n=== 데모 완료 ===")


if __name__ == "__main__":
    demo_subtask_due_date()