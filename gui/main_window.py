import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Optional
from services.todo_service import TodoService
from services.notification_service import NotificationService
from gui.todo_tree import TodoTree
from gui.components import StatusBar, SearchBox, FilterPanel, ProgressBar
from gui.dialogs import (
    show_add_todo_dialog, show_edit_todo_dialog, show_add_subtask_dialog,
    show_add_todo_dialog_with_due_date, show_edit_todo_dialog_with_due_date, 
    show_add_subtask_dialog_with_due_date,
    show_delete_confirm_dialog, show_folder_delete_confirm_dialog,
    show_error_dialog, show_info_dialog, show_folder_error_dialog,
    show_startup_notification_dialog
)


class MainWindow:
    """메인 윈도우 클래스 - GUI 할일 관리자의 주요 인터페이스"""
    
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service
        self.notification_service = NotificationService(todo_service)
        self.root = tk.Tk()
        self.settings_file = "gui_settings.json"
        
        # 윈도우 설정
        self.setup_window()
        self.load_window_settings()
        
        # UI 구성 요소 초기화
        self.setup_ui()
        
        # 윈도우 종료 이벤트 바인딩
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_window(self):
        """윈도우 기본 설정 - 레이아웃 최적화"""
        self.root.title("할일 관리자 - GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 윈도우 크기 조정 시 레이아웃 최적화를 위한 이벤트 바인딩
        self.root.bind('<Configure>', self._on_window_configure)
        
        # 그리드 가중치 설정으로 반응형 레이아웃 구현
        self.root.grid_rowconfigure(0, weight=0)  # 메뉴바
        self.root.grid_rowconfigure(1, weight=0)  # 툴바
        self.root.grid_rowconfigure(2, weight=1)  # 메인 콘텐츠
        self.root.grid_rowconfigure(3, weight=0)  # 상태바
        self.root.grid_columnconfigure(0, weight=1)
        
        # 아이콘 설정 (선택사항)
        try:
            # 아이콘 파일이 있다면 설정
            pass
        except:
            pass
    
    def setup_ui(self):
        """UI 구성 요소들을 설정"""
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_main_content()
        self.setup_status_bar()
        
        # 실시간 상태바 업데이트 시작
        self.start_status_bar_updates()
        
    def setup_menu_bar(self):
        """메뉴바 구현 (파일, 편집, 보기, 도움말)"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="새 할일", command=self.on_add_todo, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="데이터 백업", command=self.on_backup_data)
        file_menu.add_command(label="데이터 복원", command=self.on_restore_data)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.on_closing, accelerator="Ctrl+Q")
        
        # 편집 메뉴
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="편집", menu=edit_menu)
        edit_menu.add_command(label="할일 수정", command=self.on_edit_todo, accelerator="F2")
        edit_menu.add_command(label="할일 삭제", command=self.on_delete_todo, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="하위작업 추가", command=self.on_add_subtask, accelerator="Ctrl+Shift+N")
        
        # 보기 메뉴
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="보기", menu=view_menu)
        view_menu.add_command(label="새로고침", command=self.on_refresh, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="모두 확장", command=self.on_expand_all)
        view_menu.add_command(label="모두 축소", command=self.on_collapse_all)
        view_menu.add_separator()
        view_menu.add_checkbutton(label="완료된 할일 숨기기", command=self.on_toggle_completed)
        
        # 도움말 메뉴
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self.on_show_help)
        help_menu.add_command(label="정보", command=self.on_show_about)
        
        # 키보드 단축키 바인딩 - 접근성 개선
        self.root.bind('<Control-n>', lambda e: self.on_add_todo())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F2>', lambda e: self.on_edit_todo())
        self.root.bind('<Delete>', lambda e: self.on_delete_todo())
        self.root.bind('<Control-Shift-n>', lambda e: self.on_add_subtask())
        self.root.bind('<F5>', lambda e: self.on_refresh())
        
        # 추가 접근성 단축키
        self.root.bind('<Control-f>', lambda e: self._focus_search_box())
        self.root.bind('<Escape>', lambda e: self._clear_search_and_focus_tree())
        self.root.bind('<Control-h>', lambda e: self.on_show_help())
        self.root.bind('<F1>', lambda e: self.on_show_help())
        
        # 빠른 목표 날짜 설정 단축키 (Requirements: 키보드 단축키 추가)
        self.root.bind('<Control-d>', lambda e: self._quick_set_due_date_today())
        self.root.bind('<Control-Shift-d>', lambda e: self._quick_set_due_date_tomorrow())
        self.root.bind('<Control-Alt-d>', lambda e: self._quick_set_due_date_this_weekend())
        self.root.bind('<Control-r>', lambda e: self._quick_remove_due_date())
        
        # 접근성 도움말 단축키
        self.root.bind('<Alt-F1>', lambda e: self._show_accessibility_help())
        
        # Tab 순서 설정을 위한 포커스 체인 설정
        self._setup_focus_chain()
        
    def setup_toolbar(self):
        """툴바 구현 (추가, 수정, 삭제, 새로고침 버튼) - 접근성 및 툴팁 개선"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # 툴바 버튼들 - 툴팁과 접근성 개선
        self.btn_add = ttk.Button(self.toolbar, text="할일 추가", command=self.on_add_todo)
        self.btn_add.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(self.btn_add, "새로운 할일을 추가합니다 (Ctrl+N)")
        
        self.btn_edit = ttk.Button(self.toolbar, text="수정", command=self.on_edit_todo)
        self.btn_edit.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(self.btn_edit, "선택된 할일을 수정합니다 (F2)")
        
        self.btn_delete = ttk.Button(self.toolbar, text="삭제", command=self.on_delete_todo)
        self.btn_delete.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(self.btn_delete, "선택된 할일을 삭제합니다 (Del)")
        
        # 구분선
        separator1 = ttk.Separator(self.toolbar, orient=tk.VERTICAL)
        separator1.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.btn_add_subtask = ttk.Button(self.toolbar, text="하위작업 추가", command=self.on_add_subtask)
        self.btn_add_subtask.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(self.btn_add_subtask, "선택된 할일에 하위작업을 추가합니다 (Ctrl+Shift+N)")
        
        # 구분선
        separator2 = ttk.Separator(self.toolbar, orient=tk.VERTICAL)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.btn_refresh = ttk.Button(self.toolbar, text="새로고침", command=self.on_refresh)
        self.btn_refresh.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(self.btn_refresh, "할일 목록을 새로고침합니다 (F5)")
        
        self.btn_open_folder = ttk.Button(self.toolbar, text="폴더 열기", command=self.on_open_folder)
        self.btn_open_folder.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(self.btn_open_folder, "선택된 할일의 폴더를 엽니다")
        
        # 검색 박스 (오른쪽 정렬) - 컴포넌트 사용
        self.search_box = SearchBox(self.toolbar, self.on_search)
        self.search_box.pack(side=tk.RIGHT, padx=5)
        self._create_tooltip(self.search_box, "할일을 검색합니다 (실시간 검색)")
        
    def setup_main_content(self):
        """메인 콘텐츠 영역 설정 (트리 뷰)"""
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 필터 패널 추가
        self.filter_panel = FilterPanel(self.main_frame, self.on_filter_change)
        self.filter_panel.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # 트리 뷰 프레임
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # TodoTree 컴포넌트 생성
        self.todo_tree = TodoTree(self.tree_frame, self.todo_service)
        
        # 트리 이벤트 핸들러 연결
        self.todo_tree._on_edit_todo_callback = self.on_edit_todo
        self.todo_tree._on_delete_todo_callback = self.on_delete_todo
        self.todo_tree._on_add_subtask_callback = self.on_add_subtask
        self.todo_tree._on_edit_subtask_callback = self.on_edit_subtask
        self.todo_tree._on_delete_subtask_callback = self.on_delete_subtask
        self.todo_tree._on_open_folder_callback = self.on_open_folder
        self.todo_tree._on_add_new_todo_callback = self.on_add_todo
        self.todo_tree._on_refresh_callback = self.on_refresh
        self.todo_tree.on_todo_reordered = self.on_todo_reordered
        
        # 상태바 업데이트 이벤트 바인딩
        self.todo_tree.bind('<<StatusUpdate>>', self.on_status_update)
        
    def setup_status_bar(self):
        """상태바 구현 (할일 개수, 완료율 표시) - 컴포넌트 사용"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 전체 진행률 표시를 위한 프로그레스 바 추가
        progress_frame = ttk.Frame(self.status_bar.status_frame)
        progress_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(progress_frame, text="전체 진행률:").pack(side=tk.LEFT, padx=(0, 5))
        self.overall_progress_bar = ProgressBar(progress_frame, length=100)
        self.overall_progress_bar.pack(side=tk.LEFT)
        
        # 초기 상태 업데이트
        self.update_status_bar()
        
        # 사용자 설정 복원
        self._restore_user_settings()
        
    def update_status_bar(self):
        """상태바 정보 업데이트"""
        try:
            todos = self.todo_service.get_all_todos()
            total_todos = len(todos)
            
            if total_todos == 0:
                completion_rate = 0.0
                completed_todos = 0
                overall_progress = 0.0
            else:
                completed_todos = sum(1 for todo in todos if todo.is_completed())
                completion_rate = (completed_todos / total_todos) * 100
                
                # 전체 진행률 계산 (각 할일의 진행률 평균)
                total_progress = sum(todo.get_completion_rate() for todo in todos)
                overall_progress = total_progress / total_todos
            
            # 목표 날짜 관련 정보 가져오기
            status_summary = self.notification_service.get_status_bar_summary()
            due_today_count = status_summary['due_today']
            overdue_count = status_summary['overdue']
            
            # 상태바 컴포넌트 업데이트
            self.status_bar.update_todo_count(total_todos, completed_todos)
            self.status_bar.update_due_date_info(due_today_count, overdue_count)
            
            # 전체 진행률 바 업데이트
            self.overall_progress_bar.set_progress(overall_progress)
            
            # 상태 메시지 업데이트 (목표 날짜 정보 포함)
            if total_todos == 0:
                status_msg = "할일이 없습니다"
            elif completed_todos == total_todos:
                status_msg = "모든 할일이 완료되었습니다! 🎉"
            else:
                remaining = total_todos - completed_todos
                status_parts = [f"{remaining}개의 할일이 남아있습니다"]
                
                # 긴급한 정보가 있으면 상태 메시지에 추가
                if overdue_count > 0:
                    status_parts.append(f"⚠️ {overdue_count}개 지연")
                elif due_today_count > 0:
                    status_parts.append(f"📅 {due_today_count}개 오늘 마감")
                
                status_msg = " | ".join(status_parts)
            
            self.status_bar.update_status(status_msg)
            
        except Exception as e:
            self.status_bar.update_status(f"상태 업데이트 오류: {str(e)}")
    
    def start_status_bar_updates(self):
        """실시간 상태바 업데이트 시작
        
        Requirements: 실시간 정보 업데이트 구현
        """
        self._update_status_bar_periodically()
    
    def _update_status_bar_periodically(self):
        """주기적으로 상태바 업데이트 (1분마다)"""
        try:
            # 목표 날짜 관련 정보만 업데이트 (성능 최적화)
            status_summary = self.notification_service.get_status_bar_summary()
            due_today_count = status_summary['due_today']
            overdue_count = status_summary['overdue']
            
            # 상태바의 목표 날짜 정보 업데이트
            self.status_bar.update_due_date_info(due_today_count, overdue_count)
            
            # 상태 메시지도 업데이트 (변경사항이 있는 경우만)
            current_info = self.status_bar.get_due_date_info()
            if (current_info['due_today'] != due_today_count or 
                current_info['overdue'] != overdue_count):
                
                # 전체 상태바 업데이트
                self.update_status_bar()
            
        except Exception as e:
            print(f"주기적 상태바 업데이트 오류: {e}")
        
        # 1분 후 다시 실행 (60000ms)
        self.root.after(60000, self._update_status_bar_periodically)
    
    def load_window_settings(self):
        """윈도우 크기/위치 설정 로드 - 사용자 설정 확장"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 윈도우 크기와 위치 복원
                if 'geometry' in settings:
                    # 화면 해상도 검증 후 적용
                    geometry = settings['geometry']
                    if self._validate_geometry(geometry):
                        self.root.geometry(geometry)
                
                # 윈도우 상태 복원 (최대화 등)
                if 'state' in settings and settings['state'] == 'zoomed':
                    self.root.state('zoomed')
                
                # 사용자 설정 복원을 위해 저장
                self.saved_settings = settings
                    
        except Exception as e:
            print(f"설정 로드 오류: {e}")
            self.saved_settings = {}
    
    def _validate_geometry(self, geometry):
        """지오메트리 문자열이 현재 화면에 유효한지 검증"""
        try:
            # 지오메트리 파싱: "800x600+100+50"
            import re
            match = re.match(r'(\d+)x(\d+)([\+\-]\d+)([\+\-]\d+)', geometry)
            if not match:
                return False
            
            width = int(match.group(1))
            height = int(match.group(2))
            x_pos = int(match.group(3))
            y_pos = int(match.group(4))
            
            # 기본 유효성 검사
            if width <= 0 or height <= 0:
                return False
            
            # 화면 크기 가져오기 (root가 없는 경우 기본값 사용)
            try:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
            except:
                # 기본 화면 크기 (일반적인 해상도)
                screen_width = 1920
                screen_height = 1080
            
            # 윈도우가 화면 밖으로 나가지 않는지 확인
            if (width <= screen_width and height <= screen_height and
                x_pos >= -width and y_pos >= -height and
                x_pos < screen_width and y_pos < screen_height):
                return True
            
            return False
        except Exception as e:
            return False
    
    def _on_window_configure(self, event):
        """윈도우 크기 변경 시 레이아웃 최적화"""
        # 메인 윈도우의 Configure 이벤트만 처리
        if event.widget != self.root:
            return
        
        try:
            # 현재 윈도우 크기
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # 작은 화면에서 레이아웃 조정
            if width < 700:
                self._apply_compact_layout()
            else:
                self._apply_normal_layout()
            
            # 트리 뷰 컬럼 너비 자동 조정
            if hasattr(self, 'todo_tree'):
                self._adjust_tree_columns(width)
                
        except Exception as e:
            print(f"윈도우 크기 조정 처리 오류: {e}")
    
    def _apply_compact_layout(self):
        """작은 화면용 컴팩트 레이아웃"""
        try:
            # 툴바 버튼 텍스트 축약
            if hasattr(self, 'btn_add'):
                self.btn_add.config(text="추가")
            if hasattr(self, 'btn_edit'):
                self.btn_edit.config(text="수정")
            if hasattr(self, 'btn_delete'):
                self.btn_delete.config(text="삭제")
            if hasattr(self, 'btn_add_subtask'):
                self.btn_add_subtask.config(text="하위+")
            if hasattr(self, 'btn_refresh'):
                self.btn_refresh.config(text="새로고침")
            if hasattr(self, 'btn_open_folder'):
                self.btn_open_folder.config(text="폴더")
                
        except Exception as e:
            print(f"컴팩트 레이아웃 적용 오류: {e}")
    
    def _apply_normal_layout(self):
        """일반 화면용 레이아웃"""
        try:
            # 툴바 버튼 텍스트 복원
            if hasattr(self, 'btn_add'):
                self.btn_add.config(text="할일 추가")
            if hasattr(self, 'btn_edit'):
                self.btn_edit.config(text="수정")
            if hasattr(self, 'btn_delete'):
                self.btn_delete.config(text="삭제")
            if hasattr(self, 'btn_add_subtask'):
                self.btn_add_subtask.config(text="하위작업 추가")
            if hasattr(self, 'btn_refresh'):
                self.btn_refresh.config(text="새로고침")
            if hasattr(self, 'btn_open_folder'):
                self.btn_open_folder.config(text="폴더 열기")
                
        except Exception as e:
            print(f"일반 레이아웃 적용 오류: {e}")
    
    def _adjust_tree_columns(self, window_width):
        """윈도우 크기에 따른 트리 컬럼 너비 조정"""
        try:
            if not hasattr(self, 'todo_tree'):
                return
            
            # 기본 컬럼 너비 비율
            title_ratio = 0.55  # 제목 컬럼 55%
            progress_ratio = 0.25  # 진행률 컬럼 25% (진행률 바를 위해 더 넓게)
            date_ratio = 0.2  # 날짜 컬럼 20%
            
            # 사용 가능한 너비 (스크롤바 등 고려)
            available_width = max(window_width - 50, 400)
            
            # 각 컬럼 너비 계산
            title_width = int(available_width * title_ratio)
            progress_width = int(available_width * progress_ratio)
            date_width = int(available_width * date_ratio)
            
            # 최소 너비 보장
            title_width = max(title_width, 200)
            progress_width = max(progress_width, 120)  # 진행률 바를 위해 최소 너비 증가
            date_width = max(date_width, 100)
            
            # 컬럼 너비 적용
            self.todo_tree.column('#0', width=title_width)
            self.todo_tree.column('progress', width=progress_width)
            self.todo_tree.column('created_at', width=date_width)
            
            # 진행률 바 위치 재조정
            self.todo_tree.after_idle(self.todo_tree._reposition_all_progress_widgets)
            
        except Exception as e:
            print(f"트리 컬럼 조정 오류: {e}")
    
    def _restore_user_settings(self):
        """사용자 설정 복원"""
        try:
            if not hasattr(self, 'saved_settings'):
                return
            
            settings = self.saved_settings
            
            # 필터 설정 복원
            if 'filter_options' in settings and hasattr(self, 'filter_panel'):
                filter_opts = settings['filter_options']
                if 'show_completed' in filter_opts:
                    self.filter_panel.show_completed_var.set(filter_opts['show_completed'])
                if 'sort_by' in filter_opts:
                    self.filter_panel.sort_by_var.set(filter_opts['sort_by'])
                if 'sort_order' in filter_opts:
                    self.filter_panel.sort_order_var.set(filter_opts['sort_order'])
                if 'due_date_filter' in filter_opts:
                    self.filter_panel.due_date_filter_var.set(filter_opts['due_date_filter'])
            
            # 시작 알림 설정 복원
            if 'show_startup_notifications' in settings:
                # 설정이 저장되어 있으면 그 값을 사용, 없으면 기본값 True
                pass  # 이미 saved_settings에 저장되어 있음
            
            # 검색어 복원 (선택사항 - 보통은 빈 상태로 시작)
            # if 'last_search' in settings and hasattr(self, 'search_box'):
            #     self.search_box.search_var.set(settings['last_search'])
            
            # 트리 확장 상태 복원
            if 'expanded_todos' in settings and hasattr(self, 'todo_tree'):
                # 트리가 로드된 후에 확장 상태 복원
                self.root.after(100, lambda: self._restore_tree_expansion(settings['expanded_todos']))
                
        except Exception as e:
            print(f"사용자 설정 복원 오류: {e}")
    
    def _restore_tree_expansion(self, expanded_todo_ids):
        """트리 확장 상태 복원"""
        try:
            if not hasattr(self, 'todo_tree'):
                return
            
            for todo_id in expanded_todo_ids:
                if todo_id in self.todo_tree.todo_nodes:
                    node_id = self.todo_tree.todo_nodes[todo_id]
                    self.todo_tree.item(node_id, open=True)
                    
        except Exception as e:
            print(f"트리 확장 상태 복원 오류: {e}")
    
    def save_window_settings(self):
        """윈도우 크기/위치 설정 저장 - 사용자 설정 확장"""
        try:
            # 기본 윈도우 설정
            settings = {
                'geometry': self.root.geometry(),
                'state': self.root.state()
            }
            
            # 추가 사용자 설정 저장
            if hasattr(self, 'filter_panel'):
                settings['filter_options'] = self.filter_panel.get_filter_options()
            
            if hasattr(self, 'search_box'):
                settings['last_search'] = self.search_box.get_search_term()
            
            # 트리 확장 상태 저장
            if hasattr(self, 'todo_tree'):
                expanded_todos = []
                for todo_id, node_id in self.todo_tree.todo_nodes.items():
                    if self.todo_tree.item(node_id, 'open'):
                        expanded_todos.append(todo_id)
                settings['expanded_todos'] = expanded_todos
            
            # 시작 알림 설정 저장
            if hasattr(self, 'saved_settings') and 'show_startup_notifications' in self.saved_settings:
                settings['show_startup_notifications'] = self.saved_settings['show_startup_notifications']
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"설정 저장 오류: {e}")
    
    def _create_tooltip(self, widget, text):
        """위젯에 툴팁 추가"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            # 3초 후 자동 사라짐
            tooltip.after(3000, tooltip.destroy)
            
            # 마우스가 위젯을 벗어나면 즉시 사라짐
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.bind('<Leave>', hide_tooltip, add='+')
        
        widget.bind('<Enter>', show_tooltip, add='+')
    
    def _setup_focus_chain(self):
        """Tab 키 순서 설정"""
        # 포커스 가능한 위젯들의 순서 정의
        focus_widgets = []
        
        # 툴바 버튼들
        if hasattr(self, 'btn_add'):
            focus_widgets.append(self.btn_add)
        if hasattr(self, 'btn_edit'):
            focus_widgets.append(self.btn_edit)
        if hasattr(self, 'btn_delete'):
            focus_widgets.append(self.btn_delete)
        if hasattr(self, 'btn_add_subtask'):
            focus_widgets.append(self.btn_add_subtask)
        if hasattr(self, 'btn_refresh'):
            focus_widgets.append(self.btn_refresh)
        if hasattr(self, 'btn_open_folder'):
            focus_widgets.append(self.btn_open_folder)
        
        # 검색 박스
        if hasattr(self, 'search_box') and hasattr(self.search_box, 'search_entry'):
            focus_widgets.append(self.search_box.search_entry)
        
        # 필터 패널 위젯들
        if hasattr(self, 'filter_panel'):
            if hasattr(self.filter_panel, 'show_completed_check'):
                focus_widgets.append(self.filter_panel.show_completed_check)
            if hasattr(self.filter_panel, 'sort_combo'):
                focus_widgets.append(self.filter_panel.sort_combo)
            if hasattr(self.filter_panel, 'sort_order_combo'):
                focus_widgets.append(self.filter_panel.sort_order_combo)
        
        # 트리 뷰
        if hasattr(self, 'todo_tree'):
            focus_widgets.append(self.todo_tree)
        
        # Tab 키 바인딩 설정
        for i, widget in enumerate(focus_widgets):
            next_widget = focus_widgets[(i + 1) % len(focus_widgets)]
            prev_widget = focus_widgets[(i - 1) % len(focus_widgets)]
            
            widget.bind('<Tab>', lambda e, next_w=next_widget: self._focus_next_widget(next_w))
            widget.bind('<Shift-Tab>', lambda e, prev_w=prev_widget: self._focus_next_widget(prev_w))
    
    def _focus_next_widget(self, widget):
        """다음 위젯으로 포커스 이동"""
        try:
            widget.focus_set()
            return "break"  # 기본 Tab 동작 방지
        except:
            pass
    
    def _focus_search_box(self):
        """검색 박스로 포커스 이동"""
        if hasattr(self, 'search_box') and hasattr(self.search_box, 'search_entry'):
            self.search_box.search_entry.focus_set()
            self.search_box.search_entry.select_range(0, tk.END)
    
    def _clear_search_and_focus_tree(self):
        """검색 클리어 후 트리로 포커스 이동"""
        if hasattr(self, 'search_box'):
            self.search_box.clear()
        if hasattr(self, 'todo_tree'):
            self.todo_tree.focus_set()
    
    def _quick_set_due_date_today(self):
        """빠른 목표 날짜 설정 - 오늘 (Ctrl+D)
        
        Requirements: 키보드 단축키 추가 (빠른 목표 날짜 설정)
        """
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                self.status_bar.update_status("할일을 선택한 후 단축키를 사용하세요.")
                return
            
            from datetime import datetime
            today_due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
            
            success = self.todo_service.set_todo_due_date(todo_id, today_due)
            if success:
                self.on_refresh()
                self.update_status_bar()
                self.status_bar.update_status("목표 날짜가 오늘 18:00으로 설정되었습니다.")
            else:
                show_error_dialog(self.root, "목표 날짜 설정에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"목표 날짜 설정 중 오류가 발생했습니다: {str(e)}")
    
    def _quick_set_due_date_tomorrow(self):
        """빠른 목표 날짜 설정 - 내일 (Ctrl+Shift+D)
        
        Requirements: 키보드 단축키 추가 (빠른 목표 날짜 설정)
        """
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                self.status_bar.update_status("할일을 선택한 후 단축키를 사용하세요.")
                return
            
            from datetime import datetime, timedelta
            tomorrow_due = (datetime.now() + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
            
            success = self.todo_service.set_todo_due_date(todo_id, tomorrow_due)
            if success:
                self.on_refresh()
                self.update_status_bar()
                self.status_bar.update_status("목표 날짜가 내일 18:00으로 설정되었습니다.")
            else:
                show_error_dialog(self.root, "목표 날짜 설정에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"목표 날짜 설정 중 오류가 발생했습니다: {str(e)}")
    
    def _quick_set_due_date_this_weekend(self):
        """빠른 목표 날짜 설정 - 이번 주말 (Ctrl+Alt+D)
        
        Requirements: 키보드 단축키 추가 (빠른 목표 날짜 설정)
        """
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                self.status_bar.update_status("할일을 선택한 후 단축키를 사용하세요.")
                return
            
            from services.date_service import DateService
            quick_options = DateService.get_quick_date_options()
            weekend_due = quick_options.get("이번 주말")
            
            if weekend_due:
                success = self.todo_service.set_todo_due_date(todo_id, weekend_due)
                if success:
                    self.on_refresh()
                    self.update_status_bar()
                    self.status_bar.update_status("목표 날짜가 이번 주말로 설정되었습니다.")
                else:
                    show_error_dialog(self.root, "목표 날짜 설정에 실패했습니다.")
            else:
                show_error_dialog(self.root, "이번 주말 날짜를 계산할 수 없습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"목표 날짜 설정 중 오류가 발생했습니다: {str(e)}")
    
    def _quick_remove_due_date(self):
        """빠른 목표 날짜 제거 (Ctrl+R)
        
        Requirements: 키보드 단축키 추가 (빠른 목표 날짜 설정)
        """
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                self.status_bar.update_status("할일을 선택한 후 단축키를 사용하세요.")
                return
            
            success = self.todo_service.set_todo_due_date(todo_id, None)
            if success:
                self.on_refresh()
                self.update_status_bar()
                self.status_bar.update_status("목표 날짜가 제거되었습니다.")
            else:
                show_error_dialog(self.root, "목표 날짜 제거에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"목표 날짜 제거 중 오류가 발생했습니다: {str(e)}")
    
    def _show_accessibility_help(self):
        """접근성 도움말 표시 (Alt+F1)
        
        Requirements: 툴팁 및 도움말 메시지 추가
        """
        help_text = """
