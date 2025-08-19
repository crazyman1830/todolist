"""
TodoService 목표 날짜 관련 기능 데모

Task 5: TodoService에 목표 날짜 관련 비즈니스 로직 추가 데모
"""

import tempfile
import shutil
import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


def demo_todo_service_due_date():
    """TodoService 목표 날짜 기능 데모"""
    print("=== TodoService 목표 날짜 기능 데모 ===\n")
    
    # 임시 환경 설정
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, "demo_todos.json")
    todo_folders_dir = os.path.join(test_dir, "todo_folders")
    
    try:
        # 서비스 초기화
        storage_service = StorageService(data_file)
        file_service = FileService(todo_folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 1. 할일 생성 및 목표 날짜 설정
        print("1. 할일 생성 및 목표 날짜 설정")
        todo1 = todo_service.add_todo("프로젝트 문서 작성")
        todo2 = todo_service.add_todo("코드 리뷰")
        todo3 = todo_service.add_todo("테스트 작성")
        
        # 다양한 목표 날짜 설정
        due_date1 = datetime.now() + timedelta(days=3)
        due_date2 = datetime.now() + timedelta(hours=12)  # 긴급
        due_date3 = datetime.now() + timedelta(days=7)
        
        todo_service.set_todo_due_date(todo1.id, due_date1)
        todo_service.set_todo_due_date(todo2.id, due_date2)
        todo_service.set_todo_due_date(todo3.id, due_date3)
        
        print(f"- {todo1.title}: {due_date1.strftime('%Y-%m-%d %H:%M')}")
        print(f"- {todo2.title}: {due_date2.strftime('%Y-%m-%d %H:%M')}")
        print(f"- {todo3.title}: {due_date3.strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # 2. 하위 작업에 목표 날짜 설정
        print("2. 하위 작업에 목표 날짜 설정")
        subtask1 = todo_service.add_subtask(todo1.id, "요구사항 분석")
        subtask2 = todo_service.add_subtask(todo1.id, "설계 문서 작성")
        
        # 하위 작업 목표 날짜 (상위 할일보다 빠른 날짜)
        subtask_due_date1 = datetime.now() + timedelta(days=1)
        subtask_due_date2 = datetime.now() + timedelta(days=2)
        
        todo_service.set_subtask_due_date(todo1.id, subtask1.id, subtask_due_date1)
        todo_service.set_subtask_due_date(todo1.id, subtask2.id, subtask_due_date2)
        
        print(f"- {subtask1.title}: {subtask_due_date1.strftime('%Y-%m-%d %H:%M')}")
        print(f"- {subtask2.title}: {subtask_due_date2.strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # 3. 긴급한 할일 조회
        print("3. 긴급한 할일 조회 (24시간 이내)")
        urgent_todos = todo_service.get_urgent_todos(24)
        for todo in urgent_todos:
            updated_todo = todo_service.get_todo_by_id(todo.id)
            print(f"- {updated_todo.title}: {updated_todo.get_time_remaining_text()}")
        print()
        
        # 4. 목표 날짜순 정렬
        print("4. 목표 날짜순 정렬")
        all_todos = todo_service.get_all_todos()
        sorted_todos = todo_service.sort_todos_by_due_date(all_todos)
        
        for todo in sorted_todos:
            if todo.due_date:
                print(f"- {todo.title}: {todo.get_time_remaining_text()}")
        print()
        
        # 5. 통합 필터링 및 정렬
        print("5. 통합 필터링 및 정렬 (긴급한 할일, 목표 날짜순)")
        filtered_todos = todo_service.get_filtered_and_sorted_todos(
            filter_type="urgent", sort_by="due_date"
        )
        
        for todo in filtered_todos:
            print(f"- {todo.title}: {todo.get_urgency_level()} - {todo.get_time_remaining_text()}")
        print()
        
        # 6. 하위 작업 목표 날짜 유효성 검사 데모
        print("6. 하위 작업 목표 날짜 유효성 검사")
        try:
            # 상위 할일보다 늦은 날짜로 설정 시도
            invalid_date = datetime.now() + timedelta(days=5)  # todo1의 목표 날짜(3일 후)보다 늦음
            todo_service.set_subtask_due_date(todo1.id, subtask1.id, invalid_date)
        except ValueError as e:
            print(f"- 유효성 검사 오류: {e}")
        print()
        
        # 7. 목표 날짜 제거
        print("7. 목표 날짜 제거")
        todo_service.set_todo_due_date(todo3.id, None)
        updated_todo3 = todo_service.get_todo_by_id(todo3.id)
        print(f"- {updated_todo3.title}: 목표 날짜 {'있음' if updated_todo3.due_date else '없음'}")
        print()
        
        print("=== 데모 완료 ===")
        
        # 서비스 종료
        todo_service.shutdown()
        
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    demo_todo_service_due_date()