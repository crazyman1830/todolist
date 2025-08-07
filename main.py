#!/usr/bin/env python3
"""
할일 관리 프로그램 메인 진입점

Requirements 5.1, 5.4, 7.2: 프로그램 시작, 메뉴 표시, 데이터 저장
"""

import sys
import signal
from config import TODOS_FILE, TODO_FOLDERS_DIR
from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService
from ui.menu import MenuUI


def signal_handler(signum, frame):
    """
    시그널 핸들러 - Ctrl+C 등의 인터럽트 처리
    
    Args:
        signum: 시그널 번호
        frame: 현재 스택 프레임
    """
    print("\n\n" + "="*70)
    print("                  ⚠️  사용자가 프로그램을 중단했습니다")
    print("                     이용해 주셔서 감사합니다!")
    print("="*70)
    sys.exit(0)


def initialize_services():
    """
    서비스 의존성 주입 및 초기화
    
    Returns:
        tuple: (todo_service, menu_ui) 초기화된 서비스들
        
    Raises:
        RuntimeError: 서비스 초기화에 실패한 경우
    """
    try:
        # 1. 저장 서비스 초기화
        storage_service = StorageService(TODOS_FILE)
        
        # 2. 파일 서비스 초기화
        file_service = FileService(TODO_FOLDERS_DIR)
        
        # 3. 할일 서비스 초기화 (의존성 주입)
        todo_service = TodoService(storage_service, file_service)
        
        # 4. 메뉴 UI 초기화
        menu_ui = MenuUI(todo_service)
        
        return todo_service, menu_ui
        
    except Exception as e:
        raise RuntimeError(f"서비스 초기화에 실패했습니다: {e}")


def main():
    """
    프로그램 메인 함수
    
    Requirements:
    - 5.1: 프로그램 시작 시 메뉴 표시
    - 5.4: 메인 애플리케이션 루프
    - 7.2: 데이터 저장 및 로드
    """
    # 시그널 핸들러 등록 (Ctrl+C 처리)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 환영 메시지 출력
        print("\n" + "="*70)
        print("                  🎉 할일 관리 프로그램에 오신 것을 환영합니다!")
        print("="*70)
        print("                        프로그램을 초기화하는 중...")
        print("-"*70)
        
        # 서비스 초기화 및 의존성 주입
        print("⚙️  서비스 초기화 중...")
        todo_service, menu_ui = initialize_services()
        
        # 초기 데이터 로드 확인
        print("📂 기존 데이터 로드 중...")
        todos = todo_service.get_all_todos()
        
        if todos:
            print(f"✅ 기존 할일 {len(todos)}개를 성공적으로 불러왔습니다.")
            print("📋 최근 할일:")
            for i, todo in enumerate(todos[-3:], 1):  # 최근 3개만 표시
                print(f"   {i}. {todo.title}")
        else:
            print("📭 새로운 사용자입니다. 첫 번째 할일을 추가해보세요!")
        
        print("\n🎊 초기화가 완료되었습니다!")
        print("💡 팁: 언제든지 Ctrl+C를 눌러 프로그램을 종료할 수 있습니다.")
        print("="*70)
        
        # 메인 애플리케이션 루프 시작
        # Requirements 5.1, 5.4: 메뉴 표시 및 사용자 입력 처리
        menu_ui.show_main_menu()
        
    except RuntimeError as e:
        print(f"\n❌ 초기화 오류: {e}")
        print("🔧 해결 방법:")
        print("   1. 프로그램 폴더의 권한을 확인해주세요")
        print("   2. 디스크 공간이 충분한지 확인해주세요")
        print("   3. 바이러스 백신이 프로그램을 차단하지 않는지 확인해주세요")
        print("\n프로그램을 종료합니다.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("                  ⚠️  사용자가 프로그램을 중단했습니다")
        print("                     이용해 주셔서 감사합니다!")
        print("="*70)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        print("🔧 해결 방법:")
        print("   1. 프로그램을 다시 시작해보세요")
        print("   2. 문제가 지속되면 데이터 파일을 백업하고 프로그램을 재설치해주세요")
        print("\n프로그램을 종료합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()