접근성 기능 및 키보드 단축키

=== 빠른 목표 날짜 설정 ===
• Ctrl+D: 선택된 할일의 목표 날짜를 오늘 18:00으로 설정
• Ctrl+Shift+D: 선택된 할일의 목표 날짜를 내일 18:00으로 설정
• Ctrl+Alt+D: 선택된 할일의 목표 날짜를 이번 주말로 설정
• Ctrl+R: 선택된 할일의 목표 날짜 제거

=== 일반 단축키 ===
• Ctrl+N: 새 할일 추가
• F2: 선택된 할일/하위작업 수정
• Del: 선택된 할일/하위작업 삭제
• Ctrl+Shift+N: 하위작업 추가
• F5: 새로고침
• Ctrl+F: 검색 박스로 포커스 이동
• Esc: 검색 클리어 후 트리로 포커스 이동

=== 접근성 기능 ===
• 색상과 함께 패턴/아이콘으로 긴급도 표시
• 키보드만으로 모든 기능 접근 가능
• Tab 키로 UI 요소 간 이동
• 스크린 리더 지원을 위한 접근성 레이블

=== 긴급도 표시 ===
• 🔴 !!! : 지연됨 (빨간색)
• 🟠 !! : 24시간 이내 마감 (주황색)
• 🟡 ! : 3일 이내 마감 (노란색)
• ⚪ : 일반 우선순위 (검은색)
• ✅ ✓ : 완료됨 (회색)

