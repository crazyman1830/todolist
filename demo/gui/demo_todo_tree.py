"""
TodoTree 목표 날짜 표시 기능 데모

Requirements 2.1, 2.2, 3.1, 3.2, 3.3, 5.1, 5.2, 5.3 시연
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from unittest.mock import Mock

from gui.todo_tree import TodoTree
from services.todo_service import TodoService
from models.todo import Todo
from models.subtask import SubTask


def create_demo_data():
    """데모용 할일 데이터 생성"""
    now = datetime.now()
    
    # 다양한 긴급도의 할일들 생성
    todos = []
    
    # 1. 지연된 할일 (빨간색)
    overdue_todo = Todo(
        id=1,
        title="🔴 지연된 프로젝트 보고서 작성",
        created_at=now - timedelta(days=3),
        folder_path="test_folder_1",
        due_date=now - timedelta(hours=6),  # 6시간 전 마감
        subtasks=[]
    )
    todos.append(overdue_todo)
    
    # 2. 긴급한 할일 (주황색) - 24시간 이내
    urgent_todo = Todo(
        id=2,
        title="🟠 긴급 회의 준비",
        created_at=now - timedelta(hours=2),
        folder_path="test_folder_2",
        due_date=now + timedelta(hours=8),  # 8시간 후 마감
        subtasks=[]
    )
    todos.append(urgent_todo)
    
    # 3. 경고 할일 (노란색) - 3일 이내
    warning_todo = Todo(
        id=3,
        title="🟡 주간 계획 수립",
        created_at=now - timedelta(hours=1),
        folder_path="test_folder_3",
        due_date=now + timedelta(days=2, hours=12),  # 2.5일 후 마감
        subtasks=[]
    )
    todos.append(warning_todo)
    
    # 4. 일반 할일 (검은색)
    normal_todo = Todo(
        id=4,
        title="⚪ 월간 리뷰 작성",
        created_at=now - timedelta(hours=1),
        folder_path="test_folder_4",
        due_date=now + timedelta(days=10),  # 10일 후 마감
        subtasks=[]
    )
    todos.append(normal_todo)
    
    # 5. 목표 날짜가 없는 할일
    no_due_date_todo = Todo(
        id=5,
        title="📝 아이디어 정리 (목표 날짜 없음)",
        created_at=now - timedelta(hours=1),
        folder_path="test_folder_5",
        due_date=None,
        subtasks=[]
    )
    todos.append(no_due_date_todo)
    
    # 6. 완료된 할일 (회색)
    completed_todo = Todo(
        id=6,
        title="✅ 완료된 작업",
        created_at=now - timedelta(days=1),
        folder_path="test_folder_6",
        due_date=now - timedelta(hours=2),  # 2시간 전 마감이었지만 완료됨
        completed_at=now - timedelta(minutes=30),
        subtasks=[]
    )
    todos.append(completed_todo)
    
    # 7. 하위작업이 있는 할일 (다양한 긴급도의 하위작업들)
    subtask1 = SubTask(
        id=1,
        todo_id=7,
        title="🔴 지연된 하위작업",
        is_completed=False,
        due_date=now - timedelta(hours=2)  # 2시간 전 마감 (지연됨)
    )
    
    subtask2 = SubTask(
        id=2,
        todo_id=7,
        title="🟠 긴급한 하위작업",
        is_completed=False,
        due_date=now + timedelta(hours=4)  # 4시간 후 마감 (긴급)
    )
    
    subtask3 = SubTask(
        id=3,
        todo_id=7,
        title="✅ 완료된 하위작업",
        is_completed=True,
        due_date=now + timedelta(hours=12),  # 12시간 후 마감
        completed_at=now - timedelta(minutes=15)
    )
    
    subtask4 = SubTask(
        id=4,
        todo_id=7,
        title="⚪ 일반 하위작업",
        is_completed=False,
        due_date=now + timedelta(days=5)  # 5일 후 마감
    )
    
    todo_with_subtasks = Todo(
        id=7,
        title="📋 복합 프로젝트 (하위작업 포함)",
        created_at=now - timedelta(hours=3),
        folder_path="test_folder_7",
        due_date=now + timedelta(days=7),  # 7일 후 마감
        subtasks=[subtask1, subtask2, subtask3, subtask4]
    )
    todos.append(todo_with_subtasks)
    
    return todos


def main():
    """데모 실행"""
    # 메인 윈도우 생성
    root = tk.Tk()
    root.title("TodoTree 목표 날짜 표시 기능 데모")
    root.geometry("1000x600")
    
    # 설명 라벨
    info_frame = ttk.Frame(root)
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    info_label = ttk.Label(
        info_frame,
        text="목표 날짜 기반 긴급도 표시: 🔴 지연됨 | 🟠 긴급 (24시간 이내) | 🟡 경고 (3일 이내) | ⚪ 일반 | ✅ 완료됨",
        font=('TkDefaultFont', 9, 'bold')
    )
    info_label.pack()
    
    # TodoTree를 위한 프레임
    tree_frame = ttk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Mock TodoService 생성
    mock_todo_service = Mock(spec=TodoService)
    demo_todos = create_demo_data()
    mock_todo_service.get_all_todos.return_value = demo_todos
    
    # 개별 할일 조회를 위한 Mock 설정
    def get_todo_by_id(todo_id):
        for todo in demo_todos:
            if todo.id == todo_id:
                return todo
        return None
    
    def get_subtasks(todo_id):
        todo = get_todo_by_id(todo_id)
        return todo.subtasks if todo else []
    
    mock_todo_service.get_todo_by_id.side_effect = get_todo_by_id
    mock_todo_service.get_subtasks.side_effect = get_subtasks
    mock_todo_service.update_todo_expansion_state.return_value = True
    mock_todo_service.set_todo_due_date.return_value = True
    mock_todo_service.set_subtask_due_date.return_value = True
    
    # TodoTree 생성
    todo_tree = TodoTree(tree_frame, mock_todo_service)
    
    # 컨트롤 버튼들
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def refresh_tree():
        """트리 새로고침"""
        todo_tree.refresh_tree()
    
    def expand_all():
        """모든 노드 확장"""
        todo_tree.expand_all()
    
    def collapse_all():
        """모든 노드 축소"""
        todo_tree.collapse_all()
    
    ttk.Button(control_frame, text="새로고침", command=refresh_tree).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="모두 확장", command=expand_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="모두 축소", command=collapse_all).pack(side=tk.LEFT, padx=5)
    
    # 사용법 안내
    usage_frame = ttk.Frame(root)
    usage_frame.pack(fill=tk.X, padx=10, pady=5)
    
    usage_text = """
사용법:
• 우클릭으로 컨텍스트 메뉴 열기 (목표 날짜 설정/제거 옵션 포함)
• 목표 날짜 컬럼에서 남은 시간/지연 시간 확인
• 긴급도에 따른 색상 구분 확인
• 하위작업의 개별 목표 날짜 관리
    """
    
    usage_label = ttk.Label(usage_frame, text=usage_text, justify=tk.LEFT)
    usage_label.pack(anchor=tk.W)
    
    # 초기 트리 로드
    todo_tree.refresh_tree()
    
    # 메인 루프 실행
    root.mainloop()


if __name__ == "__main__":
    main()