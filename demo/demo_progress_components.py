"""
진행률 표시 및 시각적 피드백 컴포넌트 데모
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from gui.components import (
    ProgressBar, SearchBox, FilterPanel, StatusBar, 
    TodoProgressWidget, CompactProgressBar
)
from models.todo import Todo
from models.subtask import SubTask


def create_demo_window():
    """데모 윈도우 생성"""
    root = tk.Tk()
    root.title("진행률 컴포넌트 데모")
    root.geometry("800x600")
    
    # 메인 프레임
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 1. ProgressBar 데모
    progress_frame = ttk.LabelFrame(main_frame, text="ProgressBar 데모")
    progress_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 여러 진행률의 프로그레스 바들
    progress_bars = []
    progress_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    progress_labels = ["0% (시작 안함)", "25% (빨간색)", "50% (노란색)", "75% (초록색)", "100% (완료)"]
    
    for i, (value, label) in enumerate(zip(progress_values, progress_labels)):
        frame = ttk.Frame(progress_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(frame, text=label, width=20).pack(side=tk.LEFT)
        
        progress_bar = ProgressBar(frame, length=200)
        progress_bar.pack(side=tk.LEFT, padx=(10, 0))
        progress_bar.set_progress(value)
        progress_bars.append(progress_bar)
    
    # 2. CompactProgressBar 데모
    compact_frame = ttk.LabelFrame(main_frame, text="CompactProgressBar 데모")
    compact_frame.pack(fill=tk.X, pady=(0, 10))
    
    compact_bars = []
    for i, (value, label) in enumerate(zip(progress_values, progress_labels)):
        frame = ttk.Frame(compact_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(frame, text=label, width=20).pack(side=tk.LEFT)
        
        compact_bar = CompactProgressBar(frame, progress=value, width=150, height=16)
        compact_bar.pack(side=tk.LEFT, padx=(10, 0))
        compact_bars.append(compact_bar)
    
    # 3. TodoProgressWidget 데모
    todo_frame = ttk.LabelFrame(main_frame, text="TodoProgressWidget 데모")
    todo_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 샘플 할일들
    todos_data = [
        ("프로젝트 계획 수립", 0.0),
        ("요구사항 분석", 0.3),
        ("설계 문서 작성", 0.6),
        ("코딩 작업", 0.9),
        ("테스트 완료", 1.0)
    ]
    
    todo_widgets = []
    for title, progress in todos_data:
        widget = TodoProgressWidget(todo_frame, title, progress)
        widget.pack(fill=tk.X, padx=5, pady=2)
        todo_widgets.append(widget)
    
    # 4. SearchBox 데모
    search_frame = ttk.LabelFrame(main_frame, text="SearchBox 데모")
    search_frame.pack(fill=tk.X, pady=(0, 10))
    
    search_result_var = tk.StringVar(value="검색 결과가 여기에 표시됩니다")
    search_result_label = ttk.Label(search_frame, textvariable=search_result_var)
    search_result_label.pack(pady=5)
    
    def on_search(term):
        if term:
            search_result_var.set(f"검색어: '{term}'")
        else:
            search_result_var.set("검색 결과가 여기에 표시됩니다")
    
    search_box = SearchBox(search_frame, on_search)
    search_box.pack(pady=5)
    
    # 5. FilterPanel 데모
    filter_frame = ttk.LabelFrame(main_frame, text="FilterPanel 데모")
    filter_frame.pack(fill=tk.X, pady=(0, 10))
    
    filter_result_var = tk.StringVar(value="필터 옵션이 여기에 표시됩니다")
    filter_result_label = ttk.Label(filter_frame, textvariable=filter_result_var)
    filter_result_label.pack(pady=5)
    
    def on_filter(options):
        result = f"완료된 할일 표시: {options['show_completed']}, 정렬: {options['sort_by']} ({options['sort_order']})"
        filter_result_var.set(result)
    
    filter_panel = FilterPanel(filter_frame, on_filter)
    filter_panel.pack(pady=5)
    
    # 6. StatusBar 데모
    status_frame = ttk.LabelFrame(main_frame, text="StatusBar 데모")
    status_frame.pack(fill=tk.X, pady=(0, 10))
    
    status_bar = StatusBar(status_frame)
    status_bar.pack(fill=tk.X)
    
    # 상태바 업데이트
    status_bar.update_todo_count(10, 6)
    status_bar.update_status("데모 실행 중...")
    status_bar.update_last_saved("방금 전")
    
    # 7. 실시간 업데이트 데모
    control_frame = ttk.LabelFrame(main_frame, text="실시간 업데이트 데모")
    control_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 진행률 조절 슬라이더
    progress_var = tk.DoubleVar(value=0.5)
    
    def update_progress(*args):
        value = progress_var.get()
        # 모든 프로그레스 바 업데이트
        for bar in progress_bars:
            bar.set_progress(value)
        for bar in compact_bars:
            bar.update_progress(value)
        for widget in todo_widgets:
            widget.update_progress(value)
        
        # 상태바 업데이트
        completed = int(value * 10)
        status_bar.update_todo_count(10, completed)
        status_bar.update_status(f"진행률: {int(value * 100)}%")
    
    ttk.Label(control_frame, text="진행률 조절:").pack(side=tk.LEFT, padx=5)
    progress_scale = ttk.Scale(
        control_frame, 
        from_=0.0, 
        to=1.0, 
        variable=progress_var,
        orient=tk.HORIZONTAL,
        length=200,
        command=update_progress
    )
    progress_scale.pack(side=tk.LEFT, padx=5)
    
    progress_label = ttk.Label(control_frame, text="50%")
    progress_label.pack(side=tk.LEFT, padx=5)
    
    def update_label(*args):
        progress_label.config(text=f"{int(progress_var.get() * 100)}%")
    
    progress_var.trace('w', update_label)
    
    return root


def main():
    """메인 함수"""
    print("진행률 표시 및 시각적 피드백 컴포넌트 데모를 시작합니다...")
    
    root = create_demo_window()
    
    print("데모 윈도우가 열렸습니다. 다양한 컴포넌트들을 테스트해보세요:")
    print("- 진행률 바의 색상 변화 확인")
    print("- 검색 박스에서 실시간 검색 테스트")
    print("- 필터 패널에서 옵션 변경 테스트")
    print("- 하단의 슬라이더로 실시간 진행률 업데이트 테스트")
    
    root.mainloop()


if __name__ == "__main__":
    main()