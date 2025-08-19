"""
상태바 목표 날짜 정보 표시 기능 데모

Task 13: 상태바에 목표 날짜 관련 정보 표시
- 오늘 마감 할일 개수 표시 기능 구현
- 지연된 할일 개수 표시 기능 구현
- 상태바 레이아웃 조정 및 정보 업데이트 로직 구현
- 실시간 정보 업데이트 구현
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime, timedelta

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.components import StatusBar
from services.todo_service import TodoService
from services.notification_service import NotificationService
from models.todo import Todo
from models.subtask import SubTask


class StatusBarDueDateDemo:
    """상태바 목표 날짜 정보 표시 데모"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("상태바 목표 날짜 정보 표시 데모")
        self.root.geometry("800x600")
        
        # 서비스 초기화
        from services.storage_service import StorageService
        from services.file_service import FileService
        
        storage_service = StorageService("demo_data/status_bar_demo.json")
        file_service = FileService()
        self.todo_service = TodoService(storage_service, file_service)
        self.notification_service = NotificationService(self.todo_service)
        
        self.setup_demo_data()
        self.setup_ui()
        
    def setup_demo_data(self):
        """데모용 데이터 설정"""
        # 기존 데이터 클리어
        self.todo_service.todos = []
        self.todo_service.next_todo_id = 1
        self.todo_service.next_subtask_id = 1
        
        now = datetime.now()
        
        # 1. 지연된 할일 (2개) - 직접 due_date 설정 (validation 우회)
        overdue_todo1 = self.todo_service.add_todo("중요한 프로젝트 마감 (3일 지연)")
        if overdue_todo1:
            overdue_todo1.due_date = now - timedelta(days=3)
        
        overdue_todo2 = self.todo_service.add_todo("클라이언트 미팅 준비 (1일 지연)")
        if overdue_todo2:
            overdue_todo2.due_date = now - timedelta(days=1)
        
        # 2. 오늘 마감 할일 (3개) - 현재 시간보다 나중으로 설정
        today_todo1 = self.todo_service.add_todo("보고서 제출")
        if today_todo1:
            due_time1 = now.replace(hour=23, minute=59, second=0, microsecond=0)
            self.todo_service.set_todo_due_date(today_todo1.id, due_time1)
        
        today_todo2 = self.todo_service.add_todo("팀 회의 참석")
        if today_todo2:
            due_time2 = now + timedelta(hours=2)  # 2시간 후
            due_time2 = due_time2.replace(second=0, microsecond=0)
            self.todo_service.set_todo_due_date(today_todo2.id, due_time2)
        
        today_todo3 = self.todo_service.add_todo("코드 리뷰 완료")
        if today_todo3:
            due_time3 = now + timedelta(hours=4)  # 4시간 후
            due_time3 = due_time3.replace(second=0, microsecond=0)
            self.todo_service.set_todo_due_date(today_todo3.id, due_time3)
        
        # 3. 내일 마감 할일 (1개)
        tomorrow_todo = self.todo_service.add_todo("주간 계획 수립")
        if tomorrow_todo:
            self.todo_service.set_todo_due_date(tomorrow_todo.id, now + timedelta(days=1))
        
        # 4. 목표 날짜 없는 할일 (2개)
        self.todo_service.add_todo("아이디어 정리")
        self.todo_service.add_todo("새 기능 개발")
        
        # 5. 완료된 할일 (1개, 지연되었지만 완료됨)
        completed_todo = self.todo_service.add_todo("완료된 작업 (지연되었음)")
        if completed_todo:
            completed_todo.due_date = now - timedelta(days=2)
            completed_todo.mark_completed()
        
        # 데이터 저장
        self.todo_service.force_save()
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제목
        title_label = ttk.Label(main_frame, text="상태바 목표 날짜 정보 표시 데모", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 설명
        desc_text = """
이 데모는 상태바에 목표 날짜 관련 정보가 어떻게 표시되는지 보여줍니다.

현재 데모 데이터:
• 지연된 할일: 2개 (3일 지연, 1일 지연)
• 오늘 마감 할일: 3개 (보고서, 팀 회의, 코드 리뷰)
• 내일 마감 할일: 1개
• 목표 날짜 없는 할일: 2개
• 완료된 할일: 1개 (지연되었지만 완료됨)

상태바에서 확인할 수 있는 정보:
• 전체 할일 개수 및 완료율
• 오늘 마감 할일 개수 (주황색으로 표시)
• 지연된 할일 개수 (빨간색으로 표시)
• 상태 메시지에 긴급 정보 포함
        """
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 20), anchor=tk.W)
        
        # 할일 목록 표시 (간단한 리스트)
        list_frame = ttk.LabelFrame(main_frame, text="현재 할일 목록", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 스크롤 가능한 텍스트 위젯
        text_frame = ttk.Frame(list_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.todo_text = tk.Text(text_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.todo_text.yview)
        self.todo_text.configure(yscrollcommand=scrollbar.set)
        
        self.todo_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 할일 목록 업데이트
        self.update_todo_list()
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 상태바 정보 업데이트 버튼
        update_btn = ttk.Button(button_frame, text="상태바 정보 업데이트", 
                               command=self.update_status_info)
        update_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 할일 완료 토글 버튼
        toggle_btn = ttk.Button(button_frame, text="첫 번째 할일 완료 토글", 
                               command=self.toggle_first_todo)
        toggle_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 새 할일 추가 버튼
        add_btn = ttk.Button(button_frame, text="긴급 할일 추가", 
                            command=self.add_urgent_todo)
        add_btn.pack(side=tk.LEFT)
        
        # 상태바 생성
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 초기 상태바 업데이트
        self.update_status_info()
        
        # 실시간 업데이트 시작 (10초마다)
        self.start_real_time_updates()
    
    def update_todo_list(self):
        """할일 목록 텍스트 업데이트"""
        self.todo_text.delete(1.0, tk.END)
        
        todos = self.todo_service.get_all_todos()
        now = datetime.now()
        
        for i, todo in enumerate(todos, 1):
            status = "✅ 완료" if todo.is_completed() else "⏳ 진행중"
            
            if todo.due_date:
                if todo.is_overdue() and not todo.is_completed():
                    urgency = "🔴 지연"
                elif todo.due_date.date() == now.date() and not todo.is_completed():
                    urgency = "🟠 오늘 마감"
                elif todo.due_date.date() == (now + timedelta(days=1)).date() and not todo.is_completed():
                    urgency = "🟡 내일 마감"
                else:
                    urgency = "⚪ 일반"
                
                due_text = todo.due_date.strftime("%Y-%m-%d %H:%M")
                time_info = todo.get_time_remaining_text()
            else:
                urgency = "⚪ 일반"
                due_text = "목표 날짜 없음"
                time_info = ""
            
            todo_info = f"{i}. {todo.title}\n"
            todo_info += f"   상태: {status} | 긴급도: {urgency}\n"
            todo_info += f"   목표 날짜: {due_text}\n"
            if time_info:
                todo_info += f"   시간 정보: {time_info}\n"
            todo_info += "\n"
            
            self.todo_text.insert(tk.END, todo_info)
    
    def update_status_info(self):
        """상태바 정보 업데이트"""
        # 전체 할일 정보
        todos = self.todo_service.get_all_todos()
        total_todos = len(todos)
        completed_todos = sum(1 for todo in todos if todo.is_completed())
        
        # 목표 날짜 관련 정보
        status_summary = self.notification_service.get_status_bar_summary()
        due_today_count = status_summary['due_today']
        overdue_count = status_summary['overdue']
        
        # 상태바 업데이트
        self.status_bar.update_todo_count(total_todos, completed_todos)
        self.status_bar.update_due_date_info(due_today_count, overdue_count)
        
        # 상태 메시지 업데이트
        if total_todos == 0:
            status_msg = "할일이 없습니다"
        elif completed_todos == total_todos:
            status_msg = "모든 할일이 완료되었습니다! 🎉"
        else:
            remaining = total_todos - completed_todos
            status_parts = [f"{remaining}개의 할일이 남아있습니다"]
            
            if overdue_count > 0:
                status_parts.append(f"⚠️ {overdue_count}개 지연")
            elif due_today_count > 0:
                status_parts.append(f"📅 {due_today_count}개 오늘 마감")
            
            status_msg = " | ".join(status_parts)
        
        self.status_bar.update_status(status_msg)
        self.status_bar.update_last_saved(f"업데이트: {datetime.now().strftime('%H:%M:%S')}")
        
        # 할일 목록도 업데이트
        self.update_todo_list()
    
    def toggle_first_todo(self):
        """첫 번째 할일 완료 상태 토글"""
        todos = self.todo_service.get_all_todos()
        if todos:
            first_todo = todos[0]
            if first_todo.is_completed():
                first_todo.mark_uncompleted()
            else:
                first_todo.mark_completed()
            
            # 데이터 저장
            self.todo_service.force_save()
            
            # 상태바 업데이트
            self.update_status_info()
    
    def add_urgent_todo(self):
        """긴급 할일 추가 (2시간 후 마감)"""
        now = datetime.now()
        urgent_due = now + timedelta(hours=2)
        
        todo = self.todo_service.add_todo(f"긴급 작업 ({now.strftime('%H:%M')} 추가)")
        if todo:
            self.todo_service.set_todo_due_date(todo.id, urgent_due)
            self.update_status_info()
    
    def start_real_time_updates(self):
        """실시간 업데이트 시작"""
        self.update_status_info()
        # 10초마다 업데이트
        self.root.after(10000, self.start_real_time_updates)
    
    def run(self):
        """데모 실행"""
        print("상태바 목표 날짜 정보 표시 데모를 시작합니다...")
        print("\n상태바에서 확인할 수 있는 정보:")
        print("• 할일: X개 - 전체 할일 개수")
        print("• 완료율: X% - 완료된 할일 비율")
        print("• 오늘 마감: X개 - 오늘 마감인 할일 개수 (주황색)")
        print("• 지연: X개 - 지연된 할일 개수 (빨간색)")
        print("• 상태 메시지 - 긴급 정보 포함")
        print("\n버튼을 사용하여 상태 변경을 테스트해보세요!")
        
        self.root.mainloop()


if __name__ == "__main__":
    demo = StatusBarDueDateDemo()
    demo.run()