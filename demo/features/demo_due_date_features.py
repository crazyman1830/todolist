#!/usr/bin/env python3
"""
목표 날짜 기능 종합 데모
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import tempfile
from datetime import datetime, timedelta
from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService
from services.date_service import DateService
from services.notification_service import NotificationService
from utils.date_utils import DateUtils


def demo_date_parsing_and_formatting():
    """날짜 파싱 및 포맷팅 데모"""
    print("=" * 50)
    print("1. 날짜 파싱 및 포맷팅 데모")
    print("=" * 50)
    
    date_service = DateService()
    
    # 다양한 형식의 날짜 문자열 테스트
    test_dates = [
        "2024-12-25",
        "2024/12/25",
        "12/25/2024",
        "25-12-2024",
        "오늘",
        "내일",
        "다음주"
    ]
    
    for date_str in test_dates:
        try:
            parsed = date_service.parse_date_string(date_str)
            formatted = date_service.format_date(parsed)
            relative = DateUtils.format_relative_time(parsed)
            print(f"입력: '{date_str}' -> 파싱: {parsed.strftime('%Y-%m-%d %H:%M')} -> 포맷: {formatted} -> 상대: {relative}")
        except Exception as e:
            print(f"입력: '{date_str}' -> 오류: {e}")


def demo_urgency_calculation():
    """긴급도 계산 데모"""
    print("\n" + "=" * 50)
    print("2. 긴급도 계산 데모")
    print("=" * 50)
    
    now = datetime.now()
    test_dates = [
        ("지연된 할일", now - timedelta(days=2)),
        ("오늘 마감", now.replace(hour=23, minute=59)),
        ("내일 마감", now + timedelta(days=1)),
        ("이번 주 마감", now + timedelta(days=3)),
        ("다음 주 마감", now + timedelta(days=7)),
        ("한 달 후", now + timedelta(days=30))
    ]
    
    for title, due_date in test_dates:
        urgency = DateUtils.get_urgency_level(due_date)
        remaining = DateUtils.format_relative_time(due_date)
        print(f"{title}: {urgency} ({remaining})")


def demo_todo_service_with_dates():
    """TodoService 목표 날짜 기능 데모"""
    print("\n" + "=" * 50)
    print("3. TodoService 목표 날짜 기능 데모")
    print("=" * 50)
    
    # 임시 서비스 설정
    temp_data_file = "demo_date_todos.json"
    temp_folders_dir = "demo_date_folders"
    
    storage_service = StorageService(temp_data_file)
    file_service = FileService(temp_folders_dir)
    todo_service = TodoService(storage_service, file_service)
    
    try:
        # 다양한 목표 날짜를 가진 할일들 생성
        now = datetime.now()
        
        todo1 = todo_service.add_todo("지연된 프로젝트")
        todo_service.update_todo(todo1.id, todo1.title, now - timedelta(days=1))
        
        todo2 = todo_service.add_todo("오늘 마감 보고서")
        todo_service.update_todo(todo2.id, todo2.title, now.replace(hour=18, minute=0))
        
        todo3 = todo_service.add_todo("내일 회의 준비")
        todo_service.update_todo(todo3.id, todo3.title, now + timedelta(days=1))
        
        todo4 = todo_service.add_todo("목표 날짜 없는 할일")
        
        # 할일 목록 조회 및 표시
        todos = todo_service.get_all_todos()
        print(f"총 {len(todos)}개의 할일:")
        
        for todo in todos:
            if todo.due_date:
                urgency = DateUtils.get_urgency_level(todo.due_date)
                relative = DateUtils.format_relative_time(todo.due_date)
                print(f"  • {todo.title} - {urgency} ({relative})")
            else:
                print(f"  • {todo.title} - 목표 날짜 없음")
        
        # 긴급도별 필터링 데모
        print("\n긴급도별 필터링:")
        overdue_todos = todo_service.get_todos_by_urgency("overdue")
        due_today_todos = todo_service.get_todos_by_urgency("due_today")
        
        print(f"  지연된 할일: {len(overdue_todos)}개")
        for todo in overdue_todos:
            print(f"    - {todo.title}")
        
        print(f"  오늘 마감 할일: {len(due_today_todos)}개")
        for todo in due_today_todos:
            print(f"    - {todo.title}")
        
    finally:
        # 정리
        try:
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
            if os.path.exists(temp_folders_dir):
                import shutil
                shutil.rmtree(temp_folders_dir, ignore_errors=True)
        except:
            pass


def demo_notification_service():
    """NotificationService 데모"""
    print("\n" + "=" * 50)
    print("4. 알림 서비스 데모")
    print("=" * 50)
    
    # 임시 서비스 설정
    temp_data_file = "demo_notification_todos.json"
    temp_folders_dir = "demo_notification_folders"
    
    storage_service = StorageService(temp_data_file)
    file_service = FileService(temp_folders_dir)
    todo_service = TodoService(storage_service, file_service)
    notification_service = NotificationService(todo_service)
    
    try:
        # 알림 대상 할일들 생성
        now = datetime.now()
        
        # 지연된 할일
        todo1 = todo_service.add_todo("지연된 중요 작업")
        todo_service.update_todo(todo1.id, todo1.title, now - timedelta(days=2))
        
        # 오늘 마감 할일
        todo2 = todo_service.add_todo("오늘 마감 작업")
        todo_service.update_todo(todo2.id, todo2.title, now.replace(hour=23, minute=59))
        
        # 일반 할일
        todo3 = todo_service.add_todo("일반 작업")
        todo_service.update_todo(todo3.id, todo3.title, now + timedelta(days=7))
        
        # 알림 상태 확인
        should_notify = notification_service.should_show_startup_notification()
        print(f"시작 알림 표시 여부: {should_notify}")
        
        # 상태바 요약 정보
        summary = notification_service.get_status_bar_summary()
        print(f"상태 요약:")
        print(f"  • 지연된 할일: {summary['overdue']}개")
        print(f"  • 오늘 마감: {summary['due_today']}개")
        print(f"  • 긴급 할일: {summary['urgent']}개")
        print(f"  • 전체 할일: {summary['total']}개")
        print(f"  • 완료된 할일: {summary['completed']}개")
        
    finally:
        # 정리
        try:
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
            if os.path.exists(temp_folders_dir):
                import shutil
                shutil.rmtree(temp_folders_dir, ignore_errors=True)
        except:
            pass


def main():
    """메인 데모 함수"""
    print("Todo List 애플리케이션 - 목표 날짜 기능 종합 데모")
    print("=" * 80)
    
    try:
        demo_date_parsing_and_formatting()
        demo_urgency_calculation()
        demo_todo_service_with_dates()
        demo_notification_service()
        
        print("\n" + "=" * 80)
        print("🎉 목표 날짜 기능 데모 완료!")
        print("=" * 80)
        print("구현된 기능:")
        print("• 다양한 형식의 날짜 입력 지원")
        print("• 긴급도 자동 계산 및 분류")
        print("• 상대적 시간 표시 (예: '2일 전', '3시간 후')")
        print("• 목표 날짜 기반 정렬 및 필터링")
        print("• 알림 및 상태 요약 기능")
        print("• 데이터 지속성 및 호환성")
        
    except Exception as e:
        print(f"데모 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()