도움말: F1 또는 Ctrl+H
접근성 도움말: Alt+F1
        """
        
        show_info_dialog(self.root, help_text, "접근성 도움말")
    
    # 이벤트 핸들러들
    def on_add_todo(self):
        """할일 추가 이벤트 핸들러"""
        try:
            result = show_add_todo_dialog_with_due_date(self.root)
            if result:
                title = result['title']
                due_date = result.get('due_date')
                
                todo = self.todo_service.add_todo(title)
                if todo and due_date:
                    self.todo_service.set_todo_due_date(todo.id, due_date)
                
                self.on_refresh()  # 필터 적용하여 새로고침
                self.update_status_bar()  # 전체 진행률 즉시 업데이트
                self.status_bar.update_status(f"할일 '{title}'이(가) 추가되었습니다.")
                self.status_bar.update_last_saved("저장됨")
        except RuntimeError as e:
            # 폴더 관련 오류는 향상된 다이얼로그 사용
            error_msg = str(e)
            if "폴더" in error_msg:
                show_folder_error_dialog(self.root, error_msg, "할일 추가 실패")
            else:
                show_error_dialog(self.root, f"할일 추가 중 오류가 발생했습니다:\n{error_msg}")
        except Exception as e:
            show_error_dialog(self.root, f"할일 추가 중 예상치 못한 오류가 발생했습니다:\n{str(e)}")
    
    def on_edit_todo(self):
        """할일 수정 이벤트 핸들러"""
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                show_info_dialog(self.root, "수정할 할일을 선택해주세요.")
                return
            
            todo = self.todo_service.get_todo_by_id(todo_id)
            if not todo:
                show_error_dialog(self.root, "선택된 할일을 찾을 수 없습니다.")
                return
            
            result = show_edit_todo_dialog_with_due_date(self.root, todo.title, todo.due_date)
            if result:
                title_changed = result.get('title') is not None
                due_date_changed = result.get('due_date_changed', False)
                
                success = True
                if title_changed:
                    success = self.todo_service.update_todo(todo_id, result['title'])
                
                if success and due_date_changed:
                    success = self.todo_service.set_todo_due_date(todo_id, result['due_date'])
                
                if success:
                    self.on_refresh()  # 필터 적용하여 새로고침
                    self.update_status_bar()  # 전체 진행률 즉시 업데이트
                    
                    if title_changed and due_date_changed:
                        self.status_bar.update_status("할일 제목과 목표 날짜가 수정되었습니다.")
                    elif title_changed:
                        self.status_bar.update_status(f"할일이 '{result['title']}'(으)로 수정되었습니다.")
                    elif due_date_changed:
                        self.status_bar.update_status("할일의 목표 날짜가 수정되었습니다.")
                    
                    self.status_bar.update_last_saved("저장됨")
                else:
                    show_error_dialog(self.root, "할일 수정에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"할일 수정 중 오류가 발생했습니다: {str(e)}")
    
    def on_delete_todo(self):
        """할일 삭제 이벤트 핸들러"""
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                show_info_dialog(self.root, "삭제할 할일을 선택해주세요.")
                return
            
            todo = self.todo_service.get_todo_by_id(todo_id)
            if not todo:
                show_error_dialog(self.root, "선택된 할일을 찾을 수 없습니다.")
                return
            
            # 삭제 확인
            if not show_delete_confirm_dialog(self.root, todo.title):
                return
            
            # 폴더 삭제 여부 확인
            delete_folder = show_folder_delete_confirm_dialog(self.root, todo.title)
            
            success = self.todo_service.delete_todo(todo_id, delete_folder)
            if success:
                self.on_refresh()  # 필터 적용하여 새로고침
                self.update_status_bar()  # 전체 진행률 즉시 업데이트
                self.status_bar.update_status(f"할일 '{todo.title}'이(가) 삭제되었습니다.")
                self.status_bar.update_last_saved("저장됨")
            else:
                show_error_dialog(self.root, "할일 삭제에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"할일 삭제 중 오류가 발생했습니다: {str(e)}")
    
    def on_add_subtask(self):
        """하위작업 추가 이벤트 핸들러"""
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                show_info_dialog(self.root, "하위작업을 추가할 할일을 선택해주세요.")
                return
            
            todo = self.todo_service.get_todo_by_id(todo_id)
            if not todo:
                show_error_dialog(self.root, "선택된 할일을 찾을 수 없습니다.")
                return
            
            result = show_add_subtask_dialog_with_due_date(self.root, todo.title, todo.due_date)
            if result:
                subtask_title = result['title']
                due_date = result.get('due_date')
                
                subtask = self.todo_service.add_subtask(todo_id, subtask_title)
                if subtask and due_date:
                    self.todo_service.set_subtask_due_date(todo_id, subtask.id, due_date)
                
                if subtask:
                    self.on_refresh()  # 필터 적용하여 새로고침
                    self.update_status_bar()  # 전체 진행률 즉시 업데이트
                    self.status_bar.update_status(f"하위작업 '{subtask_title}'이(가) 추가되었습니다.")
                    self.status_bar.update_last_saved("저장됨")
                else:
                    show_error_dialog(self.root, "하위작업 추가에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"하위작업 추가 중 오류가 발생했습니다: {str(e)}")
    
    def on_edit_subtask(self):
        """하위작업 수정 이벤트 핸들러"""
        try:
            subtask_id = self.todo_tree.get_selected_subtask_id()
            todo_id = self.todo_tree.get_selected_todo_id()
            
            if not subtask_id or not todo_id:
                show_info_dialog(self.root, "수정할 하위작업을 선택해주세요.")
                return
            
            # 현재 하위작업 정보 가져오기
            subtasks = self.todo_service.get_subtasks(todo_id)
            current_subtask = None
            for subtask in subtasks:
                if subtask.id == subtask_id:
                    current_subtask = subtask
                    break
            
            if not current_subtask:
                show_error_dialog(self.root, "선택된 하위작업을 찾을 수 없습니다.")
                return
            
            # 하위작업 수정 다이얼로그 (EditTodoDialog를 재사용)
            from gui.dialogs import EditTodoDialog
            dialog = EditTodoDialog(self.root, current_subtask.title)
            dialog.title("하위작업 수정")
            self.root.wait_window(dialog)
            
            new_title = dialog.result
            if new_title:
                success = self.todo_service.update_subtask(todo_id, subtask_id, new_title)
                if success:
                    self.on_refresh()  # 필터 적용하여 새로고침
                    self.update_status_bar()  # 전체 진행률 즉시 업데이트
                    self.status_bar.update_status(f"하위작업이 '{new_title}'(으)로 수정되었습니다.")
                    self.status_bar.update_last_saved("저장됨")
                else:
                    show_error_dialog(self.root, "하위작업 수정에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"하위작업 수정 중 오류가 발생했습니다: {str(e)}")
    
    def on_delete_subtask(self):
        """하위작업 삭제 이벤트 핸들러"""
        try:
            subtask_id = self.todo_tree.get_selected_subtask_id()
            todo_id = self.todo_tree.get_selected_todo_id()
            
            if not subtask_id or not todo_id:
                show_info_dialog(self.root, "삭제할 하위작업을 선택해주세요.")
                return
            
            # 현재 하위작업 정보 가져오기
            subtasks = self.todo_service.get_subtasks(todo_id)
            current_subtask = None
            for subtask in subtasks:
                if subtask.id == subtask_id:
                    current_subtask = subtask
                    break
            
            if not current_subtask:
                show_error_dialog(self.root, "선택된 하위작업을 찾을 수 없습니다.")
                return
            
            # 삭제 확인
            if not show_delete_confirm_dialog(self.root, current_subtask.title, "하위작업"):
                return
            
            success = self.todo_service.delete_subtask(todo_id, subtask_id)
            if success:
                self.on_refresh()  # 필터 적용하여 새로고침
                self.update_status_bar()  # 전체 진행률 즉시 업데이트
                self.status_bar.update_status(f"하위작업 '{current_subtask.title}'이(가) 삭제되었습니다.")
                self.status_bar.update_last_saved("저장됨")
            else:
                show_error_dialog(self.root, "하위작업 삭제에 실패했습니다.")
        except Exception as e:
            show_error_dialog(self.root, f"하위작업 삭제 중 오류가 발생했습니다: {str(e)}")
    
    def on_todo_reordered(self, event=None):
        """할일 순서 변경 이벤트 핸들러"""
        self.status_bar.update_status("할일 순서가 변경되었습니다. (순서 저장 기능은 향후 구현 예정)")
        # 향후 실제 순서 저장 기능이 구현되면 여기서 처리
    
    def on_refresh(self):
        """새로고침 이벤트 핸들러"""
        try:
            # 캐시 무효화
            self.todo_service.clear_cache()
            
            # 현재 검색어와 필터 옵션 적용하여 새로고침
            if hasattr(self, 'search_box') and hasattr(self, 'filter_panel'):
                search_term = self.search_box.get_search_term()
                filter_options = self.filter_panel.get_filter_options()
                
                # 필터링된 할일 목록 가져오기
                filtered_todos = self.todo_service.filter_todos(
                    show_completed=filter_options['show_completed'],
                    search_term=search_term
                )
                
                # 정렬 적용
                sorted_todos = self.todo_service.sort_todos(
                    filtered_todos, 
                    sort_by=filter_options['sort_by']
                )
                
                # 정렬 순서 적용
                if filter_options['sort_order'] == 'desc':
                    sorted_todos.reverse()
                
                # 트리 뷰 업데이트
                self.todo_tree.populate_tree(sorted_todos)
            else:
                # 필터 컴포넌트가 없는 경우 기본 새로고침
                if hasattr(self, 'todo_tree'):
                    self.todo_tree.refresh_tree()
            
            self.update_status_bar()
            self.status_bar.update_last_saved("새로고침됨")
            self.status_bar.update_status("데이터가 새로고침되었습니다")
            
        except Exception as e:
            show_error_dialog(self.root, f"새로고침 중 오류가 발생했습니다: {str(e)}")
    
    def on_open_folder(self):
        """폴더 열기 이벤트 핸들러"""
        try:
            todo_id = self.todo_tree.get_selected_todo_id()
            if not todo_id:
                show_info_dialog(self.root, "폴더를 열 할일을 선택해주세요.")
                return
            
            todo = self.todo_service.get_todo_by_id(todo_id)
            if not todo:
                show_error_dialog(self.root, "선택된 할일을 찾을 수 없습니다.")
                return
            
            # FileService를 통해 폴더 열기 (개선된 오류 처리)
            file_service = self.todo_service.file_service
            success, error_message = file_service.open_todo_folder(todo.folder_path)
            
            if success:
                self.status_bar.update_status(f"'{todo.title}' 폴더가 열렸습니다.")
            else:
                # 향상된 폴더 오류 다이얼로그 사용
                show_folder_error_dialog(
                    self.root, 
                    f"할일: {todo.title}\n\n{error_message}",
                    "폴더 열기 실패"
                )
        except Exception as e:
            show_error_dialog(self.root, f"폴더 열기 중 예상치 못한 오류가 발생했습니다:\n{str(e)}", "시스템 오류")
    
    def on_search(self, search_term: str):
        """검색 이벤트 핸들러 - 실시간 검색 기능"""
        try:
            # 현재 필터 옵션 가져오기
            filter_options = self.filter_panel.get_filter_options()
            
            # 검색어와 필터 옵션을 적용하여 할일 목록 필터링
            filtered_todos = self.todo_service.filter_todos(
                show_completed=filter_options['show_completed'],
                search_term=search_term
            )
            
            # 정렬 적용
            sorted_todos = self.todo_service.sort_todos(
                filtered_todos, 
                sort_by=filter_options['sort_by']
            )
            
            # 정렬 순서 적용 (desc인 경우 역순)
            if filter_options['sort_order'] == 'desc':
                sorted_todos.reverse()
            
            # 트리 뷰 업데이트
            self.todo_tree.populate_tree(sorted_todos)
            
            # 상태바 업데이트
            if search_term:
                self.status_bar.update_status(f"검색 결과: {len(sorted_todos)}개 항목")
            else:
                self.status_bar.update_status(f"전체 {len(sorted_todos)}개 항목")
                
        except Exception as e:
            show_error_dialog(self.root, f"검색 중 오류가 발생했습니다: {str(e)}")
    
    def on_filter_change(self, filter_options):
        """필터 옵션 변경 이벤트 핸들러"""
        try:
            # 현재 검색어 가져오기
            search_term = self.search_box.get_search_term()
            
            # 목표 날짜 필터와 정렬을 통합하여 처리
            due_date_filter = filter_options.get('due_date_filter', 'all')
            sort_by = filter_options['sort_by']
            show_completed = filter_options['show_completed']
            
            # 통합 필터링 및 정렬 사용
            filtered_todos = self.todo_service.get_filtered_and_sorted_todos(
                filter_type=due_date_filter,
                sort_by=sort_by,
                show_completed=show_completed
            )
            
            # 검색어 필터링 (추가)
            if search_term:
                search_term_lower = search_term.lower()
                filtered_todos = [
                    todo for todo in filtered_todos
                    if (search_term_lower in todo.title.lower() or
                        any(search_term_lower in subtask.title.lower() 
                            for subtask in todo.subtasks))
                ]
            
            # 정렬 순서 적용 (desc인 경우 역순)
            if filter_options['sort_order'] == 'desc':
                filtered_todos.reverse()
            
            # 트리 뷰 업데이트
            self.todo_tree.populate_tree(filtered_todos)
            
            # 상태바 업데이트
            filter_msg = []
            if not show_completed:
                filter_msg.append("완료된 할일 숨김")
            if due_date_filter != 'all':
                filter_names = {
                    'due_today': '오늘 마감',
                    'overdue': '지연된 할일',
                    'this_week': '이번 주'
                }
                filter_msg.append(filter_names.get(due_date_filter, due_date_filter))
            if search_term:
                filter_msg.append(f"검색: '{search_term}'")
            
            if filter_msg:
                status_text = f"필터 적용 ({', '.join(filter_msg)}): {len(filtered_todos)}개 항목"
            else:
                status_text = f"전체 {len(filtered_todos)}개 항목"
            
            self.status_bar.update_status(status_text)
            
        except Exception as e:
            show_error_dialog(self.root, f"필터 적용 중 오류가 발생했습니다: {str(e)}")
    
    def on_toggle_completed(self):
        """완료된 할일 숨기기/보이기 토글"""
        # 필터 패널의 완료된 할일 표시 옵션 토글
        current_value = self.filter_panel.show_completed_var.get()
        self.filter_panel.show_completed_var.set(not current_value)
    
    def on_expand_all(self):
        """모든 트리 노드 확장"""
        if hasattr(self, 'todo_tree'):
            self.todo_tree.expand_all()
            self.status_bar.update_status("모든 항목이 확장되었습니다")
    
    def on_collapse_all(self):
        """모든 트리 노드 축소"""
        if hasattr(self, 'todo_tree'):
            self.todo_tree.collapse_all()
            self.status_bar.update_status("모든 항목이 축소되었습니다")
    
    def on_backup_data(self):
        """데이터 백업"""
        try:
            filename = filedialog.asksaveasfilename(
                title="데이터 백업",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                # TODO: 실제 백업 로직 구현
                messagebox.showinfo("성공", f"데이터가 {filename}에 백업되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"백업 중 오류가 발생했습니다: {str(e)}")
    
    def on_restore_data(self):
        """데이터 복원"""
        try:
            filename = filedialog.askopenfilename(
                title="데이터 복원",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                # TODO: 실제 복원 로직 구현
                messagebox.showinfo("성공", f"{filename}에서 데이터가 복원되었습니다.")
                self.update_status_bar()
        except Exception as e:
            messagebox.showerror("오류", f"복원 중 오류가 발생했습니다: {str(e)}")
    
    def on_show_help(self):
        """도움말 표시 - 향상된 도움말"""
        help_text = """할일 관리자 - GUI 버전 사용법

