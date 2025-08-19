#!/usr/bin/env python3
"""
컨텍스트 메뉴 및 사용자 상호작용 수동 테스트

이 스크립트는 GUI를 실제로 실행하여 컨텍스트 메뉴와 상호작용 기능을 수동으로 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TODOS_FILE, TODO_FOLDERS_DIR
from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService
from gui.main_window import MainWindow


def create_test_data(todo_service):
    """테스트용 데이터 생성"""
    try:
        # 기존 할일이 없으면 테스트 데이터 생성
        todos = todo_service.get_all_todos()
        if not todos:
            print("테스트 데이터를 생성합니다...")
            
            # 테스트 할일 추가
            todo1 = todo_service.add_todo("컨텍스트 메뉴 테스트 할일")
            todo2 = todo_service.add_todo("드래그 앤 드롭 테스트 할일")
            todo3 = todo_service.add_todo("키보드 단축키 테스트 할일")
            
            # 하위작업 추가
            todo_service.add_subtask(todo1.id, "우클릭 메뉴 테스트")
            todo_service.add_subtask(todo1.id, "더블클릭 수정 테스트")
            todo_service.add_subtask(todo2.id, "순서 변경 테스트")
            todo_service.add_subtask(todo3.id, "F2 키 테스트")
            todo_service.add_subtask(todo3.id, "Del 키 테스트")
            
            print("테스트 데이터가 생성되었습니다.")
        else:
            print(f"기존 할일 {len(todos)}개를 사용합니다.")
            
    except Exception as e:
        print(f"테스트 데이터 생성 중 오류: {e}")


def print_test_instructions():
    """테스트 지침 출력"""
    print("\n" + "="*70)
    print("                컨텍스트 메뉴 및 상호작용 테스트")
    print("="*70)
    print("다음 기능들을 테스트해보세요:")
    print()
    print("🖱️  컨텍스트 메뉴 테스트:")
    print("   • 할일 항목에서 우클릭 → 할일용 메뉴 확인")
    print("   • 하위작업 항목에서 우클릭 → 하위작업용 메뉴 확인")
    print("   • 빈 공간에서 우클릭 → 빈 공간용 메뉴 확인")
    print()
    print("⌨️  키보드 단축키 테스트:")
    print("   • Ctrl+N: 새 할일 추가")
    print("   • F2: 선택된 항목 수정")
    print("   • Del: 선택된 항목 삭제")
    print("   • Ctrl+Shift+N: 하위작업 추가")
    print("   • F5: 새로고침")
    print("   • Space: 하위작업 완료 상태 토글")
    print("   • 방향키: 항목 네비게이션")
    print()
    print("🖱️  더블클릭 테스트:")
    print("   • 할일 항목 더블클릭 → 수정 다이얼로그")
    print("   • 하위작업 항목 더블클릭 → 수정 다이얼로그")
    print()
    print("🔄 드래그 앤 드롭 테스트:")
    print("   • 할일 항목을 드래그하여 다른 할일 위로 이동")
    print("   • 순서 변경 메시지 확인")
    print()
    print("📁 폴더 열기 테스트:")
    print("   • 할일 선택 후 '폴더 열기' 메뉴 클릭")
    print("   • 파일 탐색기에서 폴더 열림 확인")
    print()
    print("테스트를 시작하려면 GUI 창을 확인하세요!")
    print("="*70)


def main():
    """메인 함수"""
    try:
        print("컨텍스트 메뉴 및 상호작용 테스트를 시작합니다...")
        
        # 서비스 초기화
        storage_service = StorageService(TODOS_FILE)
        file_service = FileService(TODO_FOLDERS_DIR)
        todo_service = TodoService(storage_service, file_service)
        
        # 테스트 데이터 생성
        create_test_data(todo_service)
        
        # 테스트 지침 출력
        print_test_instructions()
        
        # GUI 실행
        main_window = MainWindow(todo_service)
        main_window.run()
        
        print("\n테스트가 완료되었습니다.")
        
    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())