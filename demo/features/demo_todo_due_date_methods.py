"""
Todo 모델의 목표 날짜 관련 메서드 데모

Task 3 구현 결과를 시연합니다.
"""

import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from models.subtask import SubTask


def demo_todo_due_date_methods():
    """Todo 모델의 목표 날짜 관련 메서드 데모"""
    print("=== Todo 모델 목표 날짜 메서드 데모 ===\n")
    
    # Todo 생성
    todo = Todo(
        id=1,
        title="프로젝트 문서 작성",
        created_at=datetime.now(),
        folder_path="demo_folder"
    )
    
    # 하위 작업 추가
    subtask1 = SubTask(id=1, todo_id=1, title="요구사항 분석")
    subtask2 = SubTask(id=2, todo_id=1, title="설계 문서 작성")
    todo.add_subtask(subtask1)
    todo.add_subtask(subtask2)
    
    print(f"할일: {todo.title}")
    print(f"하위 작업: {[st.title for st in todo.subtasks]}\n")
    
    # 1. 목표 날짜 설정 및 조회
    print("1. 목표 날짜 설정 및 조회")
    print(f"초기 목표 날짜: {todo.get_due_date()}")
    
    due_date = datetime.now() + timedelta(days=3, hours=6)
    todo.set_due_date(due_date)
    print(f"설정된 목표 날짜: {todo.get_due_date()}")
    print(f"목표 날짜 (포맷): {due_date.strftime('%Y-%m-%d %H:%M')}\n")
    
    # 2. 긴급도 레벨 확인
    print("2. 긴급도 레벨 확인")
    print(f"현재 긴급도: {todo.get_urgency_level()}")
    
    # 다양한 날짜로 긴급도 테스트
    test_dates = [
        ("과거 날짜", datetime.now() - timedelta(hours=1)),
        ("12시간 후", datetime.now() + timedelta(hours=12)),
        ("2일 후", datetime.now() + timedelta(days=2)),
        ("1주일 후", datetime.now() + timedelta(days=7))
    ]
    
    for desc, test_date in test_dates:
        todo.set_due_date(test_date)
        print(f"{desc}: {todo.get_urgency_level()}")
    
    # 원래 날짜로 복원
    todo.set_due_date(due_date)
    print()
    
    # 3. 남은 시간 텍스트
    print("3. 남은 시간 텍스트")
    print(f"남은 시간: {todo.get_time_remaining_text()}")
    
    # 다양한 날짜로 시간 텍스트 테스트
    for desc, test_date in test_dates:
        todo.set_due_date(test_date)
        print(f"{desc}: {todo.get_time_remaining_text()}")
    
    # 원래 날짜로 복원
    todo.set_due_date(due_date)
    print()
    
    # 4. 지연 상태 확인
    print("4. 지연 상태 확인")
    print(f"현재 지연 상태: {todo.is_overdue()}")
    
    past_date = datetime.now() - timedelta(hours=2)
    todo.set_due_date(past_date)
    print(f"과거 날짜 설정 후 지연 상태: {todo.is_overdue()}")
    
    # 원래 날짜로 복원
    todo.set_due_date(due_date)
    print()
    
    # 5. 하위 작업 목표 날짜 유효성 검사
    print("5. 하위 작업 목표 날짜 유효성 검사")
    
    # 유효한 하위 작업 날짜
    valid_subtask_date = datetime.now() + timedelta(days=2)
    is_valid, message = todo.validate_subtask_due_date(valid_subtask_date)
    print(f"유효한 하위 작업 날짜 ({valid_subtask_date.strftime('%m/%d %H:%M')}): {is_valid}")
    if message:
        print(f"메시지: {message}")
    
    # 무효한 하위 작업 날짜
    invalid_subtask_date = datetime.now() + timedelta(days=5)
    is_valid, message = todo.validate_subtask_due_date(invalid_subtask_date)
    print(f"무효한 하위 작업 날짜 ({invalid_subtask_date.strftime('%m/%d %H:%M')}): {is_valid}")
    if message:
        print(f"메시지: {message}")
    print()
    
    # 6. 하위 작업 지연 확인
    print("6. 하위 작업 지연 확인")
    print(f"초기 지연된 하위 작업 여부: {todo.has_overdue_subtasks()}")
    
    # 하위 작업에 과거 날짜 설정
    subtask1.due_date = datetime.now() - timedelta(hours=1)
    print(f"하위 작업에 과거 날짜 설정 후: {todo.has_overdue_subtasks()}")
    
    # 하위 작업 완료
    subtask1.is_completed = True
    print(f"지연된 하위 작업 완료 후: {todo.has_overdue_subtasks()}")
    print()
    
    # 7. 완료 처리
    print("7. 완료 처리")
    print(f"완료 전 상태:")
    print(f"  할일 완료: {todo.is_completed()}")
    print(f"  하위 작업 1 완료: {subtask1.is_completed}")
    print(f"  하위 작업 2 완료: {subtask2.is_completed}")
    print(f"  긴급도: {todo.get_urgency_level()}")
    
    todo.mark_completed()
    print(f"\n완료 처리 후:")
    print(f"  할일 완료: {todo.is_completed()}")
    print(f"  하위 작업 1 완료: {subtask1.is_completed}")
    print(f"  하위 작업 2 완료: {subtask2.is_completed}")
    print(f"  긴급도: {todo.get_urgency_level()}")
    print(f"  시간 텍스트: {todo.get_time_remaining_text()}")
    print()
    
    # 8. 미완료 처리
    print("8. 미완료 처리")
    todo.mark_uncompleted()
    print(f"미완료 처리 후:")
    print(f"  할일 완료: {todo.is_completed()}")
    print(f"  하위 작업 1 완료: {subtask1.is_completed}")
    print(f"  하위 작업 2 완료: {subtask2.is_completed}")
    print(f"  긴급도: {todo.get_urgency_level()}")
    print()
    
    # 9. 직렬화/역직렬화
    print("9. 직렬화/역직렬화")
    todo_dict = todo.to_dict()
    print(f"직렬화된 목표 날짜: {todo_dict['due_date']}")
    print(f"직렬화된 완료 날짜: {todo_dict['completed_at']}")
    
    restored_todo = Todo.from_dict(todo_dict)
    print(f"복원된 목표 날짜: {restored_todo.get_due_date()}")
    print(f"복원된 긴급도: {restored_todo.get_urgency_level()}")
    print()
    
    print("=== 데모 완료 ===")


if __name__ == '__main__':
    demo_todo_due_date_methods()