📋 주요 기능:
• 할일 추가/수정/삭제
• 하위작업 관리 (체크박스)
• 목표 날짜 설정 및 긴급도 표시
• 실시간 진행률 표시
• 검색 및 필터링
• 폴더 관리 및 파일 연동
• 자동 저장 및 백업

⌨️ 키보드 단축키:
• Ctrl+N: 새 할일 추가
• F2: 선택된 항목 수정
• Del: 선택된 항목 삭제
• Ctrl+Shift+N: 하위작업 추가
• F5: 새로고침
• Ctrl+F: 검색 박스로 이동
• Ctrl+H 또는 F1: 도움말
• Alt+F1: 접근성 도움말
• Escape: 검색 지우고 트리로 이동
• Space: 하위작업 완료 토글
• Tab/Shift+Tab: 위젯 간 이동
• Ctrl+Q: 프로그램 종료

⚡ 빠른 목표 날짜 설정:
• Ctrl+D: 오늘 18:00으로 설정
• Ctrl+Shift+D: 내일 18:00으로 설정
• Ctrl+Alt+D: 이번 주말로 설정
• Ctrl+R: 목표 날짜 제거

🖱️ 마우스 조작:
• 단일 클릭: 항목 선택
• 더블 클릭: 항목 수정
• 우클릭: 컨텍스트 메뉴
• 체크박스 클릭: 완료 상태 토글
• 드래그: 할일 순서 변경 (예정)

