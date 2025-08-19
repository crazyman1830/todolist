#!/usr/bin/env python3
"""
메인 GUI 데모 - 전체 애플리케이션 기능 시연
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
from gui.main_window import MainWindow


def create_demo_data():
    """데모용 샘플 데이터 생성"""
    temp_data_file = "demo_gui_data.json"
    temp_folders_dir = "demo_gui_folders"
    
    now = datetime.now()
    demo_todos = [
        {
            "id": 1,
            "title": "프로젝트 계획 수립",
            "created_at": (now - timedelta(days=3)).isoformat(),
            "due_date": (now + timedelta(days=2)).isoformat(),
            "completed_at": None,
            "folder_path": f"{temp_folders_dir}/todo_1_프로젝트_계획_수립",
            "is_expanded": True,
            "subtasks": [
                {
                    "id": 1,
                    "todo_id": 1,
                    "title": "요구사항 분석",
                    "is_completed": True,
                    "created_at": (now - timedelta(days=2)).isoformat()
                },
                {
                    "id": 2,
                    "todo_id": 1,
                    "title": "일정 수립",
                    "is_completed": False,
                    "created_at": (now - timedelta(days=1)).isoformat()
                }
            ]
        },
        {
            "id": 2,
            "title": "지연된 중요 작업",
            "created_at": (now - timedelta(days=5)).isoformat(),
            "due_date": (now - timedelta(days=1)).isoformat(),
            "completed_at": None,
            "folder_path": f"{temp_folders_dir}/todo_2_지연된_중요_작업",
            "is_expanded": True,
            "subtasks": []
        },
        {
            "id": 3,
            "title": "완료된 작업",
            "created_at": (now - timedelta(days=7)).isoformat(),
            "due_date": (now - timedelta(days=3)).isoformat(),
            "completed_at": (now - timedelta(days=2)).isoformat(),
            "folder_path": f"{temp_folders_dir}/todo_3_완료된_작업",
            "is_expanded": False,
            "subtasks": [
                {
                    "id": 3,
                    "todo_id": 3,
                    "title": "문서 작성",
                    "is_completed": True,
                    "created_at": (now - timedelta(days=6)).isoformat()
                }
            ]
        }
    ]
    
    data = {
        "todos": demo_todos,
        "next_todo_id": 4,
        "next_subtask_id": 4
    }
    
    with open(temp_data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return temp_data_file, temp_folders_dir


def main():
    """메인 GUI 데모 실행"""
    print("=" * 60)
    print("Todo List 애플리케이션 - 메인 GUI 데모")
    print("=" * 60)
    print("이 데모는 다음 기능들을 보여줍니다:")
    print("• 할일 추가, 수정, 삭제")
    print("• 하위작업 관리")
    print("• 목표 날짜 설정 및 관리")
    print("• 진행률 표시")
    print("• 컨텍스트 메뉴")
    print("• 키보드 단축키")
    print("• 드래그 앤 드롭")
    print("• 폴더 관리")
    print("• 알림 기능")
    print("=" * 60)
    
    try:
        # 데모 데이터 생성
        data_file, folders_dir = create_demo_data()
        print(f"데모 데이터 생성: {data_file}")
        
        # 서비스 초기화
        storage_service = StorageService(data_file)
        file_service = FileService(folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        print("GUI 애플리케이션 시작...")
        print("창을 닫으면 데모가 종료됩니다.")
        
        # GUI 실행
        main_window = MainWindow(todo_service)
        main_window.run()
        
        print("데모 완료!")
        
    except Exception as e:
        print(f"데모 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리 작업
        try:
            if os.path.exists(data_file):
                os.remove(data_file)
            if os.path.exists(folders_dir):
                import shutil
                shutil.rmtree(folders_dir, ignore_errors=True)
            print("임시 파일 정리 완료")
        except Exception as e:
            print(f"정리 작업 중 오류: {e}")


if __name__ == "__main__":
    main()