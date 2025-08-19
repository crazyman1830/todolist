"""
GUI 컴포넌트 모듈 - 재사용 가능한 GUI 컴포넌트들
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
from services.date_service import DateService
from utils.color_utils import ColorUtils


class ProgressBar(ttk.Progressbar):
    """진행률 표시를 위한 커스텀 프로그레스 바 컴포넌트"""
    
    def __init__(self, parent, **kwargs):
        # 기본 설정
        default_kwargs = {
            'mode': 'determinate',
            'length': 100,
            'maximum': 100
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        # 현재 진행률 저장
        self._current_progress = 0.0
        
        # 색상 스타일 설정
        self.setup_styles()
    
    def setup_styles(self) -> None:
        """진행률에 따른 색상 스타일 설정"""
        style = ttk.Style()
        
        # 빨간색 (0-33%)
        style.configure("Red.Horizontal.TProgressbar", 
                       foreground='red', 
                       background='red',
                       troughcolor='lightgray')
        
        # 노란색 (34-66%)
        style.configure("Yellow.Horizontal.TProgressbar", 
                       foreground='orange', 
                       background='orange',
                       troughcolor='lightgray')
        
        # 초록색 (67-100%)
        style.configure("Green.Horizontal.TProgressbar", 
                       foreground='green', 
                       background='green',
                       troughcolor='lightgray')
        
        # 완료 (100%)
        style.configure("Complete.Horizontal.TProgressbar", 
                       foreground='darkgreen', 
                       background='darkgreen',
                       troughcolor='lightgray')
    
    def set_progress(self, value: float) -> None:
        """진행률 설정 (0.0 ~ 1.0)"""
        if not 0.0 <= value <= 1.0:
            raise ValueError("Progress value must be between 0.0 and 1.0")
        
        self._current_progress = value
        percentage = value * 100
        
        # 프로그레스 바 값 설정
        self['value'] = percentage
        
        # 진행률에 따른 색상 변경
        self._update_color(percentage)
    
    def _update_color(self, percentage: float) -> None:
        """진행률에 따른 색상 업데이트"""
        if percentage == 0:
            # 진행률이 0%인 경우 기본 스타일
            self.configure(style="TProgressbar")
        elif percentage < 34:
            # 빨간색 (0-33%)
            self.configure(style="Red.Horizontal.TProgressbar")
        elif percentage < 67:
            # 노란색 (34-66%)
            self.configure(style="Yellow.Horizontal.TProgressbar")
        elif percentage < 100:
            # 초록색 (67-99%)
            self.configure(style="Green.Horizontal.TProgressbar")
        else:
            # 완료 (100%)
            self.configure(style="Complete.Horizontal.TProgressbar")
    
    def get_progress(self) -> float:
        """현재 진행률 반환 (0.0 ~ 1.0)"""
        return self._current_progress
    
    def set_color(self, color: str) -> None:
        """수동으로 색상 설정"""
        style = ttk.Style()
        custom_style = f"Custom.{color}.Horizontal.TProgressbar"
        style.configure(custom_style, 
                       foreground=color, 
                       background=color,
                       troughcolor='lightgray')
        self.configure(style=custom_style)


class SearchBox(ttk.Frame):
    """검색 기능을 위한 검색 박스 컴포넌트"""
    
    def __init__(self, parent, on_search_callback: Callable[[str], None], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_search_callback = on_search_callback
        self.search_var = tk.StringVar()
        
        self.setup_ui()
        self.setup_events()
    
    def setup_ui(self) -> None:
        """UI 구성 요소 설정"""
        # 검색 레이블
        self.search_label = ttk.Label(self, text="검색:")
        self.search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 검색 입력 필드
        self.search_entry = ttk.Entry(self, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 검색 버튼
        self.search_button = ttk.Button(self, text="검색", command=self._on_search_button)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 클리어 버튼
        self.clear_button = ttk.Button(self, text="지우기", command=self.clear)
        self.clear_button.pack(side=tk.LEFT)
    
    def setup_events(self) -> None:
        """이벤트 바인딩 설정"""
        # 실시간 검색을 위한 변수 추적
        self.search_var.trace('w', self._on_search_change)
        
        # Enter 키로 검색
        self.search_entry.bind('<Return>', lambda e: self._on_search_button())
        
        # Escape 키로 클리어
        self.search_entry.bind('<Escape>', lambda e: self.clear())
    
    def _on_search_change(self, *args) -> None:
        """검색어 변경 시 실시간 검색"""
        search_term = self.search_var.get()
        if self.on_search_callback:
            self.on_search_callback(search_term)
    
    def _on_search_button(self) -> None:
        """검색 버튼 클릭 시"""
        search_term = self.search_var.get()
        if self.on_search_callback:
            self.on_search_callback(search_term)
    
    def get_search_term(self) -> str:
        """현재 검색어 반환"""
        return self.search_var.get()
    
    def clear(self) -> None:
        """검색어 클리어"""
        self.search_var.set("")
        self.search_entry.focus()


class FilterPanel(ttk.Frame):
    """필터링 기능을 위한 필터 패널 컴포넌트"""
    
    def __init__(self, parent, on_filter_callback: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_filter_callback = on_filter_callback
        
        # 필터 옵션 변수들
        self.show_completed_var = tk.BooleanVar(value=True)
        self.sort_by_var = tk.StringVar(value="created_at")
        self.sort_order_var = tk.StringVar(value="desc")
        self.due_date_filter_var = tk.StringVar(value="all")  # 새로운 목표 날짜 필터
        
        self.setup_ui()
        self.setup_events()
    
    def setup_ui(self) -> None:
        """UI 구성 요소 설정"""
        # 완료된 할일 표시 체크박스
        self.show_completed_check = ttk.Checkbutton(
            self, 
            text="완료된 할일 표시", 
            variable=self.show_completed_var
        )
        self.show_completed_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # 목표 날짜 필터 선택
        ttk.Label(self, text="필터:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.due_date_filter_combo = ttk.Combobox(
            self,
            textvariable=self.due_date_filter_var,
            values=["all", "due_today", "overdue", "this_week"],
            state="readonly",
            width=12
        )
        self.due_date_filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 정렬 기준 선택
        ttk.Label(self, text="정렬:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_combo = ttk.Combobox(
            self, 
            textvariable=self.sort_by_var,
            values=["created_at", "title", "progress", "due_date"],
            state="readonly",
            width=10
        )
        self.sort_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # 정렬 순서 선택
        self.sort_order_combo = ttk.Combobox(
            self,
            textvariable=self.sort_order_var,
            values=["asc", "desc"],
            state="readonly",
            width=8
        )
        self.sort_order_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 필터 리셋 버튼
        self.reset_button = ttk.Button(self, text="리셋", command=self.reset_filters)
        self.reset_button.pack(side=tk.LEFT)
        
        # 콤보박스 값 표시 설정
        self._setup_combo_display_values()
    
    def setup_events(self) -> None:
        """이벤트 바인딩 설정"""
        # 필터 옵션 변경 시 콜백 호출
        self.show_completed_var.trace('w', self._on_filter_change)
        self.sort_by_var.trace('w', self._on_filter_change)
        self.sort_order_var.trace('w', self._on_filter_change)
        self.due_date_filter_var.trace('w', self._on_filter_change)
    
    def _on_filter_change(self, *args) -> None:
        """필터 옵션 변경 시"""
        if self.on_filter_callback:
            self.on_filter_callback(self.get_filter_options())
    
    def get_filter_options(self) -> Dict[str, Any]:
        """현재 필터 옵션 반환"""
        return {
            'show_completed': self.show_completed_var.get(),
            'sort_by': self.sort_by_var.get(),
            'sort_order': self.sort_order_var.get(),
            'due_date_filter': self.due_date_filter_var.get()
        }
    
    def reset_filters(self) -> None:
        """필터 옵션 리셋"""
        self.show_completed_var.set(True)
        self.sort_by_var.set("created_at")
        self.sort_order_var.set("desc")
        self.due_date_filter_var.set("all")
    
    def _setup_combo_display_values(self) -> None:
        """콤보박스 표시 값 설정"""
        # 목표 날짜 필터 표시 값 매핑
        self.due_date_filter_display = {
            "all": "전체",
            "due_today": "오늘 마감",
            "overdue": "지연된 할일",
            "this_week": "이번 주"
        }
        
        # 정렬 기준 표시 값 매핑
        self.sort_by_display = {
            "created_at": "생성일",
            "title": "제목",
            "progress": "진행률",
            "due_date": "목표 날짜"
        }
        
        # 정렬 순서 표시 값 매핑
        self.sort_order_display = {
            "asc": "오름차순",
            "desc": "내림차순"
        }
        
        # 콤보박스 바인딩 이벤트 설정
        self.due_date_filter_combo.bind('<<ComboboxSelected>>', self._on_combo_selected)
        self.sort_combo.bind('<<ComboboxSelected>>', self._on_combo_selected)
        self.sort_order_combo.bind('<<ComboboxSelected>>', self._on_combo_selected)
    
    def _on_combo_selected(self, event=None) -> None:
        """콤보박스 선택 시 처리"""
        # 선택된 값에 따라 표시 업데이트는 필요시 구현
        pass


class StatusBar(ttk.Frame):
    """상태바 컴포넌트"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 목표 날짜 관련 정보 저장
        self._due_today_count = 0
        self._overdue_count = 0
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """UI 구성 요소 설정"""
        # 상태바 구분선
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(side=tk.TOP, fill=tk.X)
        
        # 상태 정보 프레임
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 왼쪽 상태 정보
        self.left_frame = ttk.Frame(self.status_frame)
        self.left_frame.pack(side=tk.LEFT)
        
        # 할일 개수 표시
        self.todo_count_label = ttk.Label(self.left_frame, text="할일: 0개")
        self.todo_count_label.pack(side=tk.LEFT)
        
        # 구분선
        ttk.Label(self.left_frame, text=" | ").pack(side=tk.LEFT)
        
        # 완료율 표시
        self.completion_label = ttk.Label(self.left_frame, text="완료율: 0%")
        self.completion_label.pack(side=tk.LEFT)
        
        # 구분선
        ttk.Label(self.left_frame, text=" | ").pack(side=tk.LEFT)
        
        # 오늘 마감 할일 개수 표시
        self.due_today_label = ttk.Label(self.left_frame, text="오늘 마감: 0개", foreground="gray")
        self.due_today_label.pack(side=tk.LEFT)
        
        # 구분선
        ttk.Label(self.left_frame, text=" | ").pack(side=tk.LEFT)
        
        # 지연된 할일 개수 표시
        self.overdue_label = ttk.Label(self.left_frame, text="지연: 0개", foreground="gray")
        self.overdue_label.pack(side=tk.LEFT)
        
        # 구분선
        ttk.Label(self.left_frame, text=" | ").pack(side=tk.LEFT)
        
        # 상태 메시지
        self.status_message_label = ttk.Label(self.left_frame, text="준비")
        self.status_message_label.pack(side=tk.LEFT)
        
        # 오른쪽 상태 정보
        self.right_frame = ttk.Frame(self.status_frame)
        self.right_frame.pack(side=tk.RIGHT)
        
        # 마지막 저장 시간
        self.last_saved_label = ttk.Label(self.right_frame, text="")
        self.last_saved_label.pack(side=tk.RIGHT)
    
    def update_status(self, message: str) -> None:
        """상태 메시지 업데이트"""
        self.status_message_label.config(text=message)
    
    def update_todo_count(self, total: int, completed: int) -> None:
        """할일 개수 및 완료율 업데이트"""
        self.todo_count_label.config(text=f"할일: {total}개")
        
        if total == 0:
            completion_rate = 0
        else:
            completion_rate = (completed / total) * 100
        
        self.completion_label.config(text=f"완료율: {completion_rate:.1f}%")
    
    def update_due_date_info(self, due_today_count: int, overdue_count: int) -> None:
        """목표 날짜 관련 정보 업데이트
        
        Requirements 8.1, 8.2: 오늘 마감 할일 개수와 지연된 할일 개수 표시
        
        Args:
            due_today_count: 오늘 마감인 할일 개수
            overdue_count: 지연된 할일 개수
        """
        self._due_today_count = due_today_count
        self._overdue_count = overdue_count
        
        # 오늘 마감 할일 표시 업데이트
        if due_today_count > 0:
            self.due_today_label.config(
                text=f"오늘 마감: {due_today_count}개",
                foreground="orange"
            )
        else:
            self.due_today_label.config(
                text="오늘 마감: 0개",
                foreground="gray"
            )
        
        # 지연된 할일 표시 업데이트
        if overdue_count > 0:
            self.overdue_label.config(
                text=f"지연: {overdue_count}개",
                foreground="red"
            )
        else:
            self.overdue_label.config(
                text="지연: 0개",
                foreground="gray"
            )
    
    def get_due_date_info(self) -> Dict[str, int]:
        """현재 목표 날짜 정보 반환
        
        Returns:
            Dict[str, int]: 목표 날짜 관련 정보
        """
        return {
            'due_today': self._due_today_count,
            'overdue': self._overdue_count
        }
    
    def update_last_saved(self, message: str) -> None:
        """마지막 저장 시간 업데이트"""
        self.last_saved_label.config(text=message)