🔍 검색 및 필터:
• 실시간 검색 지원
• 완료된 할일 숨기기/보이기
• 목표 날짜별 필터링: 전체, 오늘 마감, 지연된 할일, 이번 주
• 생성일/제목/진행률/목표 날짜 순 정렬
• 오름차순/내림차순 정렬

📅 목표 날짜 기능:
• 할일 및 하위작업에 목표 날짜 설정
• 긴급도에 따른 색상 및 아이콘 표시:
  🔴 !!! 빨간색: 지연된 할일
  🟠 !! 주황색: 24시간 이내 마감
  🟡 ! 노란색: 3일 이내 마감
  ⚪ 검은색: 일반 우선순위
  ✅ ✓ 회색: 완료된 할일
• 상대적 시간 표시 (D-3, 2일 후, 3시간 지남 등)
• 상태바에 오늘 마감/지연된 할일 개수 표시

💾 데이터 관리:
• 자동 저장 (변경 시 즉시)
• 자동 백업 (최대 5개 유지)
• 윈도우 설정 자동 저장
• 프로그램 종료 시 안전한 데이터 보존

📁 폴더 기능:
• 할일별 전용 폴더 자동 생성
• 폴더 열기로 관련 파일 관리
• 할일 삭제 시 폴더 삭제 선택 가능

