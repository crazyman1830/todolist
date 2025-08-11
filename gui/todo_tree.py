import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Any
from datetime import datetime
from services.todo_service import TodoService
from models.todo import Todo
from models.subtask import SubTask
from gui.components import CompactProgressBar


class TodoTree(ttk.Treeview):
    """할일 트리 뷰 컴포넌트 - 할일과 하위작업을 계층적으로 표시"""
    
    def __init__(self, parent, todo_service: TodoService, **kwargs):
        super().__init__(parent, **kwargs)
        self.todo_service = todo_service
        self.parent = parent
        
        # 트리 노드 ID와 데이터 매핑을 위한 딕셔너리
        self.todo_nodes: Dict[int, str] = {}  # todo_id -> tree_item_id
        self.subtask_nodes: Dict[int, str] = {}  # subtask_id -> tree_item_id
        self.node_data: Dict[str, Dict[str, Any]] = {}  # tree_item_id -> data
        
        # 트리 설정
        self.setup_tree()
        self.setup_columns()
        self.setup_context_menu()
        self.setup_events()
        self._setup_visual_styles()
        
        # 초기 데이터 로드
        self.refresh_tree()
    
    def setup_tree(self) -> None:
        """트리 구조 기본 설정"""
        # 트리 스타일 설정
        self.configure(
            show='tree headings',  # 트리와 헤더 모두 표시
            selectmode='extended'  # 다중 선택 가능
        )
        
        # 스크롤바 설정
        self.scrollbar_v = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.yview)
        self.scrollbar_h = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        
        # 스크롤바 배치
        self.scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_columns(self) -> None:
        """컬럼 설정 (제목, 진행률, 생성일)"""
        # 컬럼 정의
        self['columns'] = ('progress', 'created_at')
        
        # 트리 컬럼 (제목) 설정
        self.column('#0', width=350, minwidth=250, anchor='w')
        self.heading('#0', text='제목', anchor='w')
        
        # 진행률 컬럼 설정 (더 넓게 설정하여 진행률 바 표시)
        self.column('progress', width=120, minwidth=100, anchor='center')
        self.heading('progress', text='진행률', anchor='center')
        
        # 생성일 컬럼 설정
        self.column('created_at', width=150, minwidth=120, anchor='center')
        self.heading('created_at', text='생성일', anchor='center')
        
        # 진행률 바 위젯들을 저장할 딕셔너리
        self.progress_widgets: Dict[str, CompactProgressBar] = {}
    
    def setup_context_menu(self) -> None:
        """우클릭 컨텍스트 메뉴 설정"""
        # 할일용 컨텍스트 메뉴
        self.todo_context_menu = tk.Menu(self, tearoff=0)
        self.todo_context_menu.add_command(label="할일 수정 (F2)", command=self.on_edit_todo)
        self.todo_context_menu.add_command(label="할일 삭제 (Del)", command=self.on_delete_todo)
        self.todo_context_menu.add_separator()
        self.todo_context_menu.add_command(label="하위작업 추가 (Ctrl+Shift+N)", command=self.on_add_subtask)
        self.todo_context_menu.add_separator()
        self.todo_context_menu.add_command(label="폴더 열기", command=self.on_open_folder)
        self.todo_context_menu.add_separator()
        self.todo_context_menu.add_command(label="모두 확장", command=self.expand_all)
        self.todo_context_menu.add_command(label="모두 축소", command=self.collapse_all)
        
        # 하위작업용 컨텍스트 메뉴
        self.subtask_context_menu = tk.Menu(self, tearoff=0)
        self.subtask_context_menu.add_command(label="하위작업 수정 (F2)", command=self.on_edit_subtask)
        self.subtask_context_menu.add_command(label="하위작업 삭제 (Del)", command=self.on_delete_subtask)
        self.subtask_context_menu.add_separator()
        self.subtask_context_menu.add_command(label="완료 상태 토글 (Space)", command=self.on_toggle_subtask_from_menu)
        self.subtask_context_menu.add_separator()
        self.subtask_context_menu.add_command(label="폴더 열기", command=self.on_open_folder)
        
        # 빈 공간용 컨텍스트 메뉴
        self.empty_context_menu = tk.Menu(self, tearoff=0)
        self.empty_context_menu.add_command(label="새 할일 추가 (Ctrl+N)", command=self.on_add_new_todo)
        self.empty_context_menu.add_separator()
        self.empty_context_menu.add_command(label="새로고침 (F5)", command=self.refresh_tree)
        self.empty_context_menu.add_separator()
        self.empty_context_menu.add_command(label="모두 확장", command=self.expand_all)
        self.empty_context_menu.add_command(label="모두 축소", command=self.collapse_all)
    
    def setup_events(self) -> None:
        """이벤트 바인딩 설정"""
        # 마우스 이벤트
        self.bind('<Button-1>', self.on_single_click)
        self.bind('<Double-1>', self.on_double_click)
        self.bind('<Button-3>', self.on_right_click)
        
        # 키보드 이벤트
        self.bind('<Return>', self.on_enter_key)
        self.bind('<Delete>', self.on_delete_key)
        self.bind('<F2>', self.on_f2_key)
        self.bind('<space>', self.on_space_key)  # 스페이스바로 체크박스 토글
        
        # 트리 확장/축소 이벤트
        self.bind('<<TreeviewOpen>>', self.on_tree_open)
        self.bind('<<TreeviewClose>>', self.on_tree_close)
        
        # 체크박스 토글을 위한 가상 이벤트
        self.bind('<<CheckboxToggle>>', self.on_checkbox_toggle)
        
        # 키보드 네비게이션
        self.bind('<Up>', self.handle_key_navigation)
        self.bind('<Down>', self.handle_key_navigation)
        self.bind('<Left>', self.handle_key_navigation)
        self.bind('<Right>', self.handle_key_navigation)
        
        # 할일 순서 변경 이벤트
        self.bind('<<TodoReordered>>', self.on_todo_reordered)
        
        # 드래그 앤 드롭 이벤트
        self.bind('<Button1-Motion>', self.on_drag_motion)
        self.bind('<ButtonRelease-1>', self.on_drag_release)
        self.bind('<B1-Motion>', self.on_drag_motion)
        
        # 드래그 상태 추적
        self._drag_data = {
            'item': None, 
            'start_y': 0, 
            'start_x': 0,
            'is_dragging': False,
            'drag_threshold': 5  # 드래그 시작을 위한 최소 이동 거리
        }
    
    def refresh_tree(self) -> None:
        """트리 데이터 새로고침"""
        # 기존 진행률 위젯들 제거
        for widget in self.progress_widgets.values():
            try:
                widget.destroy()
            except:
                pass
        self.progress_widgets.clear()
        
        # 기존 데이터 클리어
        self.delete(*self.get_children())
        self.todo_nodes.clear()
        self.subtask_nodes.clear()
        self.node_data.clear()
        
        # 새 데이터 로드
        todos = self.todo_service.get_all_todos()
        self.populate_tree(todos)
    
    def populate_tree(self, todos: List[Todo]) -> None:
        """Todo 리스트를 트리로 변환하여 표시"""
        # 기존 진행률 위젯들 제거
        for widget in self.progress_widgets.values():
            try:
                widget.destroy()
            except:
                pass
        self.progress_widgets.clear()
        
        # 기존 데이터 클리어
        self.delete(*self.get_children())
        self.todo_nodes.clear()
        self.subtask_nodes.clear()
        self.node_data.clear()
        
        # 새 데이터 추가
        for todo in todos:
            node_id = self.add_todo_node(todo)
            # 확장 상태 복원
            self.item(node_id, open=todo.is_expanded)
    
    def add_todo_node(self, todo: Todo) -> str:
        """할일 노드를 트리에 추가"""
        # 완료 상태에 따른 아이콘 선택
        icon = self._get_todo_icon(todo)
        
        # 진행률 계산
        progress_rate = todo.get_completion_rate()
        progress_text = self._format_progress(progress_rate)
        
        # 생성일 포맷
        created_text = todo.created_at.strftime('%Y-%m-%d %H:%M')
        
        # 완료된 할일의 경우 제목에 시각적 효과 적용
        title_text = self._format_todo_title(todo)
        
        # 트리 노드 추가
        node_id = self.insert(
            '',  # 부모 (루트)
            'end',
            text=f"{icon} {title_text}",
            values=(progress_text, created_text),
            open=todo.is_expanded,
            tags=('todo_completed' if todo.is_completed() else 'todo_incomplete',)
        )
        
        # 매핑 정보 저장
        self.todo_nodes[todo.id] = node_id
        self.node_data[node_id] = {
            'type': 'todo',
            'todo_id': todo.id,
            'data': todo
        }
        
        # 진행률 바 위젯 생성 (하위작업이 있는 경우만)
        if todo.subtasks:
            self._create_progress_widget(node_id, progress_rate)
        
        # 하위작업 추가
        for subtask in todo.subtasks:
            self.add_subtask_node(node_id, subtask)
        
        # 완료된 할일에 대한 시각적 스타일 적용
        self._apply_completion_style(node_id, todo.is_completed())
        
        return node_id
    
    def add_subtask_node(self, parent_id: str, subtask: SubTask) -> str:
        """하위작업 노드를 트리에 추가"""
        # 완료 상태에 따른 아이콘 선택
        icon = self._get_subtask_icon(subtask)
        
        # 하위작업은 진행률 대신 완료 상태 표시
        status_text = "완료" if subtask.is_completed else "진행중"
        
        # 생성일 포맷
        created_text = subtask.created_at.strftime('%Y-%m-%d %H:%M')
        
        # 완료된 하위작업의 경우 제목에 시각적 효과 적용
        title_text = self._format_subtask_title(subtask)
        
        # 트리 노드 추가
        node_id = self.insert(
            parent_id,
            'end',
            text=f"  {icon} {title_text}",  # 들여쓰기로 계층 표현
            values=(status_text, created_text),
            tags=('subtask_completed' if subtask.is_completed else 'subtask_incomplete',)
        )
        
        # 매핑 정보 저장
        self.subtask_nodes[subtask.id] = node_id
        self.node_data[node_id] = {
            'type': 'subtask',
            'subtask_id': subtask.id,
            'todo_id': subtask.todo_id,
            'data': subtask
        }
        
        # 완료된 하위작업에 대한 시각적 스타일 적용
        self._apply_completion_style(node_id, subtask.is_completed)
        
        return node_id
    
    def update_todo_node(self, todo: Todo) -> None:
        """할일 노드 업데이트"""
        if todo.id not in self.todo_nodes:
            return
        
        node_id = self.todo_nodes[todo.id]
        
        # 아이콘과 텍스트 업데이트
        icon = self._get_todo_icon(todo)
        title_text = self._format_todo_title(todo)
        
        # 진행률 업데이트
        progress_rate = todo.get_completion_rate()
        progress_text = self._format_progress(progress_rate)
        
        # 노드 업데이트
        self.item(node_id, 
                 text=f"{icon} {title_text}", 
                 values=(progress_text, self.item(node_id)['values'][1]),
                 tags=('todo_completed' if todo.is_completed() else 'todo_incomplete',))
        
        # 진행률 바 위젯 업데이트
        if todo.subtasks:
            self._update_progress_widget(node_id, progress_rate)
        
        # 완료 상태에 따른 시각적 스타일 적용
        self._apply_completion_style(node_id, todo.is_completed())
        
        # 데이터 업데이트
        self.node_data[node_id]['data'] = todo
    
    def update_subtask_node(self, subtask: SubTask) -> None:
        """하위작업 노드 업데이트"""
        if subtask.id not in self.subtask_nodes:
            return
        
        node_id = self.subtask_nodes[subtask.id]
        
        # 아이콘과 텍스트 업데이트
        icon = self._get_subtask_icon(subtask)
        title_text = self._format_subtask_title(subtask)
        
        # 상태 업데이트
        status_text = "완료" if subtask.is_completed else "진행중"
        
        # 노드 업데이트
        self.item(node_id, 
                 text=f"  {icon} {title_text}", 
                 values=(status_text, self.item(node_id)['values'][1]),
                 tags=('subtask_completed' if subtask.is_completed else 'subtask_incomplete',))
        
        # 완료 상태에 따른 시각적 스타일 적용
        self._apply_completion_style(node_id, subtask.is_completed)
        
        # 데이터 업데이트
        self.node_data[node_id]['data'] = subtask
    
    def remove_todo_node(self, todo_id: int) -> None:
        """할일 노드 제거"""
        if todo_id not in self.todo_nodes:
            return
        
        node_id = self.todo_nodes[todo_id]
        
        # 진행률 위젯 제거
        if node_id in self.progress_widgets:
            try:
                self.progress_widgets[node_id].destroy()
                del self.progress_widgets[node_id]
            except:
                pass
        
        # 하위작업 노드들도 매핑에서 제거
        todo = self.node_data[node_id]['data']
        for subtask in todo.subtasks:
            if subtask.id in self.subtask_nodes:
                subtask_node_id = self.subtask_nodes[subtask.id]
                del self.subtask_nodes[subtask.id]
                if subtask_node_id in self.node_data:
                    del self.node_data[subtask_node_id]
        
        # 트리에서 노드 제거
        self.delete(node_id)
        
        # 매핑에서 제거
        del self.todo_nodes[todo_id]
        if node_id in self.node_data:
            del self.node_data[node_id]
    
    def remove_subtask_node(self, subtask_id: int) -> None:
        """하위작업 노드 제거"""
        if subtask_id not in self.subtask_nodes:
            return
        
        node_id = self.subtask_nodes[subtask_id]
        
        # 트리에서 노드 제거
        self.delete(node_id)
        
        # 매핑에서 제거
        del self.subtask_nodes[subtask_id]
        if node_id in self.node_data:
            del self.node_data[node_id]
    
    def _get_todo_icon(self, todo: Todo) -> str:
        """할일의 완료 상태에 따른 아이콘 반환"""
        if todo.is_completed():
            return "✅"  # 완료된 할일
        elif todo.subtasks and todo.get_completion_rate() > 0:
            return "🔄"  # 진행 중인 할일
        elif todo.subtasks:
            return "📋"  # 하위작업이 있는 할일
        else:
            return "📝"  # 일반 할일
    
    def _get_subtask_icon(self, subtask: SubTask) -> str:
        """하위작업의 완료 상태에 따른 아이콘 반환"""
        return "☑️" if subtask.is_completed else "☐"
    
    def _format_progress(self, progress_rate: float) -> str:
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
    
    def _format_todo_title(self, todo: Todo) -> str:
        """할일 제목 포맷 (완료 상태에 따른 시각적 효과 적용)"""
        title = todo.title
        if todo.is_completed():
            return f"✓ {title}"
        return title
    
    def _format_subtask_title(self, subtask: SubTask) -> str:
        """하위작업 제목 포맷 (완료 상태에 따른 시각적 효과 적용)"""
        title = subtask.title
        if subtask.is_completed:
            return f"✓ {title}"
        return title
    
    def _create_progress_widget(self, node_id: str, progress: float) -> None:
        """진행률 바 위젯 생성"""
        try:
            # 진행률 바 위젯 생성
            progress_widget = CompactProgressBar(self, progress=progress, width=80, height=14)
            
            # 위젯을 트리뷰에 배치 (진행률 컬럼에)
            bbox = self.bbox(node_id, 'progress')
            if bbox:
                x, y, width, height = bbox
                # 위젯을 적절한 위치에 배치
                progress_widget.place(x=x + 10, y=y + 2)
                
                # 위젯 참조 저장
                self.progress_widgets[node_id] = progress_widget
        except Exception as e:
            # 위젯 생성 실패 시 로그 출력 (선택사항)
            print(f"진행률 위젯 생성 실패: {e}")
    
    def _update_progress_widget(self, node_id: str, progress: float) -> None:
        """진행률 바 위젯 업데이트"""
        if node_id in self.progress_widgets:
            try:
                self.progress_widgets[node_id].update_progress(progress)
            except Exception as e:
                print(f"진행률 위젯 업데이트 실패: {e}")
        else:
            # 위젯이 없으면 새로 생성
            self._create_progress_widget(node_id, progress)
    
    def _apply_completion_style(self, node_id: str, is_completed: bool) -> None:
        """완료 상태에 따른 시각적 스타일 적용"""
        try:
            if is_completed:
                # 완료된 항목의 텍스트 색상을 회색으로 변경
                self.item(node_id, tags=('completed',))
            else:
                # 미완료 항목의 기본 스타일
                self.item(node_id, tags=('incomplete',))
        except Exception as e:
            print(f"스타일 적용 실패: {e}")
    
    def _setup_visual_styles(self) -> None:
        """시각적 스타일 설정"""
        # 완료된 항목에 대한 스타일
        self.tag_configure('completed', foreground='gray')
        self.tag_configure('todo_completed', foreground='gray')
        self.tag_configure('subtask_completed', foreground='gray')
        
        # 미완료 항목에 대한 스타일
        self.tag_configure('incomplete', foreground='black')
        self.tag_configure('todo_incomplete', foreground='black')
        self.tag_configure('subtask_incomplete', foreground='black')
    
    # 이벤트 핸들러들
    def on_single_click(self, event) -> None:
        """단일 클릭 이벤트 처리"""
        item_id = self.identify_row(event.y)
        
        # 드래그 시작 위치 저장
        self._drag_data['start_x'] = event.x
        self._drag_data['start_y'] = event.y
        self._drag_data['item'] = item_id
        self._drag_data['is_dragging'] = False
        
        if not item_id:
            return
        
        # 체크박스 영역 클릭 감지 (아이콘 부분)
        region = self.identify_region(event.x, event.y)
        if region == 'tree':
            try:
                # 아이콘 영역 클릭 시 체크박스 토글
                bbox = self.bbox(item_id, '#0')
                if bbox:
                    x_offset = event.x - bbox[0]
                    # 아이콘 영역 클릭 감지 (들여쓰기 고려)
                    if item_id in self.node_data:
                        node_data = self.node_data[item_id]
                        if node_data['type'] == 'subtask':
                            # 하위작업의 경우 들여쓰기를 고려한 아이콘 영역
                            if 20 <= x_offset <= 50:  # 하위작업 아이콘 영역
                                self.event_generate('<<CheckboxToggle>>', x=event.x, y=event.y)
                        elif node_data['type'] == 'todo':
                            # 할일의 경우 직접적인 아이콘 영역
                            if x_offset <= 30:  # 할일 아이콘 영역
                                # 할일은 체크박스 토글이 아닌 확장/축소만 처리
                                pass
            except (tk.TclError, KeyError):
                # bbox 계산 실패 시 무시
                pass
    
    def on_double_click(self, event) -> None:
        """더블 클릭 이벤트 처리 - 할일/하위작업 수정"""
        item_id = self.identify_row(event.y)
        if not item_id or item_id not in self.node_data:
            return
        
        node_data = self.node_data[item_id]
        if node_data['type'] == 'todo':
            self.on_edit_todo()
        elif node_data['type'] == 'subtask':
            self.on_edit_subtask()
    
    def on_right_click(self, event) -> None:
        """우클릭 이벤트 처리 - 컨텍스트 메뉴 표시"""
        item_id = self.identify_row(event.y)
        
        if item_id and item_id in self.node_data:
            # 항목 선택
            self.selection_set(item_id)
            
            # 노드 타입에 따라 적절한 컨텍스트 메뉴 표시
            node_data = self.node_data[item_id]
            if node_data['type'] == 'todo':
                self.todo_context_menu.post(event.x_root, event.y_root)
            elif node_data['type'] == 'subtask':
                self.subtask_context_menu.post(event.x_root, event.y_root)
        else:
            # 빈 공간 클릭 시
            self.selection_set('')  # 선택 해제
            self.empty_context_menu.post(event.x_root, event.y_root)
    
    def on_enter_key(self, event) -> None:
        """Enter 키 이벤트 처리"""
        self.on_edit_todo()
    
    def on_delete_key(self, event) -> None:
        """Delete 키 이벤트 처리"""
        self.on_delete_todo()
    
    def on_f2_key(self, event) -> None:
        """F2 키 이벤트 처리"""
        self.on_edit_todo()
    
    def on_space_key(self, event) -> None:
        """스페이스 키 이벤트 처리 - 하위작업 체크박스 토글"""
        selection = self.selection()
        if not selection:
            return
        
        item_id = selection[0]
        if item_id in self.node_data and self.node_data[item_id]['type'] == 'subtask':
            # 가상 이벤트 생성하여 체크박스 토글
            self.event_generate('<<CheckboxToggle>>', x=0, y=self.bbox(item_id)[1] if self.bbox(item_id) else 0)
    
    def on_drag_motion(self, event) -> None:
        """드래그 모션 이벤트 처리"""
        if not self._drag_data['item']:
            return
        
        # 드래그 시작 여부 확인
        dx = abs(event.x - self._drag_data['start_x'])
        dy = abs(event.y - self._drag_data['start_y'])
        
        if not self._drag_data['is_dragging']:
            # 드래그 임계값 확인
            if dx > self._drag_data['drag_threshold'] or dy > self._drag_data['drag_threshold']:
                self._drag_data['is_dragging'] = True
                self._start_drag_visual_feedback()
        
        if self._drag_data['is_dragging']:
            # 드래그 중인 항목의 시각적 피드백
            self._update_drag_visual_feedback(event)
    
    def on_drag_release(self, event) -> None:
        """드래그 릴리스 이벤트 처리"""
        if self._drag_data['is_dragging']:
            self._handle_drop(event)
            self._end_drag_visual_feedback()
        
        # 드래그 데이터 초기화
        self._drag_data = {
            'item': None, 
            'start_y': 0, 
            'start_x': 0,
            'is_dragging': False,
            'drag_threshold': 5
        }
    
    def _start_drag_visual_feedback(self) -> None:
        """드래그 시작 시 시각적 피드백"""
        if self._drag_data['item']:
            # 드래그 중인 항목을 하이라이트
            self.configure(cursor="hand2")
    
    def _update_drag_visual_feedback(self, event) -> None:
        """드래그 중 시각적 피드백 업데이트"""
        # 드롭 가능한 위치 표시
        target_item = self.identify_row(event.y)
        if target_item and target_item != self._drag_data['item']:
            # 드롭 대상 하이라이트 (선택사항)
            pass
    
    def _end_drag_visual_feedback(self) -> None:
        """드래그 종료 시 시각적 피드백 정리"""
        self.configure(cursor="")
    
    def _handle_drop(self, event) -> None:
        """드롭 처리"""
        source_item = self._drag_data['item']
        target_item = self.identify_row(event.y)
        
        if not source_item or not target_item or source_item == target_item:
            return
        
        # 드래그 앤 드롭 로직 (할일 순서 변경)
        if source_item in self.node_data and target_item in self.node_data:
            source_data = self.node_data[source_item]
            target_data = self.node_data[target_item]
            
            # 할일끼리만 순서 변경 가능
            if source_data['type'] == 'todo' and target_data['type'] == 'todo':
                self._reorder_todos(source_data['todo_id'], target_data['todo_id'], event.y)
    
    def _reorder_todos(self, source_todo_id: int, target_todo_id: int, drop_y: int) -> None:
        """할일 순서 변경"""
        try:
            # 현재는 기본적인 순서 변경만 구현 (실제 데이터 순서는 변경하지 않음)
            # 향후 TodoService에 순서 변경 메서드가 추가되면 연동
            
            # 시각적 피드백만 제공
            source_todo = self.todo_service.get_todo_by_id(source_todo_id)
            target_todo = self.todo_service.get_todo_by_id(target_todo_id)
            
            if source_todo and target_todo:
                # 트리 새로고침으로 순서 복원 (실제 순서 변경은 구현되지 않음)
                self.refresh_tree()
                
                # 상태 메시지 표시 (메인 윈도우에서 처리하도록 이벤트 생성)
                self.event_generate('<<TodoReordered>>')
        except Exception as e:
            print(f"할일 순서 변경 중 오류: {e}")
    
    def on_todo_reordered(self, event) -> None:
        """할일 순서 변경 이벤트 처리"""
        # 메인 윈도우에서 구현
        pass
    
    def on_tree_open(self, event) -> None:
        """트리 노드 확장 이벤트 처리"""
        item_id = self.selection()[0] if self.selection() else None
        if item_id and item_id in self.node_data:
            node_data = self.node_data[item_id]
            if node_data['type'] == 'todo':
                todo = node_data['data']
                todo.is_expanded = True
                # 확장 상태를 서비스를 통해 저장
                self.todo_service.update_todo_expansion_state(todo.id, True)
    
    def on_tree_close(self, event) -> None:
        """트리 노드 축소 이벤트 처리"""
        item_id = self.selection()[0] if self.selection() else None
        if item_id and item_id in self.node_data:
            node_data = self.node_data[item_id]
            if node_data['type'] == 'todo':
                todo = node_data['data']
                todo.is_expanded = False
                # 축소 상태를 서비스를 통해 저장
                self.todo_service.update_todo_expansion_state(todo.id, False)
    
    def on_checkbox_toggle(self, event) -> None:
        """체크박스 토글 이벤트 처리 (가상 이벤트)"""
        item_id = self.identify_row(event.y)
        if not item_id or item_id not in self.node_data:
            return
        
        node_data = self.node_data[item_id]
        
        if node_data['type'] == 'subtask':
            try:
                # 하위작업 완료 상태 토글
                subtask = node_data['data']
                success = self.todo_service.toggle_subtask_completion(subtask.todo_id, subtask.id)
                if success:
                    # 하위작업 노드 업데이트
                    updated_subtasks = self.todo_service.get_subtasks(subtask.todo_id)
                    for st in updated_subtasks:
                        if st.id == subtask.id:
                            self.update_subtask_node(st)
                            break
                    
                    # 상위 할일 노드도 업데이트 (진행률 변경)
                    todo = self.todo_service.get_todo_by_id(subtask.todo_id)
                    if todo:
                        self.update_todo_node(todo)
                        
                    # 상태 변경 성공 시 시각적 피드백 (선택사항)
                    self.selection_set(item_id)
                else:
                    # 토글 실패 시 사용자에게 알림 (선택사항)
                    print(f"하위작업 상태 변경에 실패했습니다: {subtask.title}")
                    
            except Exception as e:
                # 예외 발생 시 로그 출력
                print(f"체크박스 토글 중 오류 발생: {e}")
        elif node_data['type'] == 'todo':
            # 할일 노드의 경우 체크박스 토글이 아닌 확장/축소 처리
            # (이 부분은 트리뷰의 기본 동작에 맡김)
            pass
    
    # 유틸리티 메서드들
    def get_selected_todo_id(self) -> Optional[int]:
        """선택된 할일의 ID 반환"""
        selection = self.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        if item_id not in self.node_data:
            return None
        
        node_data = self.node_data[item_id]
        if node_data['type'] == 'todo':
            return node_data['todo_id']
        elif node_data['type'] == 'subtask':
            return node_data['todo_id']
        
        return None
    
    def get_selected_subtask_id(self) -> Optional[int]:
        """선택된 하위작업의 ID 반환"""
        selection = self.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        if item_id not in self.node_data:
            return None
        
        node_data = self.node_data[item_id]
        if node_data['type'] == 'subtask':
            return node_data['subtask_id']
        
        return None
    
    def get_selected_node_type(self) -> Optional[str]:
        """선택된 노드의 타입 반환 ('todo' 또는 'subtask')"""
        selection = self.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        if item_id not in self.node_data:
            return None
        
        return self.node_data[item_id]['type']
    
    def expand_all(self) -> None:
        """모든 트리 노드 확장"""
        def expand_recursive(item_id):
            self.item(item_id, open=True)
            # 해당 노드가 할일 노드인 경우 상태 저장
            if item_id in self.node_data and self.node_data[item_id]['type'] == 'todo':
                todo_id = self.node_data[item_id]['todo_id']
                self.todo_service.update_todo_expansion_state(todo_id, True)
            
            for child in self.get_children(item_id):
                expand_recursive(child)
        
        for item_id in self.get_children():
            expand_recursive(item_id)
    
    def collapse_all(self) -> None:
        """모든 트리 노드 축소"""
        def collapse_recursive(item_id):
            self.item(item_id, open=False)
            # 해당 노드가 할일 노드인 경우 상태 저장
            if item_id in self.node_data and self.node_data[item_id]['type'] == 'todo':
                todo_id = self.node_data[item_id]['todo_id']
                self.todo_service.update_todo_expansion_state(todo_id, False)
            
            for child in self.get_children(item_id):
                collapse_recursive(child)
        
        for item_id in self.get_children():
            collapse_recursive(item_id)
    
    # 외부에서 호출할 이벤트 핸들러들 (실제 구현은 메인 윈도우에서)
    def on_edit_todo(self) -> None:
        """할일 수정 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_edit_todo_callback') and self._on_edit_todo_callback:
            self._on_edit_todo_callback()
    
    def on_delete_todo(self) -> None:
        """할일 삭제 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_delete_todo_callback') and self._on_delete_todo_callback:
            self._on_delete_todo_callback()
    
    def on_add_subtask(self) -> None:
        """하위작업 추가 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_add_subtask_callback') and self._on_add_subtask_callback:
            self._on_add_subtask_callback()
    
    def on_edit_subtask(self) -> None:
        """하위작업 수정 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_edit_subtask_callback') and self._on_edit_subtask_callback:
            self._on_edit_subtask_callback()
    
    def on_delete_subtask(self) -> None:
        """하위작업 삭제 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_delete_subtask_callback') and self._on_delete_subtask_callback:
            self._on_delete_subtask_callback()
    
    def on_open_folder(self) -> None:
        """폴더 열기 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_open_folder_callback') and self._on_open_folder_callback:
            self._on_open_folder_callback()
    
    def on_add_new_todo(self) -> None:
        """새 할일 추가 - 메인 윈도우에서 구현"""
        if hasattr(self, '_on_add_new_todo_callback') and self._on_add_new_todo_callback:
            self._on_add_new_todo_callback()
    
    def on_toggle_subtask_from_menu(self) -> None:
        """메뉴에서 하위작업 토글"""
        selection = self.selection()
        if selection:
            item_id = selection[0]
            if item_id in self.node_data and self.node_data[item_id]['type'] == 'subtask':
                # 가상 이벤트 생성하여 체크박스 토글
                bbox = self.bbox(item_id)
                if bbox:
                    self.event_generate('<<CheckboxToggle>>', x=0, y=bbox[1])
    
    def handle_key_navigation(self, event) -> None:
        """키보드 네비게이션 처리"""
        selection = self.selection()
        if not selection:
            return
        
        current_item = selection[0]
        
        if event.keysym == 'Up':
            # 이전 항목으로 이동
            prev_item = self.prev(current_item)
            if prev_item:
                self.selection_set(prev_item)
                self.see(prev_item)
        elif event.keysym == 'Down':
            # 다음 항목으로 이동
            next_item = self.next(current_item)
            if next_item:
                self.selection_set(next_item)
                self.see(next_item)
        elif event.keysym == 'Left':
            # 노드 축소
            if self.item(current_item, 'open'):
                self.item(current_item, open=False)
        elif event.keysym == 'Right':
            # 노드 확장
            if not self.item(current_item, 'open'):
                self.item(current_item, open=True)
    
    def save_expansion_states(self) -> None:
        """현재 모든 노드의 확장 상태를 저장"""
        for item_id in self.get_children():
            if item_id in self.node_data and self.node_data[item_id]['type'] == 'todo':
                todo_id = self.node_data[item_id]['todo_id']
                is_expanded = self.item(item_id, 'open')
                self.todo_service.update_todo_expansion_state(todo_id, is_expanded)
    
    def restore_expansion_states(self) -> None:
        """저장된 확장 상태를 복원"""
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            if todo.id in self.todo_nodes:
                node_id = self.todo_nodes[todo.id]
                self.item(node_id, open=todo.is_expanded)