class TodoProgressWidget(ttk.Frame):
    """할일별 진행률을 표시하는 위젯"""
    
    def __init__(self, parent, todo_title: str, progress: float = 0.0, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.todo_title = todo_title
        self.progress = progress
        
        self.setup_ui()
        self.update_progress(progress)
    
    def setup_ui(self) -> None:
        """UI 구성 요소 설정"""
        # 할일 제목 레이블
        self.title_label = ttk.Label(self, text=self.todo_title)
        self.title_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 진행률 바
        self.progress_bar = ProgressBar(self, length=100)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 5))
        
        # 진행률 텍스트
        self.progress_label = ttk.Label(self, text="0%")
        self.progress_label.pack(side=tk.LEFT)
    
    def update_progress(self, progress: float) -> None:
        """진행률 업데이트"""
        self.progress = progress
        self.progress_bar.set_progress(progress)
        
        percentage = int(progress * 100)
        self.progress_label.config(text=f"{percentage}%")
        
        # 완료된 할일의 경우 제목에 시각적 효과 적용
        if progress >= 1.0:
            self.title_label.config(foreground='gray')
            # tkinter에서는 취소선을 직접 지원하지 않으므로 텍스트로 표현
            if not self.todo_title.startswith("✓"):
                self.title_label.config(text=f"✓ {self.todo_title}")
        else:
            self.title_label.config(foreground='black')
            # 완료 표시 제거
            if self.todo_title.startswith("✓"):
                clean_title = self.todo_title[2:]  # "✓ " 제거
                self.title_label.config(text=clean_title)
    
    def set_title(self, title: str) -> None:
        """할일 제목 설정"""
        self.todo_title = title
        self.title_label.config(text=title)
        # 진행률에 따른 시각적 효과 재적용
        self.update_progress(self.progress)