♿ 접근성 기능:
• 색상과 함께 아이콘/패턴으로 정보 표시
• 키보드만으로 모든 기능 접근 가능
• 스크린 리더 지원을 위한 접근성 레이블
• 고대비 색상 및 명확한 시각적 구분
• 툴팁으로 상세한 도움말 제공

💡 사용 팁:
• 할일에 하위작업을 추가하여 세부 계획 관리
• 진행률 바로 전체 진행 상황 파악
• 검색으로 많은 할일 중 원하는 항목 빠르게 찾기
• 컨텍스트 메뉴로 다양한 기능 빠르게 접근
• 목표 날짜를 설정하여 시간 기반 할일 관리
• 긴급도 색상을 참고하여 우선순위 결정"""
        
        # 도움말 창을 별도 윈도우로 표시
        self._show_help_window(help_text)
    
    def _show_help_window(self, help_text):
        """도움말을 별도 윈도우로 표시"""
        help_window = tk.Toplevel(self.root)
        help_window.title("할일 관리자 - 도움말")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        help_window.transient(self.root)
        
        # 도움말 텍스트 표시
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스크롤 가능한 텍스트 위젯
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 도움말 텍스트 삽입
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용
        
        # 닫기 버튼
        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        close_button = ttk.Button(button_frame, text="닫기", command=help_window.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # 윈도우 중앙 배치
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() - help_window.winfo_reqwidth()) // 2
        y = (help_window.winfo_screenheight() - help_window.winfo_reqheight()) // 2
        help_window.geometry(f"+{x}+{y}")
        
        # 포커스 설정
        help_window.focus_set()
        close_button.focus_set()
    
    def on_show_about(self):
        """프로그램 정보 표시"""
        about_text = """할일 관리자 GUI 버전 1.0

