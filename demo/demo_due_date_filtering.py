"""
목표 날짜 필터링 및 정렬 기능 데모

Requirements 4.1, 4.2, 4.3, 4.4: 목표 날짜 기반 필터링 및 정렬 데모
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
import tempfile
from datetime import datetime, timedelta
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from gui.components import FilterPanel
from gui.todo_tree import TodoTree


class DueDateFilteringDemo:
    """목표 날짜 필터링 데모 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("목표 날짜 필터링 및 정렬 데모")
        self.root.geometry("900x700")
        
        # 임시 데이터 설정
        self.setup_test_data()
        
        # UI 구성
        self.setup_ui()
        
        # 초기 데이터 로드
        self.refresh_display()
    
    def setup_test_data(self):
        """테스트용 데이터 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, "demo_todos.json")
        
        # 서비스 초기화
        self.file_service = FileService()
        self.storage_service = StorageService(self.data_file)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 데모용 할일 생성
        self.create_demo_todos()
    
    def create_demo_todos(self):
        """데모용 할일들 생성"""
        now = datetime.now()
        
        # 1. 지연된 할일들 - 직접 데이터 조작으로 과거 날짜 설정
        overdue1 = self.todo_service.add_todo("🔴 중요한 프로젝트 마감 (3일 지연)")
        overdue2 = self.todo_service.add_todo("🔴 클라이언트 미팅 준비 (1일 지연)")
        
        # 과거 날짜 직접 설정
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            if todo.id == overdue1.id:
                todo.due_date = now - timedelta(days=3)
            elif todo.id == overdue2.id:
                todo.due_date = now - timedelta(days=1)
        self.storage_service.save_todos_with_auto_save(todos)
        self.todo_service.clear_cache()
        
        # 2. 오늘 마감 할일들
        today1 = self.todo_service.add_todo("🟡 보고서 제출")
        today_due = now.replace(hour=23, minute=30, second=0, microsecond=0)
        if today_due > now:
            self.todo_service.set_todo_due_date(today1.id, today_due)
        else:
            # 이미 지난 시간이면 내일로 설정
            today_due = (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
            self.todo_service.set_todo_due_date(today1.id, today_due)
        
        today2 = self.todo_service.add_todo("🟡 팀 회의 참석")
        today_due2 = now.replace(hour=23, minute=45, second=0, microsecond=0)
        if today_due2 > now:
            self.todo_service.set_todo_due_date(today2.id, today_due2)
        else:
            # 이미 지난 시간이면 내일로 설정
            today_due2 = (now + timedelta(days=1)).replace(hour=14, minute=30, second=0, microsecond=0)
            self.todo_service.set_todo_due_date(today2.id, today_due2)
        
        # 3. 이번 주 마감 할일들
        week1 = self.todo_service.add_todo("📋 주간 계획 수립")
        self.todo_service.set_todo_due_date(week1.id, now + timedelta(days=2))
        
        week2 = self.todo_service.add_todo("📋 코드 리뷰 완료")
        self.todo_service.set_todo_due_date(week2.id, now + timedelta(days=4))
        
        # 4. 다음 주 이후 할일들
        future1 = self.todo_service.add_todo("🟢 새 기능 개발")
        self.todo_service.set_todo_due_date(future1.id, now + timedelta(days=10))
        
        future2 = self.todo_service.add_todo("🟢 문서화 작업")
        self.todo_service.set_todo_due_date(future2.id, now + timedelta(days=15))
        
        # 5. 목표 날짜 없는 할일들
        no_due1 = self.todo_service.add_todo("⚪ 아이디어 정리")
        no_due2 = self.todo_service.add_todo("⚪ 학습 자료 수집")
        
        # 6. 완료된 할일 (지연되었지만 완료됨)
        completed = self.todo_service.add_todo("✅ 완료된 작업 (지연되었음)")
        # 하위 작업 추가하고 완료 처리
        subtask = self.todo_service.add_subtask(completed.id, "완료된 하위작업")
        self.todo_service.toggle_subtask_completion(completed.id, subtask.id)
        
        # 완료된 할일에 과거 날짜 설정
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            if todo.id == completed.id:
                todo.due_date = now - timedelta(days=2)
                break
        self.storage_service.save_todos_with_auto_save(todos)
        self.todo_service.clear_cache()
        
        # 일부 할일에 하위 작업 추가
        subtask1 = self.todo_service.add_subtask(overdue1.id, "요구사항 분석")
        subtask2 = self.todo_service.add_subtask(overdue1.id, "설계 문서 작성")
        
        # 하위 작업에 과거 날짜 설정
        todos = self.todo_service.get_all_todos()
        for todo in todos:
            if todo.id == overdue1.id:
                for subtask in todo.subtasks:
                    if subtask.id == subtask1.id:
                        subtask.due_date = now - timedelta(days=4)
                    elif subtask.id == subtask2.id:
                        subtask.due_date = now - timedelta(days=2)
                break
        self.storage_service.save_todos_with_auto_save(todos)
        self.todo_service.clear_cache()
        
        # 하위 작업 일부 완료
        self.todo_service.toggle_subtask_completion(overdue1.id, subtask1.id)
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제목
        title_label = ttk.Label(main_frame, text="목표 날짜 필터링 및 정렬 데모", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 설명
        desc_text = """