class CompactProgressBar(ttk.Frame):
    """트리뷰에서 사용할 수 있는 컴팩트한 진행률 표시 위젯"""
    
    def __init__(self, parent, progress: float = 0.0, width: int = 100, height: int = 16, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.progress = progress
        self.width = width
        self.height = height
        
        self.setup_ui()
        self.update_progress(progress)
    
    def setup_ui(self) -> None:
        """UI 구성 요소 설정"""
        # 캔버스를 사용하여 커스텀 진행률 바 구현
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, 
                               highlightthickness=0, bd=0, bg='white')
        self.canvas.pack()
        
        # 배경 사각형 (둥근 모서리 효과)
        self.bg_rect = self.canvas.create_rectangle(
            1, 1, self.width-1, self.height-1,
            fill='#f0f0f0', outline='#d0d0d0', width=1
        )
        
        # 진행률 사각형
        self.progress_rect = self.canvas.create_rectangle(
            2, 2, 2, self.height-2,
            fill='#e0e0e0', outline='', width=0
        )
        
        # 진행률 텍스트
        self.progress_text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text="0%", fill='#666666', font=('Arial', 8, 'bold')
        )
    
    def update_progress(self, progress: float) -> None:
        """진행률 업데이트"""
        if not 0.0 <= progress <= 1.0:
            return
        
        self.progress = progress
        percentage = int(progress * 100)
        
        # 진행률 바 너비 계산 (여백 고려)
        progress_width = max(2, int((self.width - 4) * progress) + 2)
        
        # 진행률 사각형 업데이트
        self.canvas.coords(self.progress_rect, 2, 2, progress_width, self.height-2)
        
        # 진행률에 따른 색상 변경 (더 부드러운 색상)
        if progress == 0:
            color = '#e0e0e0'
            text_color = '#999999'
        elif progress < 0.34:
            color = '#ff6b6b'  # 부드러운 빨간색
            text_color = 'white'
        elif progress < 0.67:
            color = '#ffa726'  # 부드러운 주황색
            text_color = 'white'
        elif progress < 1.0:
            color = '#66bb6a'  # 부드러운 초록색
            text_color = 'white'
        else:
            color = '#4caf50'  # 완료 - 진한 초록색
            text_color = 'white'
        
        self.canvas.itemconfig(self.progress_rect, fill=color)
        
        # 진행률 텍스트 업데이트
        self.canvas.itemconfig(self.progress_text, text=f"{percentage}%", fill=text_color)
        
        # 진행률이 0%일 때는 텍스트를 회색으로
        if progress == 0:
            self.canvas.itemconfig(self.progress_text, fill='#999999')
    
    def get_progress(self) -> float:
        """현재 진행률 반환"""
        return self.progress