Python tkinter 기반 할일 관리 프로그램
하위작업 지원 및 폴더 관리 기능 포함

개발: AI Assistant
라이선스: MIT"""
        
        messagebox.showinfo("프로그램 정보", about_text)
    
    def on_status_update(self, event=None):
        """상태바 즉시 업데이트 이벤트 처리"""
        self.update_status_bar()
    
    def on_closing(self):
        """윈도우 종료 이벤트 핸들러"""
        try:
            # 윈도우 설정 저장
            self.save_window_settings()
            
            # 데이터 저장 확인
            if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
                self.root.destroy()
                
        except Exception as e:
            messagebox.showerror("오류", f"종료 중 오류가 발생했습니다: {str(e)}")
            self.root.destroy()
    
    def check_and_show_startup_notification(self):
        """
        시작 시 알림 표시 조건 확인 및 다이얼로그 표시 로직 구현
        
        Requirements 8.4: 목표 날짜가 임박한 할일이 있으면 시작 시 알림 표시
        """
        try:
            # "다시 보지 않기" 설정 확인
            if not self.get_startup_notification_setting():
                return
            
            # 알림 표시 조건 확인
            if not self.notification_service.should_show_startup_notification():
                return
            
            # 알림 정보 가져오기
            status_summary = self.notification_service.get_status_bar_summary()
            overdue_count = status_summary['overdue']
            due_today_count = status_summary['due_today']
            
            # 시작 알림 다이얼로그 표시
            self.root.after(500, lambda: self._show_startup_notification_dialog(overdue_count, due_today_count))
            
        except Exception as e:
            # 알림 표시 실패는 치명적이지 않으므로 로그만 남기고 계속 진행
            print(f"시작 알림 확인 중 오류: {e}")
    
    def _show_startup_notification_dialog(self, overdue_count: int, due_today_count: int):
        """
        시작 알림 다이얼로그 표시
        
        Args:
            overdue_count: 지연된 할일 개수
            due_today_count: 오늘 마감인 할일 개수
        """
        try:
            result = show_startup_notification_dialog(self.root, overdue_count, due_today_count)
            
            # "다시 보지 않기" 옵션 처리
            if result.get('dont_show_again', False):
                self.set_startup_notification_setting(False)
                if hasattr(self, 'status_bar'):
                    self.status_bar.update_status("시작 알림이 비활성화되었습니다.")
            
        except Exception as e:
            print(f"시작 알림 다이얼로그 표시 중 오류: {e}")
    
    def get_startup_notification_setting(self) -> bool:
        """
        시작 알림 설정 가져오기
        
        Returns:
            bool: 시작 알림을 표시할지 여부 (기본값: True)
        """
        try:
            if hasattr(self, 'saved_settings') and self.saved_settings:
                return self.saved_settings.get('show_startup_notifications', True)
            return True
        except Exception:
            return True
    
    def set_startup_notification_setting(self, enabled: bool):
        """
        시작 알림 설정 저장
        
        Args:
            enabled: 시작 알림 활성화 여부
        """
        try:
            if not hasattr(self, 'saved_settings'):
                self.saved_settings = {}
            
            self.saved_settings['show_startup_notifications'] = enabled
            self.save_window_settings()
            
        except Exception as e:
            print(f"시작 알림 설정 저장 중 오류: {e}")
    
    def run(self):
        """GUI 애플리케이션 실행"""
        try:
            # 시작 시 알림 체크 (UI가 완전히 로드된 후)
            self.root.after(100, self.check_and_show_startup_notification)
            
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("치명적 오류", f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")