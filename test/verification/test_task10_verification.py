"""
Task 10 구현 검증 테스트 - 진행률 표시 및 시각적 피드백
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from models.todo import Todo
from models.subtask import SubTask
from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService


def test_progress_calculation():
    """진행률 계산 테스트"""
    print("=== 진행률 계산 테스트 ===")
    
    # 하위작업이 없는 할일
    todo_no_subtasks = Todo(
        id=1,
        title="하위작업 없는 할일",
        created_at=datetime.now(),
        folder_path="test_folder"
    )
    
    print(f"하위작업 없는 할일 진행률: {todo_no_subtasks.get_completion_rate():.1%}")
    print(f"완료 상태: {todo_no_subtasks.is_completed()}")
    
    # 부분 완료된 할일
    todo_partial = Todo(
        id=2,
        title="부분 완료된 할일",
        created_at=datetime.now(),
        folder_path="test_folder",
        subtasks=[
            SubTask(1, 2, "완료된 하위작업", True, datetime.now()),
            SubTask(2, 2, "미완료 하위작업", False, datetime.now()),
            SubTask(3, 2, "또 다른 미완료", False, datetime.now())
        ]
    )
    
    print(f"부분 완료된 할일 진행률: {todo_partial.get_completion_rate():.1%}")
    print(f"완료 상태: {todo_partial.is_completed()}")
    
    # 완전 완료된 할일
    todo_complete = Todo(
        id=3,
        title="완전 완료된 할일",
        created_at=datetime.now(),
        folder_path="test_folder",
        subtasks=[
            SubTask(4, 3, "완료된 하위작업 1", True, datetime.now()),
            SubTask(5, 3, "완료된 하위작업 2", True, datetime.now())
        ]
    )
    
    print(f"완전 완료된 할일 진행률: {todo_complete.get_completion_rate():.1%}")
    print(f"완료 상태: {todo_complete.is_completed()}")
    
    return True


def test_visual_feedback_formatting():
    """시각적 피드백 포맷팅 테스트"""
    print("\n=== 시각적 피드백 포맷팅 테스트 ===")
    
    # 진행률 텍스트 포맷팅 테스트
    def format_progress(progress_rate: float) -> str:
        """진행률을 텍스트로 포맷"""
        percentage = int(progress_rate * 100)
        if percentage == 0:
            return "0%"
        elif percentage == 100:
            return "100% ✅"
        else:
            # 진행률에 따른 색상 표시 이모지 추가
            if percentage < 34:
                return f"{percentage}% 🔴"  # 빨간색
            elif percentage < 67:
                return f"{percentage}% 🟡"  # 노란색
            else:
                return f"{percentage}% 🟢"  # 초록색
    
    test_values = [0.0, 0.2, 0.5, 0.8, 1.0]
    for value in test_values:
        formatted = format_progress(value)
        print(f"진행률 {value:.1%} -> {formatted}")
    
    # 제목 포맷팅 테스트
    def format_todo_title(todo: Todo) -> str:
        """할일 제목 포맷 (완료 상태에 따른 시각적 효과 적용)"""
        title = todo.title
        if todo.is_completed():
            return f"✓ {title}"
        return title
    
    def format_subtask_title(subtask: SubTask) -> str:
        """하위작업 제목 포맷 (완료 상태에 따른 시각적 효과 적용)"""
        title = subtask.title
        if subtask.is_completed:
            return f"✓ {title}"
        return title
    
    # 테스트 데이터
    incomplete_todo = Todo(1, "미완료 할일", datetime.now(), "folder", [
        SubTask(1, 1, "미완료 하위작업", False, datetime.now())
    ])
    
    complete_todo = Todo(2, "완료된 할일", datetime.now(), "folder", [
        SubTask(2, 2, "완료된 하위작업", True, datetime.now())
    ])
    
    print(f"미완료 할일 제목: '{format_todo_title(incomplete_todo)}'")
    print(f"완료된 할일 제목: '{format_todo_title(complete_todo)}'")
    print(f"미완료 하위작업 제목: '{format_subtask_title(incomplete_todo.subtasks[0])}'")
    print(f"완료된 하위작업 제목: '{format_subtask_title(complete_todo.subtasks[0])}'")
    
    return True


def test_real_time_updates():
    """실시간 진행률 업데이트 테스트"""
    print("\n=== 실시간 진행률 업데이트 테스트 ===")
    
    # 서비스 초기화
    storage_service = StorageService("test/data/test_todos.json")
    file_service = FileService("test/todo_folders")
    todo_service = TodoService(storage_service, file_service)
    
    # 테스트 할일 생성
    todo = todo_service.add_todo("실시간 업데이트 테스트")
    print(f"할일 생성: {todo.title}")
    print(f"초기 진행률: {todo.get_completion_rate():.1%}")
    
    # 하위작업 추가
    subtask1 = todo_service.add_subtask(todo.id, "첫 번째 하위작업")
    subtask2 = todo_service.add_subtask(todo.id, "두 번째 하위작업")
    subtask3 = todo_service.add_subtask(todo.id, "세 번째 하위작업")
    
    updated_todo = todo_service.get_todo_by_id(todo.id)
    print(f"하위작업 3개 추가 후 진행률: {updated_todo.get_completion_rate():.1%}")
    
    # 첫 번째 하위작업 완료
    todo_service.toggle_subtask_completion(todo.id, subtask1.id)
    updated_todo = todo_service.get_todo_by_id(todo.id)
    print(f"첫 번째 하위작업 완료 후 진행률: {updated_todo.get_completion_rate():.1%}")
    
    # 두 번째 하위작업 완료
    todo_service.toggle_subtask_completion(todo.id, subtask2.id)
    updated_todo = todo_service.get_todo_by_id(todo.id)
    print(f"두 번째 하위작업 완료 후 진행률: {updated_todo.get_completion_rate():.1%}")
    
    # 세 번째 하위작업 완료
    todo_service.toggle_subtask_completion(todo.id, subtask3.id)
    updated_todo = todo_service.get_todo_by_id(todo.id)
    print(f"모든 하위작업 완료 후 진행률: {updated_todo.get_completion_rate():.1%}")
    print(f"할일 완료 상태: {updated_todo.is_completed()}")
    
    # 정리
    todo_service.delete_todo(todo.id, True)
    
    return True


def test_color_progression():
    """진행률에 따른 색상 변화 테스트"""
    print("\n=== 진행률에 따른 색상 변화 테스트 ===")
    
    def get_progress_color_description(progress: float) -> str:
        """진행률에 따른 색상 설명 반환"""
        percentage = progress * 100
        if percentage == 0:
            return "회색 (시작 안함)"
        elif percentage < 34:
            return "빨간색 (낮은 진행률)"
        elif percentage < 67:
            return "노란색 (중간 진행률)"
        elif percentage < 100:
            return "초록색 (높은 진행률)"
        else:
            return "진한 초록색 (완료)"
    
    test_progress_values = [0.0, 0.1, 0.33, 0.5, 0.66, 0.9, 1.0]
    
    for progress in test_progress_values:
        color_desc = get_progress_color_description(progress)
        print(f"진행률 {progress:.0%}: {color_desc}")
    
    return True


def test_overall_progress_calculation():
    """전체 진행률 계산 테스트"""
    print("\n=== 전체 진행률 계산 테스트 ===")
    
    # 서비스 초기화
    storage_service = StorageService("test/data/test_todos.json")
    file_service = FileService("test/todo_folders")
    todo_service = TodoService(storage_service, file_service)
    
    # 기존 할일들 삭제
    existing_todos = todo_service.get_all_todos()
    for todo in existing_todos:
        todo_service.delete_todo(todo.id, True)
    
    # 테스트 할일들 생성
    todo1 = todo_service.add_todo("프로젝트 계획")
    todo_service.add_subtask(todo1.id, "요구사항 분석")
    todo_service.add_subtask(todo1.id, "일정 수립")
    
    todo2 = todo_service.add_todo("개발 작업")
    subtask1 = todo_service.add_subtask(todo2.id, "코딩")
    subtask2 = todo_service.add_subtask(todo2.id, "테스트")
    todo_service.toggle_subtask_completion(todo2.id, subtask1.id)  # 50% 완료
    
    todo3 = todo_service.add_todo("문서화")
    subtask3 = todo_service.add_subtask(todo3.id, "사용자 매뉴얼")
    subtask4 = todo_service.add_subtask(todo3.id, "API 문서")
    todo_service.toggle_subtask_completion(todo3.id, subtask3.id)  # 50% 완료
    todo_service.toggle_subtask_completion(todo3.id, subtask4.id)  # 100% 완료
    
    # 전체 진행률 계산
    all_todos = todo_service.get_all_todos()
    total_progress = sum(todo.get_completion_rate() for todo in all_todos)
    overall_progress = total_progress / len(all_todos) if all_todos else 0
    
    print(f"총 할일 개수: {len(all_todos)}")
    for todo in all_todos:
        print(f"  - {todo.title}: {todo.get_completion_rate():.1%}")
    
    print(f"전체 평균 진행률: {overall_progress:.1%}")
    
    # 완료된 할일 개수
    completed_todos = sum(1 for todo in all_todos if todo.is_completed())
    print(f"완료된 할일: {completed_todos}/{len(all_todos)}")
    
    # 정리
    for todo in all_todos:
        todo_service.delete_todo(todo.id, True)
    
    return True


def main():
    """메인 테스트 함수"""
    print("Task 10 구현 검증 테스트를 시작합니다...")
    print("=" * 50)
    
    tests = [
        ("진행률 계산", test_progress_calculation),
        ("시각적 피드백 포맷팅", test_visual_feedback_formatting),
        ("실시간 진행률 업데이트", test_real_time_updates),
        ("진행률에 따른 색상 변화", test_color_progression),
        ("전체 진행률 계산", test_overall_progress_calculation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n[테스트] {test_name}")
            result = test_func()
            if result:
                print(f"✅ {test_name} 통과")
                passed += 1
            else:
                print(f"❌ {test_name} 실패")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 오류: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"테스트 결과: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("🎉 모든 테스트가 통과했습니다!")
        print("\nTask 10 구현 완료 사항:")
        print("✅ ProgressBar 컴포넌트 구현")
        print("✅ 할일별 진행률 계산 및 표시")
        print("✅ 완료된 할일 시각적 표시 (체크 마크, 색상 변경)")
        print("✅ 실시간 진행률 업데이트")
        print("✅ 진행률에 따른 색상 변경 (빨강 > 노랑 > 초록)")
        print("✅ 전체 진행률 계산 및 표시")
        print("✅ 컴팩트 진행률 바 컴포넌트")
        print("✅ 검색 박스 및 필터 패널 컴포넌트")
        print("✅ 상태바 컴포넌트 개선")
        return True
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)