class DueDateLabel(ttk.Label):
    """목표 날짜를 표시하는 커스텀 레이블"""
    
    def __init__(self, parent, due_date: Optional[datetime] = None, 
                 completed_at: Optional[datetime] = None, **kwargs):
        """
        목표 날짜 표시 레이블 초기화
        
        Requirements 2.1, 2.2: 목표 날짜 표시 및 상대적 시간 표시
        
        Args:
            parent: 부모 위젯
            due_date: 목표 날짜
            completed_at: 완료 날짜
            **kwargs: 추가 레이블 옵션
        """
        super().__init__(parent, **kwargs)
        self.due_date = due_date
        self.completed_at = completed_at
        self.update_display()
    
    def update_display(self) -> None:
        """표시 내용 업데이트"""
        if self.due_date is None:
            self.config(text="", foreground='gray')
            return
        
        # 시간 표시 텍스트 생성
        time_text = DateService.get_time_remaining_text(self.due_date, self.completed_at)
        date_text = DateService.format_due_date(self.due_date, 'relative')
        
        # 완료된 경우
        if self.completed_at is not None:
            self.config(text=f"✓ {time_text}", foreground='gray')
            self._create_tooltip("완료됨")
            return
        
        # 긴급도에 따른 색상 설정
        urgency_level = DateService.get_urgency_level(self.due_date)
        color = ColorUtils.get_urgency_color(urgency_level)
        
        # 접근성을 위한 아이콘 추가
        patterns = ColorUtils.get_accessibility_patterns()
        symbols = ColorUtils.get_accessibility_symbols()
        pattern = patterns.get(urgency_level, '')
        symbol = symbols.get(urgency_level, '')
        
        # 표시 텍스트 결합 (아이콘과 심볼 포함)
        display_text = f"{pattern} {symbol} {date_text}"
        if time_text and time_text != date_text:
            display_text += f" ({time_text})"
        
        self.config(text=display_text, foreground=color)
        
        # 접근성 툴팁 추가
        descriptions = ColorUtils.get_accessibility_descriptions()
        description = descriptions.get(urgency_level, '')
        if description:
            tooltip_text = f"{description}\n목표 날짜: {date_text}"
            if time_text and time_text != date_text:
                tooltip_text += f"\n{time_text}"
            self._create_tooltip(tooltip_text)
    
    def set_due_date(self, due_date: Optional[datetime], 
                    completed_at: Optional[datetime] = None) -> None:
        """목표 날짜 설정"""
        self.due_date = due_date
        self.completed_at = completed_at
        self.update_display()
    
    def get_due_date(self) -> Optional[datetime]:
        """목표 날짜 반환"""
        return self.due_date
    
    def _create_tooltip(self, text: str):
        """툴팁 생성
        
        Requirements: 툴팁 및 도움말 메시지 추가
        """
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9),
                           justify=tk.LEFT)
            label.pack()
            
            # 3초 후 자동 사라짐
            tooltip.after(3000, tooltip.destroy)
            
            # 마우스가 위젯을 벗어나면 즉시 사라짐
            def hide_tooltip(event):
                tooltip.destroy()
            
            self.bind('<Leave>', hide_tooltip, add='+')
        
        self.bind('<Enter>', show_tooltip, add='+')


