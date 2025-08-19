#!/usr/bin/env python3
"""
목표 날짜 관련 GUI 컴포넌트들의 데모 스크립트

새로 구현된 DueDateLabel, UrgencyIndicator, DateTimeWidget, QuickDateButtons 컴포넌트들을 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from gui.components import DueDateLabel, UrgencyIndicator, DateTimeWidget, QuickDateButtons


class DueDateComponentsDemo:
    """목표 날짜 컴포넌트들 데모 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("목표 날짜 GUI 컴포넌트 데모")
        self.root.geometry("800x600")
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 노트북 (탭)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 각 컴포넌트별 탭 생성
        self.setup_due_date_label_tab(notebook)
        self.setup_urgency_indicator_tab(notebook)
        self.setup_datetime_widget_tab(notebook)
        self.setup_quick_date_buttons_tab(notebook)
        self.setup_combined_demo_tab(notebook)
    
    def setup_due_date_label_tab(self, notebook):
        """DueDateLabel 컴포넌트 데모 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="DueDateLabel")
        
        # 제목
        ttk.Label(frame, text="DueDateLabel 컴포넌트 데모", 
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # 다양한 상태의 DueDateLabel들
        examples_frame = ttk.LabelFrame(frame, text="다양한 상태 예시")
        examples_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 지연된 할일
        overdue_frame = ttk.Frame(examples_frame)
        overdue_frame.pack(fill=tk.X, pady=5)
        ttk.Label(overdue_frame, text="지연된 할일:", width=15).pack(side=tk.LEFT)
        overdue_date = datetime.now() - timedelta(days=2)
        DueDateLabel(overdue_frame, due_date=overdue_date).pack(side=tk.LEFT)
        
        # 긴급한 할일 (24시간 이내)
        urgent_frame = ttk.Frame(examples_frame)
        urgent_frame.pack(fill=tk.X, pady=5)
        ttk.Label(urgent_frame, text="긴급한 할일:", width=15).pack(side=tk.LEFT)
        urgent_date = datetime.now() + timedelta(hours=12)
        DueDateLabel(urgent_frame, due_date=urgent_date).pack(side=tk.LEFT)
        
        # 경고 할일 (3일 이내)
        warning_frame = ttk.Frame(examples_frame)
        warning_frame.pack(fill=tk.X, pady=5)
        ttk.Label(warning_frame, text="경고 할일:", width=15).pack(side=tk.LEFT)
        warning_date = datetime.now() + timedelta(days=2)
        DueDateLabel(warning_frame, due_date=warning_date).pack(side=tk.LEFT)
        
        # 일반 할일
        normal_frame = ttk.Frame(examples_frame)
        normal_frame.pack(fill=tk.X, pady=5)
        ttk.Label(normal_frame, text="일반 할일:", width=15).pack(side=tk.LEFT)
        normal_date = datetime.now() + timedelta(days=7)
        DueDateLabel(normal_frame, due_date=normal_date).pack(side=tk.LEFT)
        
        # 완료된 할일
        completed_frame = ttk.Frame(examples_frame)
        completed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(completed_frame, text="완료된 할일:", width=15).pack(side=tk.LEFT)
        completed_date = datetime.now() + timedelta(days=1)
        completed_at = datetime.now() - timedelta(hours=2)
        DueDateLabel(completed_frame, due_date=completed_date, completed_at=completed_at).pack(side=tk.LEFT)
        
        # 목표 날짜 없음
        no_date_frame = ttk.Frame(examples_frame)
        no_date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(no_date_frame, text="목표 날짜 없음:", width=15).pack(side=tk.LEFT)
        DueDateLabel(no_date_frame, due_date=None).pack(side=tk.LEFT)
        
        # 동적 업데이트 테스트
        dynamic_frame = ttk.LabelFrame(frame, text="동적 업데이트 테스트")
        dynamic_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.dynamic_label = DueDateLabel(dynamic_frame, due_date=datetime.now() + timedelta(hours=1))
        self.dynamic_label.pack(pady=10)
        
        buttons_frame = ttk.Frame(dynamic_frame)
        buttons_frame.pack(pady=5)
        
        ttk.Button(buttons_frame, text="1시간 후로 설정", 
                  command=lambda: self.update_dynamic_label(timedelta(hours=1))).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="1일 후로 설정", 
                  command=lambda: self.update_dynamic_label(timedelta(days=1))).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="완료로 표시", 
                  command=self.mark_dynamic_completed).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="목표 날짜 제거", 
                  command=lambda: self.dynamic_label.set_due_date(None)).pack(side=tk.LEFT, padx=5)
    
    def update_dynamic_label(self, delta):
        """동적 레이블 업데이트"""
        new_date = datetime.now() + delta
        self.dynamic_label.set_due_date(new_date)
    
    def mark_dynamic_completed(self):
        """동적 레이블을 완료로 표시"""
        self.dynamic_label.set_due_date(self.dynamic_label.get_due_date(), datetime.now())
    
    def setup_urgency_indicator_tab(self, notebook):
        """UrgencyIndicator 컴포넌트 데모 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="UrgencyIndicator")
        
        # 제목
        ttk.Label(frame, text="UrgencyIndicator 컴포넌트 데모", 
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # 긴급도별 인디케이터
        indicators_frame = ttk.LabelFrame(frame, text="긴급도별 인디케이터")
        indicators_frame.pack(fill=tk.X, padx=20, pady=10)
        
        urgency_levels = [
            ('overdue', '지연됨'),
            ('urgent', '긴급'),
            ('warning', '경고'),
            ('normal', '일반')
        ]
        
        for level, description in urgency_levels:
            level_frame = ttk.Frame(indicators_frame)
            level_frame.pack(fill=tk.X, pady=5)
            
            UrgencyIndicator(level_frame, urgency_level=level).pack(side=tk.LEFT)
            ttk.Label(level_frame, text=f"{description} ({level})").pack(side=tk.LEFT, padx=10)
        
        # 접근성 패턴 포함 인디케이터
        accessibility_frame = ttk.LabelFrame(frame, text="접근성 패턴 포함")
        accessibility_frame.pack(fill=tk.X, padx=20, pady=10)
        
        for level, description in urgency_levels:
            level_frame = ttk.Frame(accessibility_frame)
            level_frame.pack(fill=tk.X, pady=5)
            
            UrgencyIndicator(level_frame, urgency_level=level, show_pattern=True).pack(side=tk.LEFT)
            ttk.Label(level_frame, text=f"{description} (패턴 포함)").pack(side=tk.LEFT, padx=10)
        
        # 동적 변경 테스트
        dynamic_frame = ttk.LabelFrame(frame, text="동적 변경 테스트")
        dynamic_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.dynamic_indicator = UrgencyIndicator(dynamic_frame, urgency_level='normal', show_pattern=True)
        self.dynamic_indicator.pack(pady=10)
        
        buttons_frame = ttk.Frame(dynamic_frame)
        buttons_frame.pack(pady=5)
        
        for level, description in urgency_levels:
            ttk.Button(buttons_frame, text=description, 
                      command=lambda l=level: self.dynamic_indicator.set_urgency_level(l)).pack(side=tk.LEFT, padx=2)
    
    def setup_datetime_widget_tab(self, notebook):
        """DateTimeWidget 컴포넌트 데모 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="DateTimeWidget")
        
        # 제목
        ttk.Label(frame, text="DateTimeWidget 컴포넌트 데모", 
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # 기본 위젯
        basic_frame = ttk.LabelFrame(frame, text="기본 날짜/시간 선택")
        basic_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.datetime_widget = DateTimeWidget(basic_frame, initial_datetime=datetime.now())
        self.datetime_widget.pack(pady=10)
        
        # 선택된 값 표시
        self.selected_datetime_var = tk.StringVar()
        ttk.Label(basic_frame, text="선택된 날짜/시간:").pack()
        ttk.Label(basic_frame, textvariable=self.selected_datetime_var).pack(pady=5)
        
        # 값 가져오기 버튼
        ttk.Button(basic_frame, text="선택된 값 확인", 
                  command=self.show_selected_datetime).pack(pady=5)
        
        # 프리셋 설정 버튼들
        preset_frame = ttk.LabelFrame(frame, text="프리셋 설정")
        preset_frame.pack(fill=tk.X, padx=20, pady=10)
        
        preset_buttons_frame = ttk.Frame(preset_frame)
        preset_buttons_frame.pack(pady=10)
        
        presets = [
            ("현재 시간", datetime.now()),
            ("내일 오후 6시", datetime.now().replace(hour=18, minute=0) + timedelta(days=1)),
            ("다음 주 월요일", self.get_next_monday()),
            ("한 달 후", datetime.now() + timedelta(days=30))
        ]
        
        for name, dt in presets:
            ttk.Button(preset_buttons_frame, text=name,
                      command=lambda d=dt: self.datetime_widget.set_datetime(d)).pack(side=tk.LEFT, padx=5)
    
    def show_selected_datetime(self):
        """선택된 날짜/시간 표시"""
        selected = self.datetime_widget.get_datetime()
        if selected:
            self.selected_datetime_var.set(selected.strftime('%Y-%m-%d %H:%M'))
        else:
            self.selected_datetime_var.set("선택된 날짜 없음")
    
    def get_next_monday(self):
        """다음 월요일 날짜 반환"""
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # 월요일은 0
        if days_ahead <= 0:  # 오늘이 월요일이거나 이미 지났으면
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    def setup_quick_date_buttons_tab(self, notebook):
        """QuickDateButtons 컴포넌트 데모 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="QuickDateButtons")
        
        # 제목
        ttk.Label(frame, text="QuickDateButtons 컴포넌트 데모", 
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # 빠른 선택 버튼들
        buttons_frame = ttk.LabelFrame(frame, text="빠른 날짜 선택")
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.quick_buttons = QuickDateButtons(buttons_frame, on_date_selected=self.on_quick_date_selected)
        self.quick_buttons.pack(pady=10)
        
        # 선택된 날짜 표시
        self.quick_selected_var = tk.StringVar(value="날짜를 선택해주세요")
        ttk.Label(buttons_frame, text="선택된 날짜:").pack(pady=(10, 0))
        ttk.Label(buttons_frame, textvariable=self.quick_selected_var, 
                 font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # 업데이트 버튼 (시간이 지나면서 "오늘", "내일" 등이 변경될 수 있음)
        ttk.Button(buttons_frame, text="옵션 업데이트", 
                  command=self.quick_buttons.update_options).pack(pady=10)
    
    def on_quick_date_selected(self, selected_date):
        """빠른 날짜 선택 콜백"""
        self.quick_selected_var.set(selected_date.strftime('%Y-%m-%d %H:%M'))
        messagebox.showinfo("날짜 선택됨", f"선택된 날짜: {selected_date.strftime('%Y-%m-%d %H:%M')}")
    
    def setup_combined_demo_tab(self, notebook):
        """통합 데모 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="통합 데모")
        
        # 제목
        ttk.Label(frame, text="모든 컴포넌트 통합 데모", 
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # 할일 시뮬레이션
        todo_frame = ttk.LabelFrame(frame, text="할일 목록 시뮬레이션")
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 할일 항목들
        todos = [
            ("프로젝트 문서 작성", datetime.now() + timedelta(hours=2), False),
            ("회의 준비", datetime.now() - timedelta(hours=1), False),
            ("코드 리뷰", datetime.now() + timedelta(days=1), False),
            ("테스트 작성", datetime.now() + timedelta(days=3), True),
            ("배포 준비", datetime.now() + timedelta(days=7), False),
        ]
        
        for i, (title, due_date, is_completed) in enumerate(todos):
            todo_item_frame = ttk.Frame(todo_frame)
            todo_item_frame.pack(fill=tk.X, pady=2)
            
            # 긴급도 인디케이터
            from services.date_service import DateService
            urgency = DateService.get_urgency_level(due_date if not is_completed else None)
            UrgencyIndicator(todo_item_frame, urgency_level=urgency, show_pattern=True).pack(side=tk.LEFT)
            
            # 할일 제목
            title_label = ttk.Label(todo_item_frame, text=title, width=20)
            title_label.pack(side=tk.LEFT, padx=10)
            
            # 목표 날짜 레이블
            completed_at = datetime.now() - timedelta(minutes=30) if is_completed else None
            DueDateLabel(todo_item_frame, due_date=due_date, completed_at=completed_at).pack(side=tk.LEFT, padx=10)
        
        # 새 할일 추가 시뮬레이션
        add_frame = ttk.LabelFrame(frame, text="새 할일 추가")
        add_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 제목 입력
        title_frame = ttk.Frame(add_frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text="할일 제목:").pack(side=tk.LEFT)
        self.new_todo_title = tk.StringVar(value="새로운 할일")
        ttk.Entry(title_frame, textvariable=self.new_todo_title, width=30).pack(side=tk.LEFT, padx=10)
        
        # 빠른 날짜 선택
        quick_frame = ttk.Frame(add_frame)
        quick_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quick_frame, text="빠른 선택:").pack(anchor=tk.W)
        QuickDateButtons(quick_frame, on_date_selected=self.on_new_todo_date_selected).pack(pady=5)
        
        # 또는 직접 선택
        manual_frame = ttk.Frame(add_frame)
        manual_frame.pack(fill=tk.X, pady=5)
        ttk.Label(manual_frame, text="직접 선택:").pack(anchor=tk.W)
        self.new_todo_datetime = DateTimeWidget(manual_frame)
        self.new_todo_datetime.pack(pady=5)
        
        # 미리보기
        preview_frame = ttk.Frame(add_frame)
        preview_frame.pack(fill=tk.X, pady=10)
        ttk.Label(preview_frame, text="미리보기:").pack(side=tk.LEFT)
        
        self.preview_indicator = UrgencyIndicator(preview_frame, show_pattern=True)
        self.preview_indicator.pack(side=tk.LEFT, padx=5)
        
        self.preview_label = DueDateLabel(preview_frame)
        self.preview_label.pack(side=tk.LEFT, padx=5)
        
        # 미리보기 업데이트 버튼
        ttk.Button(preview_frame, text="미리보기 업데이트", 
                  command=self.update_preview).pack(side=tk.LEFT, padx=10)
        
        # 초기 미리보기 업데이트
        self.update_preview()
    
    def on_new_todo_date_selected(self, selected_date):
        """새 할일 날짜 선택 콜백"""
        self.new_todo_datetime.set_datetime(selected_date)
        self.update_preview()
    
    def update_preview(self):
        """미리보기 업데이트"""
        selected_date = self.new_todo_datetime.get_datetime()
        if selected_date:
            from services.date_service import DateService
            urgency = DateService.get_urgency_level(selected_date)
            self.preview_indicator.set_urgency_level(urgency)
            self.preview_label.set_due_date(selected_date)
    
    def run(self):
        """데모 실행"""
        self.root.mainloop()


if __name__ == "__main__":
    demo = DueDateComponentsDemo()
    demo.run()