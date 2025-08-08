"""
GUI 컴포넌트 모듈 - 재사용 가능한 GUI 컴포넌트들
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any


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
        
        # 정렬 기준 선택
        ttk.Label(self, text="정렬:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_combo = ttk.Combobox(
            self, 
            textvariable=self.sort_by_var,
            values=["created_at", "title", "progress"],
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
    
    def setup_events(self) -> None:
        """이벤트 바인딩 설정"""
        # 필터 옵션 변경 시 콜백 호출
        self.show_completed_var.trace('w', self._on_filter_change)
        self.sort_by_var.trace('w', self._on_filter_change)
        self.sort_order_var.trace('w', self._on_filter_change)
    
    def _on_filter_change(self, *args) -> None:
        """필터 옵션 변경 시"""
        if self.on_filter_callback:
            self.on_filter_callback(self.get_filter_options())
    
    def get_filter_options(self) -> Dict[str, Any]:
        """현재 필터 옵션 반환"""
        return {
            'show_completed': self.show_completed_var.get(),
            'sort_by': self.sort_by_var.get(),
            'sort_order': self.sort_order_var.get()
        }
    
    def reset_filters(self) -> None:
        """필터 옵션 리셋"""
        self.show_completed_var.set(True)
        self.sort_by_var.set("created_at")
        self.sort_order_var.set("desc")


class StatusBar(ttk.Frame):
    """상태바 컴포넌트"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
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
    
    def __init__(self, parent, progress: float = 0.0, width: int = 80, height: int = 16, **kwargs):
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
                               highlightthickness=0, bd=0)
        self.canvas.pack()
        
        # 배경 사각형
        self.bg_rect = self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill='lightgray', outline='gray', width=1
        )
        
        # 진행률 사각형
        self.progress_rect = self.canvas.create_rectangle(
            0, 0, 0, self.height,
            fill='red', outline=''
        )
        
        # 진행률 텍스트
        self.progress_text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text="0%", fill='black', font=('Arial', 8)
        )
    
    def update_progress(self, progress: float) -> None:
        """진행률 업데이트"""
        if not 0.0 <= progress <= 1.0:
            return
        
        self.progress = progress
        percentage = int(progress * 100)
        
        # 진행률 바 너비 계산
        progress_width = int(self.width * progress)
        
        # 진행률 사각형 업데이트
        self.canvas.coords(self.progress_rect, 0, 0, progress_width, self.height)
        
        # 진행률에 따른 색상 변경
        if progress == 0:
            color = 'lightgray'
        elif progress < 0.34:
            color = 'red'
        elif progress < 0.67:
            color = 'orange'
        elif progress < 1.0:
            color = 'green'
        else:
            color = 'darkgreen'
        
        self.canvas.itemconfig(self.progress_rect, fill=color)
        
        # 진행률 텍스트 업데이트
        self.canvas.itemconfig(self.progress_text, text=f"{percentage}%")
        
        # 텍스트 색상 조정 (진행률이 높을 때 가독성 향상)
        text_color = 'white' if progress > 0.5 else 'black'
        self.canvas.itemconfig(self.progress_text, fill=text_color)
    
    def get_progress(self) -> float:
        """현재 진행률 반환"""
        return self.progress