class UrgencyIndicator(ttk.Frame):
    """긴급도를 시각적으로 표시하는 위젯"""
    
    def __init__(self, parent, urgency_level: str = 'normal', 
                 show_pattern: bool = False, **kwargs):
        """
        긴급도 표시 위젯 초기화
        
        Requirements 2.3: 긴급도 시각적 표시
        
        Args:
            parent: 부모 위젯
            urgency_level: 긴급도 레벨
            show_pattern: 접근성을 위한 패턴 표시 여부
            **kwargs: 추가 프레임 옵션
        """
        super().__init__(parent, **kwargs)
        self.urgency_level = urgency_level
        self.show_pattern = show_pattern
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """긴급도 표시 UI 구성"""
        # 색상 인디케이터 (작은 원형)
        self.canvas = tk.Canvas(self, width=16, height=16, 
                               highlightthickness=0, bd=0, bg='white')
        self.canvas.pack(side=tk.LEFT, padx=(0, 5))
        
        # 패턴 레이블 (접근성용) - 항상 표시하도록 변경
        self.pattern_label = ttk.Label(self, text="", font=('Arial', 8))
        self.pattern_label.pack(side=tk.LEFT, padx=(0, 2))
        
        # 텍스트 심볼 레이블 (색맹 사용자용)
        if self.show_pattern:
            self.symbol_label = ttk.Label(self, text="", font=('Arial', 8, 'bold'))
            self.symbol_label.pack(side=tk.LEFT)
        
        self.update_indicator()
    
    def update_indicator(self) -> None:
        """인디케이터 업데이트"""
        # 캔버스 클리어
        self.canvas.delete("all")
        
        # 긴급도에 따른 색상
        color = ColorUtils.get_urgency_color(self.urgency_level)
        
        # 원형 인디케이터 그리기
        if self.urgency_level != 'normal':
            self.canvas.create_oval(2, 2, 14, 14, fill=color, outline=color)
        else:
            # 일반 상태는 빈 원
            self.canvas.create_oval(2, 2, 14, 14, fill='white', outline='lightgray')
        
        # 패턴 표시 (접근성) - 항상 표시
        patterns = ColorUtils.get_accessibility_patterns()
        pattern = patterns.get(self.urgency_level, '')
        self.pattern_label.config(text=pattern)
        
        # 텍스트 심볼 표시 (색맹 사용자용)
        if self.show_pattern and hasattr(self, 'symbol_label'):
            symbols = ColorUtils.get_accessibility_symbols()
            symbol = symbols.get(self.urgency_level, '')
            self.symbol_label.config(text=symbol, foreground=color)
        
        # 툴팁 설정 (접근성 설명)
        descriptions = ColorUtils.get_accessibility_descriptions()
        description = descriptions.get(self.urgency_level, '')
        if description:
            self._create_tooltip(description)
    
    def set_urgency_level(self, level: str) -> None:
        """긴급도 레벨 설정"""
        self.urgency_level = level
        self.update_indicator()
    
    def get_urgency_level(self) -> str:
        """현재 긴급도 레벨 반환"""
        return self.urgency_level
    
    def _create_tooltip(self, text: str):
        """툴팁 생성
        
        Requirements: 툴팁 및 도움말 메시지 추가
        """
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
            
            self.bind('<Leave>', hide_tooltip, add='+')
        
        self.bind('<Enter>', show_tooltip, add='+')


