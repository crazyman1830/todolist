"""
목표 날짜 설정 다이얼로그 데모

DueDateDialog의 기능을 수동으로 테스트할 수 있는 데모 프로그램입니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from gui.dialogs import show_due_date_dialog, show_startup_notification_dialog


class DueDateDialogDemo:
    """목표 날짜 다이얼로그 데모 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("목표 날짜 다이얼로그 데모")
        self.root.geometry("400x300")
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(
            main_frame, 
            text="목표 날짜 다이얼로그 데모", 
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 테스트 버튼들
        buttons = [
            ("새 할일 목표 날짜 설정", self.test_new_todo_due_date),
            ("기존 할일 목표 날짜 수정", self.test_edit_todo_due_date),
            ("하위작업 목표 날짜 설정", self.test_subtask_due_date),
            ("하위작업 목표 날짜 (충돌)", self.test_subtask_due_date_conflict),
            ("과거 날짜 설정 테스트", self.test_past_due_date),
            ("시작 알림 다이얼로그", self.test_startup_notification),
            ("종료", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(main_frame, text=text, command=command)
            btn.pack(fill=tk.X, pady=2)
        
        # 결과 표시 영역
        result_frame = ttk.LabelFrame(main_frame, text="결과", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log_result(self, message):
        """결과 로그"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.result_text.see(tk.END)
    
    def test_new_todo_due_date(self):
        """새 할일 목표 날짜 설정 테스트"""
        self.log_result("새 할일 목표 날짜 설정 다이얼로그 열기...")
        
        result = show_due_date_dialog(self.root, item_type="할일")
        
        if result:
            self.log_result(f"선택된 날짜: {result.strftime('%Y-%m-%d %H:%M')}")
        else:
            self.log_result("목표 날짜가 설정되지 않았습니다.")
    
    def test_edit_todo_due_date(self):
        """기존 할일 목표 날짜 수정 테스트"""
        current_due_date = datetime.now() + timedelta(days=3, hours=2)
        
        self.log_result(f"기존 목표 날짜: {current_due_date.strftime('%Y-%m-%d %H:%M')}")
        self.log_result("할일 목표 날짜 수정 다이얼로그 열기...")
        
        result = show_due_date_dialog(self.root, current_due_date=current_due_date, item_type="할일")
        
        if result:
            self.log_result(f"수정된 날짜: {result.strftime('%Y-%m-%d %H:%M')}")
        else:
            self.log_result("목표 날짜가 제거되었습니다.")
    
    def test_subtask_due_date(self):
        """하위작업 목표 날짜 설정 테스트"""
        parent_due_date = datetime.now() + timedelta(days=7)
        
        self.log_result(f"상위 할일 목표 날짜: {parent_due_date.strftime('%Y-%m-%d %H:%M')}")
        self.log_result("하위작업 목표 날짜 설정 다이얼로그 열기...")
        
        result = show_due_date_dialog(
            self.root, 
            parent_due_date=parent_due_date, 
            item_type="하위작업"
        )
        
        if result:
            self.log_result(f"선택된 날짜: {result.strftime('%Y-%m-%d %H:%M')}")
            if result > parent_due_date:
                self.log_result("⚠️ 경고: 하위작업 목표 날짜가 상위 할일보다 늦습니다!")
        else:
            self.log_result("목표 날짜가 설정되지 않았습니다.")
    
    def test_subtask_due_date_conflict(self):
        """하위작업 목표 날짜 충돌 테스트"""
        parent_due_date = datetime.now() + timedelta(days=2)
        current_subtask_due = parent_due_date + timedelta(days=1)  # 상위보다 늦음
        
        self.log_result(f"상위 할일 목표 날짜: {parent_due_date.strftime('%Y-%m-%d %H:%M')}")
        self.log_result(f"현재 하위작업 목표 날짜: {current_subtask_due.strftime('%Y-%m-%d %H:%M')} (충돌!)")
        self.log_result("하위작업 목표 날짜 수정 다이얼로그 열기...")
        
        result = show_due_date_dialog(
            self.root,
            current_due_date=current_subtask_due,
            parent_due_date=parent_due_date,
            item_type="하위작업"
        )
        
        if result:
            self.log_result(f"수정된 날짜: {result.strftime('%Y-%m-%d %H:%M')}")
            if result > parent_due_date:
                self.log_result("⚠️ 경고: 여전히 상위 할일보다 늦습니다!")
            else:
                self.log_result("✅ 충돌이 해결되었습니다.")
        else:
            self.log_result("목표 날짜가 제거되었습니다.")
    
    def test_past_due_date(self):
        """과거 날짜 설정 테스트"""
        past_date = datetime.now() - timedelta(hours=3)
        
        self.log_result(f"과거 날짜로 설정 시도: {past_date.strftime('%Y-%m-%d %H:%M')}")
        self.log_result("과거 날짜 설정 다이얼로그 열기...")
        
        result = show_due_date_dialog(self.root, current_due_date=past_date, item_type="할일")
        
        if result:
            self.log_result(f"설정된 날짜: {result.strftime('%Y-%m-%d %H:%M')}")
        else:
            self.log_result("목표 날짜가 설정되지 않았습니다.")
    
    def test_startup_notification(self):
        """시작 알림 다이얼로그 테스트"""
        self.log_result("시작 알림 다이얼로그 열기...")
        
        # 테스트 데이터
        overdue_count = 2
        due_today_count = 3
        
        result = show_startup_notification_dialog(self.root, overdue_count, due_today_count)
        
        self.log_result(f"알림 결과: {result}")
        if result.get('dont_show_again'):
            self.log_result("사용자가 '다시 보지 않기'를 선택했습니다.")
    
    def run(self):
        """데모 실행"""
        self.log_result("목표 날짜 다이얼로그 데모를 시작합니다.")
        self.log_result("위의 버튼들을 클릭하여 다양한 시나리오를 테스트해보세요.")
        self.root.mainloop()


if __name__ == "__main__":
    demo = DueDateDialogDemo()
    demo.run()