#!/usr/bin/env python3
"""
TodoTree 컴포넌트 데모 스크립트
트리 뷰 기능을 시각적으로 확인할 수 있습니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from models.todo import Todo
from models.subtask import SubTask


def create_demo_data(todo_service: TodoService):
    """데모용 데이터 생성"""
    print("데모 데이터 생성 중...")
    
    # 기존 데이터 클리어
    todos = todo_service.get_all_todos()
    for todo in todos:
        todo_service.delete_todo(todo.id, delete_folder=False)
    
    # 데모 할일 1: 완료된 할일
    todo1 = todo_service.add_todo("프로젝트 문서 작성")
    if todo1:
        todo_service.add_subtask(todo1.id, "요구사항 분석")
        todo_service.add_subtask(todo1.id, "설계 문서 작성")
        todo_service.add_subtask(todo1.id, "API 문서 작성")
        
        # 모든 하위작업 완료 처리
        subtasks = todo_service.get_subtasks(todo1.id)
        for subtask in subtasks:
            todo_service.toggle_subtask_completion(todo1.id, subtask.id)
    
    # 데모 할일 2: 진행 중인 할일
    todo2 = todo_service.add_todo("GUI 개발")
    if todo2:
        todo_service.add_subtask(todo2.id, "메인 윈도우 구현")
        todo_service.add_subtask(todo2.id, "트리 뷰 구현")
        todo_service.add_subtask(todo2.id, "다이얼로그 구현")
        todo_service.add_subtask(todo2.id, "테스트 작성")
        
        # 일부 하위작업만 완료 처리
        subtasks = todo_service.get_subtasks(todo2.id)
        for i, subtask in enumerate(subtasks[:2]):  # 처음 2개만 완료
            todo_service.toggle_subtask_completion(todo2.id, subtask.id)
    
    # 데모 할일 3: 하위작업이 없는 할일
    todo_service.add_todo("코드 리뷰")
    
    # 데모 할일 4: 미완료 할일
    todo4 = todo_service.add_todo("배포 준비")
    if todo4:
        todo_service.add_subtask(todo4.id, "빌드 스크립트 작성")
        todo_service.add_subtask(todo4.id, "도커 이미지 생성")
        todo_service.add_subtask(todo4.id, "배포 문서 작성")
    
    print("데모 데이터 생성 완료!")


def main():
    """메인 함수"""
    print("TodoTree 컴포넌트 데모 시작")
    print("=" * 50)
    
    try:
        # 서비스 초기화
        file_service = FileService()
        storage_service = StorageService("data/demo_todos.json", file_service)
        todo_service = TodoService(storage_service, file_service)
        
        # 데모 데이터 생성
        create_demo_data(todo_service)
        
        # GUI 실행
        print("GUI 실행 중...")
        print("\n사용법:")
        print("- 트리에서 할일과 하위작업을 확인하세요")
        print("- 아이콘을 클릭하여 하위작업 완료 상태를 토글하세요")
        print("- 우클릭으로 컨텍스트 메뉴를 확인하세요")
        print("- 더블클릭으로 편집 기능을 테스트하세요")
        print("- 메뉴에서 '모두 확장/축소' 기능을 테스트하세요")
        print("- 검색 기능을 테스트하세요")
        print("\n윈도우를 닫으면 데모가 종료됩니다.")
        print("=" * 50)
        
        # 메인 윈도우 생성 및 실행
        app = MainWindow(todo_service)
        app.run()
        
    except Exception as e:
        print(f"오류 발생: {e}")
        messagebox.showerror("오류", f"데모 실행 중 오류가 발생했습니다:\n{str(e)}")
    
    finally:
        print("TodoTree 컴포넌트 데모 종료")


if __name__ == "__main__":
    main()