class DateTimeWidget(ttk.Frame):
    """날짜/시간 선택을 위한 복합 위젯"""
    
    def __init__(self, parent, initial_datetime: Optional[datetime] = None, **kwargs):
        """
        날짜/시간 선택 위젯 초기화
        
        Requirements 6.1: 날짜/시간 선택 인터페이스
        
        Args:
            parent: 부모 위젯
            initial_datetime: 초기 날짜/시간
            **kwargs: 추가 프레임 옵션
        """
        super().__init__(parent, **kwargs)
        self.datetime_value = initial_datetime or datetime.now()
        
        # 날짜/시간 변수들
        self.date_var = tk.StringVar()
        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        
        self.setup_ui()
        self.set_datetime(self.datetime_value)
    
    def setup_ui(self) -> None:
        """날짜/시간 선택 UI 구성"""
        # 날짜 선택 프레임
        date_frame = ttk.Frame(self)
        date_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(date_frame, text="날짜:").pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 시간 선택 프레임
        time_frame = ttk.Frame(self)
        time_frame.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="시간:").pack(side=tk.LEFT)
        
        # 시간 스핀박스
        self.hour_spin = ttk.Spinbox(time_frame, textvariable=self.hour_var,
                                    from_=0, to=23, width=3, format="%02.0f")
        self.hour_spin.pack(side=tk.LEFT, padx=(5, 2))
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        # 분 스핀박스
        self.minute_spin = ttk.Spinbox(time_frame, textvariable=self.minute_var,
                                      from_=0, to=59, width=3, format="%02.0f")
        self.minute_spin.pack(side=tk.LEFT, padx=(2, 0))
        
        # 이벤트 바인딩
        self.date_entry.bind('<FocusOut>', self._on_date_change)
        self.hour_var.trace('w', self._on_time_change)
        self.minute_var.trace('w', self._on_time_change)
    
    def _on_date_change(self, event=None) -> None:
        """날짜 변경 이벤트 처리"""
        try:
            date_str = self.date_var.get()
            # 간단한 날짜 형식 파싱 (YYYY-MM-DD 또는 MM/DD)
            if '/' in date_str:
                month, day = map(int, date_str.split('/'))
                year = datetime.now().year
                new_date = datetime(year, month, day)
            else:
                new_date = datetime.fromisoformat(date_str)
            
            # 시간 정보 유지
            self.datetime_value = new_date.replace(
                hour=int(self.hour_var.get() or 0),
                minute=int(self.minute_var.get() or 0)
            )
        except (ValueError, TypeError):
            # 잘못된 입력시 현재 값 유지
            self.set_datetime(self.datetime_value)
    
    def _on_time_change(self, *args) -> None:
        """시간 변경 이벤트 처리"""
        try:
            hour = int(self.hour_var.get() or 0)
            minute = int(self.minute_var.get() or 0)
            self.datetime_value = self.datetime_value.replace(hour=hour, minute=minute)
        except (ValueError, TypeError):
            pass
    
    def get_datetime(self) -> Optional[datetime]:
        """선택된 날짜/시간 반환"""
        return self.datetime_value
    
    def set_datetime(self, dt: Optional[datetime]) -> None:
        """날짜/시간 설정"""
        if dt is None:
            dt = datetime.now()
        
        self.datetime_value = dt
        self.date_var.set(dt.strftime('%Y-%m-%d'))
        self.hour_var.set(f"{dt.hour:02d}")
        self.minute_var.set(f"{dt.minute:02d}")