이 데모는 목표 날짜 기반 필터링 및 정렬 기능을 보여줍니다:
• 필터: 전체, 오늘 마감, 지연된 할일, 이번 주
• 정렬: 생성일, 제목, 진행률, 목표 날짜
• 완료된 할일 표시/숨기기 옵션
        """
        desc_label = ttk.Label(main_frame, text=desc_text.strip(), 
                              justify=tk.LEFT, font=('Arial', 10))
        desc_label.pack(pady=(0, 10))
        
        # 필터 패널
        self.filter_panel = FilterPanel(main_frame, self.on_filter_change)
        self.filter_panel.pack(fill=tk.X, pady=(0, 10))
        
        # 트리 뷰 프레임
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # TodoTree 생성
        self.todo_tree = TodoTree(tree_frame, self.todo_service)
        
        # 상태 정보 프레임
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="", font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT)
        
        # 새로고침 버튼
        refresh_btn = ttk.Button(status_frame, text="새로고침", command=self.refresh_display)
        refresh_btn.pack(side=tk.RIGHT)
        
        # 통계 정보 표시
        self.stats_label = ttk.Label(status_frame, text="", font=('Arial', 9), foreground='gray')
        self.stats_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def on_filter_change(self, filter_options):
        """필터 변경 이벤트 핸들러"""
        try:
            # 필터링 및 정렬 적용
            due_date_filter = filter_options.get('due_date_filter', 'all')
            sort_by = filter_options['sort_by']
            show_completed = filter_options['show_completed']
            sort_order = filter_options['sort_order']
            
            # 통합 필터링 및 정렬
            filtered_todos = self.todo_service.get_filtered_and_sorted_todos(
                filter_type=due_date_filter,
                sort_by=sort_by,
                show_completed=show_completed
            )
            
            # 정렬 순서 적용
            if sort_order == 'desc':
                filtered_todos.reverse()
            
            # 트리 뷰 업데이트
            self.todo_tree.populate_tree(filtered_todos)
            
            # 상태 정보 업데이트
            self.update_status(filter_options, len(filtered_todos))
            
        except Exception as e:
            self.status_label.config(text=f"오류: {str(e)}")
    
    def update_status(self, filter_options, count):
        """상태 정보 업데이트"""
        # 필터 정보
        filter_names = {
            'all': '전체',
            'due_today': '오늘 마감',
            'overdue': '지연된 할일',
            'this_week': '이번 주'
        }
        
        sort_names = {
            'created_at': '생성일',
            'title': '제목',
            'progress': '진행률',
            'due_date': '목표 날짜'
        }
        
        order_names = {
            'asc': '오름차순',
            'desc': '내림차순'
        }
        
        filter_name = filter_names.get(filter_options.get('due_date_filter', 'all'), '전체')
        sort_name = sort_names.get(filter_options['sort_by'], '생성일')
        order_name = order_names.get(filter_options['sort_order'], '내림차순')
        completed_text = "포함" if filter_options['show_completed'] else "제외"
        
        status_text = f"필터: {filter_name} | 정렬: {sort_name} ({order_name}) | 완료된 할일: {completed_text} | 결과: {count}개"
        self.status_label.config(text=status_text)
        
        # 통계 정보 업데이트
        self.update_statistics()
    
    def update_statistics(self):
        """통계 정보 업데이트"""
        try:
            all_todos = self.todo_service.get_all_todos()
            overdue_count = len(self.todo_service.get_overdue_todos())
            due_today_count = len(self.todo_service.get_due_today_todos())
            completed_count = len([t for t in all_todos if t.is_completed()])
            
            stats_text = f"전체: {len(all_todos)}개 | 지연: {overdue_count}개 | 오늘 마감: {due_today_count}개 | 완료: {completed_count}개"
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            self.stats_label.config(text=f"통계 오류: {str(e)}")
    
    def refresh_display(self):
        """화면 새로고침"""
        # 현재 필터 옵션으로 다시 필터링
        filter_options = self.filter_panel.get_filter_options()
        self.on_filter_change(filter_options)
    
    def run(self):
        """데모 실행"""
        try:
            self.root.mainloop()
        finally:
            # 정리 작업
            self.cleanup()
    
    def cleanup(self):
        """정리 작업"""
        try:
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            if os.path.exists(self.test_dir):
                os.rmdir(self.test_dir)
        except Exception as e:
            print(f"정리 작업 중 오류: {e}")


def main():
    """메인 함수"""
    print("목표 날짜 필터링 및 정렬 데모를 시작합니다...")
    print("\n데모 기능:")
    print("1. 목표 날짜 기반 필터링 (전체, 오늘 마감, 지연된 할일, 이번 주)")
    print("2. 다양한 정렬 옵션 (생성일, 제목, 진행률, 목표 날짜)")
    print("3. 완료된 할일 표시/숨기기")
    print("4. 실시간 통계 정보 표시")
    print("\n필터와 정렬 옵션을 변경해보세요!")
    
    demo = DueDateFilteringDemo()
    demo.run()


if __name__ == "__main__":
    main()