#!/usr/bin/env python3
"""
시작 시 알림 다이얼로그 통합 데모

Task 14 구현을 실제로 테스트하는 데모 스크립트
"""

import sys
import os
import json
import tempfile
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TODOS_FILE, TODO_FOLDERS_DIR
from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService
from gui.main_window import MainWindow


def create_test_data_with_due_dates():
    """목표 날짜가 있는 테스트 데이터 생성"""
    print("테스트 데이터 생성 중...")
    
    # 임시 데이터 파일 생성
    temp_data_file = "demo_startup_notification_data.json"
    temp_folders_dir = "demo_startup_notification_folders"
    
    # 테스트 할일 데이터 생성
    now = datetime.now()
    test_todos = [
        {
            "id": 1,
            "title": "지연된 중요한 프로젝트",
            "created_at": (now - timedelta(days=5)).isoformat(),
            "due_date": (now - timedelta(days=2)).isoformat(),  # 2일 지연
            "completed_at": None,
            "folder_path": f"{temp_folders_dir}/todo_1_지연된_중요한_프로젝트",
            "is_expanded": True,
            "subtasks": []
        },
        {
            "id": 2,
            "title": "오늘 마감인 보고서 작성",
            "created_at": (now - timedelta(days=3)).isoformat(),
            "due_date": now.replace(hour=18, minute=0, second=0, microsecond=0).isoformat(),  # 오늘 마감
            "completed_at": None,
            "folder_path": f"{temp_folders_dir}/todo_2_오늘_마감인_보고서_작성",
            "is_expanded": True,
            "subtasks": []
        },
        {
            "id": 3,
            "title": "내일 마감인 회의 준비",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "due_date": (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
            "completed_at": None,
            "folder_path": f"{temp_folders_dir}/todo_3_내일_마감인_회의_준비",
            "is_expanded": True,
            "subtasks": []
        },
        {
            "id": 4,
            "title": "완료된 할일",
            "created_at": (now - timedelta(days=7)).isoformat(),
            "due_date": (now - timedelta(days=1)).isoformat(),
            "completed_at": (now - timedelta(hours=2)).isoformat(),  # 완료됨
            "folder_path": f"{temp_folders_dir}/todo_4_완료된_할일",
            "is_expanded": True,
            "subtasks": []
        }
    ]
    
    # 데이터 파일 저장
    data = {
        "todos": test_todos,
        "next_todo_id": 5,
        "next_subtask_id": 1
    }
    
    with open(temp_data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"테스트 데이터 파일 생성: {temp_data_file}")
    print(f"- 지연된 할일: 1개")
    print(f"- 오늘 마감 할일: 1개")
    print(f"- 내일 마감 할일: 1개")
    print(f"- 완료된 할일: 1개")
    
    return temp_data_file, temp_folders_dir


def demo_startup_notification():
    """시작 시 알림 데모 실행"""
    print("="*60)
    print("시작 시 알림 다이얼로그 통합 데모")
    print("="*60)
    
    try:
        # 테스트 데이터 생성
        temp_data_file, temp_folders_dir = create_test_data_with_due_dates()
        
        print("\n1. 서비스 초기화...")
        
        # 서비스 초기화
        storage_service = StorageService(temp_data_file)
        file_service = FileService(temp_folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        print("2. GUI 애플리케이션 시작...")
        print("   - 시작 시 알림이 표시될 예정입니다")
        print("   - 지연된 할일과 오늘 마감 할일이 있습니다")
        print("   - '다시 보지 않기' 옵션을 테스트해보세요")
        
        # MainWindow 생성 및 실행
        main_window = MainWindow(todo_service)
        
        # 임시 설정 파일 사용
        main_window.settings_file = "demo_startup_notification_settings.json"
        
        print("\n3. GUI 실행 중...")
        print("   - 창이 열리면 시작 알림을 확인하세요")
        print("   - 프로그램을 종료하려면 창을 닫으세요")
        
        # GUI 실행
        main_window.run()
        
        print("\n4. 데모 완료!")
        
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리 작업
        print("\n5. 정리 작업...")
        try:
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
                print(f"   - 임시 데이터 파일 삭제: {temp_data_file}")
            
            settings_file = "demo_startup_notification_settings.json"
            if os.path.exists(settings_file):
                os.remove(settings_file)
                print(f"   - 임시 설정 파일 삭제: {settings_file}")
            
            if os.path.exists(temp_folders_dir):
                import shutil
                shutil.rmtree(temp_folders_dir, ignore_errors=True)
                print(f"   - 임시 폴더 삭제: {temp_folders_dir}")
                
        except Exception as e:
            print(f"   - 정리 작업 중 오류: {e}")


def demo_startup_notification_disabled():
    """시작 알림이 비활성화된 상태 데모"""
    print("="*60)
    print("시작 시 알림 비활성화 데모")
    print("="*60)
    
    try:
        # 테스트 데이터 생성
        temp_data_file, temp_folders_dir = create_test_data_with_due_dates()
        
        # 시작 알림이 비활성화된 설정 파일 생성
        settings_file = "demo_startup_notification_disabled_settings.json"
        settings = {
            "geometry": "800x600+100+100",
            "state": "normal",
            "show_startup_notifications": False
        }
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        print("1. 시작 알림이 비활성화된 설정으로 실행...")
        
        # 서비스 초기화
        storage_service = StorageService(temp_data_file)
        file_service = FileService(temp_folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # MainWindow 생성 및 실행
        main_window = MainWindow(todo_service)
        main_window.settings_file = settings_file
        
        print("2. GUI 실행 중...")
        print("   - 시작 알림이 표시되지 않아야 합니다")
        print("   - 지연된 할일이 있지만 알림이 비활성화되어 있습니다")
        
        # GUI 실행
        main_window.run()
        
        print("\n3. 데모 완료!")
        
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리 작업
        print("\n4. 정리 작업...")
        try:
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
            if os.path.exists(settings_file):
                os.remove(settings_file)
            if os.path.exists(temp_folders_dir):
                import shutil
                shutil.rmtree(temp_folders_dir, ignore_errors=True)
        except Exception as e:
            print(f"   - 정리 작업 중 오류: {e}")


def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "disabled":
        demo_startup_notification_disabled()
    else:
        demo_startup_notification()


if __name__ == "__main__":
    main()