class QuickDateButtons(ttk.Frame):
    """빠른 날짜 선택 버튼들"""
    
    def __init__(self, parent, on_date_selected: Callable[[datetime], None], **kwargs):
        """
        빠른 날짜 선택 버튼 위젯 초기화
        
        Requirements 6.2: 빠른 날짜 선택 옵션
        
        Args:
            parent: 부모 위젯
            on_date_selected: 날짜 선택 시 호출될 콜백 함수
            **kwargs: 추가 프레임 옵션
        """
        super().__init__(parent, **kwargs)
        self.on_date_selected = on_date_selected
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """빠른 선택 버튼들 구성"""
        # 빠른 날짜 옵션 가져오기
        quick_options = DateService.get_quick_date_options()
        
        # 첫 번째 행: 오늘, 내일, 모레
        row1_frame = ttk.Frame(self)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        for option_name in ["오늘", "내일", "모레"]:
            if option_name in quick_options:
                btn = ttk.Button(row1_frame, text=option_name,
                               command=lambda opt=option_name: self._on_button_click(opt))
                btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 두 번째 행: 이번 주말, 다음 주
        row2_frame = ttk.Frame(self)
        row2_frame.pack(fill=tk.X, pady=(0, 5))
        
        for option_name in ["이번 주말", "다음 주"]:
            if option_name in quick_options:
                btn = ttk.Button(row2_frame, text=option_name,
                               command=lambda opt=option_name: self._on_button_click(opt))
                btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 세 번째 행: 1주일 후, 1개월 후
        row3_frame = ttk.Frame(self)
        row3_frame.pack(fill=tk.X)
        
        for option_name in ["1주일 후", "1개월 후"]:
            if option_name in quick_options:
                btn = ttk.Button(row3_frame, text=option_name,
                               command=lambda opt=option_name: self._on_button_click(opt))
                btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def _on_button_click(self, option_name: str) -> None:
        """빠른 선택 버튼 클릭 처리"""
        quick_options = DateService.get_quick_date_options()
        if option_name in quick_options and self.on_date_selected:
            selected_date = quick_options[option_name]
            self.on_date_selected(selected_date)
    
    def update_options(self) -> None:
        """옵션 업데이트 (시간이 지나면서 날짜가 변경될 수 있음)"""
        # 기존 버튼들 제거
        for widget in self.winfo_children():
            widget.destroy()
        
        # UI 재구성
        self.setup_ui()