#!/usr/bin/env python3
"""
GUI 할일 관리자 데모 스크립트

GUI 기본 구조가 올바르게 구현되었는지 시각적으로 확인할 수 있는 데모입니다.
이 스크립트를 실행하면 GUI 윈도우가 3초간 표시된 후 자동으로 종료됩니다.
"""

import sys
import os
import threading
import time

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from gui.main_window import MainWindow


def auto_close_window(app, delay=3):
    """지정된 시간 후 윈도우를 자동으로 닫는 함수"""
    time.sleep(delay)
    try:
        app.root.quit()
        app.root.destroy()
    except:
        pass


def main():
    """데모 메인 함수"""
    try:
        print("GUI 할일 관리자 데모를 시작합니다...")
        print("윈도우가 3초간 표시된 후 자동으로 종료됩니다.")
        
        # 서비스 초기화
        storage_service = StorageService("data/todos.json")
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        
        # GUI 생성
        app = MainWindow(todo_service)
        
        # 윈도우 크기 설정 (데모용)
        app.root.geometry("800x600+100+100")
        
        # 자동 종료 스레드 시작
        close_thread = threading.Thread(target=auto_close_window, args=(app, 3))
        close_thread.daemon = True
        close_thread.start()
        
        print("GUI 윈도우를 표시합니다...")
        print("\n구현된 기능들:")
        print("✓ 메인 윈도우 (800x600)")
        print("✓ 메뉴바 (파일, 편집, 보기, 도움말)")
        print("✓ 툴바 (추가, 수정, 삭제, 새로고침, 하위작업 추가, 폴더 열기)")
        print("✓ 검색 박스")
        print("✓ 상태바 (할일 개수, 완료율, 상태 메시지)")
        print("✓ 키보드 단축키 지원")
        print("✓ 윈도우 설정 저장/복원")
        
        # GUI 실행
        app.run()
        
        print("데모가 완료되었습니다.")
        
    except Exception as e:
        print(f"데모 실행 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()