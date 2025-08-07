"""
사용자 인터페이스 및 메뉴 시스템

콘솔 기반 메뉴 인터페이스를 제공하여 사용자가 할일을 관리할 수 있도록 합니다.
"""

import sys
from datetime import datetime
from typing import List, Optional
from services.todo_service import TodoService
from utils.validators import TodoValidator


class MenuUI:
    """사용자 인터페이스 및 메뉴 시스템 클래스"""
    
    def __init__(self, todo_service: TodoService):
        """
        MenuUI 초기화
        
        Args:
            todo_service: 할일 관리 서비스
        """
        self.todo_service = todo_service
    
    def show_main_menu(self) -> None:
        """
        메인 메뉴를 표시하고 사용자 입력을 처리합니다.
        
        Requirements 5.1: 프로그램 시작 시 사용 가능한 모든 기능의 메뉴 표시
        Requirements 5.4: 각 기능 완료 후 메인 메뉴로 돌아가기
        """
        while True:
            # 현재 할일 개수 표시
            todos_count = len(self.todo_service.get_all_todos())
            
            print("\n" + "="*60)
            print("                    📝 할일 관리 프로그램")
            print("="*60)
            print(f"                   현재 할일: {todos_count}개")
            print("-"*60)
            print("  1️⃣  할일 추가                    📝 새로운 할일을 등록합니다")
            print("  2️⃣  할일 목록 보기               📋 등록된 모든 할일을 확인합니다")
            print("  3️⃣  할일 수정                    ✏️  기존 할일의 내용을 변경합니다")
            print("  4️⃣  할일 삭제                    🗑️  완료된 할일을 제거합니다")
            print("  5️⃣  할일 폴더 열기               📁 할일 관련 파일을 관리합니다")
            print("  0️⃣  프로그램 종료                🚪 프로그램을 안전하게 종료합니다")
            print("="*60)
            
            choice = self.get_user_input("💡 원하는 기능의 번호를 입력하세요 (0-5): ").strip()
            
            try:
                if choice == "1":
                    self.handle_add_todo()
                elif choice == "2":
                    self.handle_list_todos()
                elif choice == "3":
                    self.handle_update_todo()
                elif choice == "4":
                    self.handle_delete_todo()
                elif choice == "5":
                    self.handle_open_folder()
                elif choice == "0":
                    print("\n" + "="*60)
                    print("                  👋 프로그램을 종료합니다")
                    print("                   이용해 주셔서 감사합니다!")
                    print("="*60)
                    sys.exit(0)
                else:
                    # Requirements 5.3: 잘못된 메뉴 옵션 선택 시 오류 메시지 표시
                    self.show_error_message("올바른 메뉴 번호를 선택해주세요. (0-5 중 선택)")
                    self.show_info_message("💡 팁: 숫자 0부터 5까지만 입력 가능합니다.")
                    
            except KeyboardInterrupt:
                print("\n\n" + "="*60)
                print("                  ⚠️  사용자가 프로그램을 중단했습니다")
                print("                   이용해 주셔서 감사합니다!")
                print("="*60)
                sys.exit(0)
            except Exception as e:
                self.show_error_message(f"예상치 못한 오류가 발생했습니다: {e}")
                self.show_info_message("💡 문제가 지속되면 프로그램을 다시 시작해보세요.")
    
    def handle_add_todo(self) -> None:
        """
        할일 추가 UI를 처리합니다.
        
        Requirements 1.1, 1.2, 1.3: 할일 추가 기능 및 유효성 검사
        """
        print("\n" + "="*60)
        print("                    📝 새로운 할일 추가")
        print("="*60)
        self.show_info_message("💡 할일 제목을 입력하면 자동으로 전용 폴더가 생성됩니다.")
        
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                title = self.get_user_input("📝 할일 제목을 입력하세요 (취소하려면 Enter): ").strip()
                
                # 빈 입력 시 취소
                if not title:
                    print("✅ 할일 추가를 취소했습니다.")
                    return
                
                # 제목 길이 사전 검사
                if len(title) > 100:
                    self.show_error_message("제목이 너무 깁니다. 100자 이하로 입력해주세요.")
                    continue
                
                # 제목 유효성 검사
                if not TodoValidator.validate_title(title):
                    self.show_error_message("할일 제목을 입력해주세요.")
                    continue
                
                # 할일 추가
                todo = self.todo_service.add_todo(title)
                print("\n" + "="*60)
                print("                    🎉 할일 추가 완료!")
                print("="*60)
                print(f"  📋 할일 번호: {todo.id}")
                print(f"  📝 제목: {todo.title}")
                print(f"  📁 전용 폴더: {todo.folder_path}")
                print(f"  📅 생성 시간: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-"*60)
                self.show_info_message("💡 메뉴 5번을 통해 할일 폴더를 열어 관련 파일을 저장할 수 있습니다.")
                return
                
            except ValueError as e:
                self.show_error_message(str(e))
                retry_count += 1
                if retry_count >= max_retries:
                    self.show_error_message("최대 재시도 횟수를 초과했습니다. 메인 메뉴로 돌아갑니다.")
                    return
                continue
                
            except RuntimeError as e:
                self.show_error_message(str(e))
                # 시스템 오류는 재시도하지 않음
                return
                
            except Exception as e:
                self.show_error_message(f"예상치 못한 오류가 발생했습니다: {e}")
                return
    
    def handle_list_todos(self) -> None:
        """
        할일 목록 표시 UI를 처리합니다.
        
        Requirements 4.1, 4.2, 4.3: 할일 목록 조회 및 표시
        """
        print("\n" + "="*60)
        print("                    📋 등록된 할일 목록")
        print("="*60)
        
        try:
            todos = self.todo_service.get_all_todos()
            
            if not todos:
                # Requirements 4.2: 할일 목록이 비어있을 때 메시지 표시
                print("                    📭 등록된 할일이 없습니다")
                print("-"*60)
                self.show_info_message("💡 메뉴 1번을 통해 새로운 할일을 추가해보세요!")
                return
            
            # Requirements 4.1: 모든 할일을 번호와 함께 표시
            print(f"                   총 {len(todos)}개의 할일이 등록되어 있습니다")
            print("-"*60)
            
            for i, todo in enumerate(todos, 1):
                created_date = todo.created_at.strftime("%Y-%m-%d %H:%M")
                print(f"  {todo.id:2d}️⃣  {todo.title}")
                print(f"       📅 생성일: {created_date}")
                print(f"       📁 폴더: {todo.folder_path}")
                if i < len(todos):
                    print("       " + "-"*40)
            
            print("-"*60)
            self.show_info_message("💡 할일을 수정하려면 메뉴 3번, 삭제하려면 메뉴 4번을 선택하세요.")
                
        except Exception as e:
            self.show_error_message(f"할일 목록을 불러오는 중 오류가 발생했습니다: {e}")
    
    def handle_update_todo(self) -> None:
        """
        할일 수정 UI를 처리합니다.
        
        Requirements 2.1, 2.2, 2.3, 2.4: 할일 수정 기능 및 오류 처리
        """
        print("\n" + "="*60)
        print("                    ✏️  할일 내용 수정")
        print("="*60)
        
        try:
            # 현재 할일 목록 표시
            todos = self.todo_service.get_all_todos()
            if not todos:
                print("                   📭 수정할 할일이 없습니다")
                print("-"*60)
                self.show_info_message("💡 메뉴 1번을 통해 새로운 할일을 추가해보세요!")
                return
            
            print("                   수정할 할일을 선택하세요")
            print("-"*60)
            for todo in todos:
                print(f"  {todo.id:2d}️⃣  {todo.title}")
            print("-"*60)
            
        except Exception as e:
            self.show_error_message(f"할일 목록을 불러오는 중 오류가 발생했습니다: {e}")
            return
        
        # 수정할 할일 선택
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                todo_id_str = self.get_user_input("🔢 수정할 할일의 번호를 입력하세요 (취소하려면 Enter): ").strip()
                
                if not todo_id_str:
                    print("✅ 할일 수정을 취소했습니다.")
                    return
                
                # ID 유효성 검사
                max_id = self.todo_service.get_max_todo_id()
                todo_id = TodoValidator.validate_todo_id(todo_id_str, max_id)
                
                if todo_id is None:
                    self.show_error_message("올바른 할일 번호를 입력해주세요.")
                    retry_count += 1
                    continue
                
                # 할일 존재 확인
                todo = self.todo_service.get_todo_by_id(todo_id)
                if todo is None:
                    # Requirements 2.4: 존재하지 않는 할일 선택 시 오류 메시지
                    self.show_error_message("해당 번호의 할일을 찾을 수 없습니다.")
                    retry_count += 1
                    continue
                
                # Requirements 2.2: 현재 제목 표시 및 새로운 제목 입력 요청
                print(f"\n📝 현재 제목: {todo.title}")
                print("-"*60)
                
                title_retry_count = 0
                while title_retry_count < max_retries:
                    try:
                        new_title = self.get_user_input("✏️  새로운 제목을 입력하세요 (취소하려면 Enter): ").strip()
                        
                        if not new_title:
                            print("✅ 할일 수정을 취소했습니다.")
                            return
                        
                        # 제목 길이 사전 검사
                        if len(new_title) > 100:
                            self.show_error_message("제목이 너무 깁니다. 100자 이하로 입력해주세요.")
                            title_retry_count += 1
                            continue
                        
                        # 제목 유효성 검사
                        if not TodoValidator.validate_title(new_title):
                            self.show_error_message("할일 제목을 입력해주세요.")
                            title_retry_count += 1
                            continue
                        
                        # 할일 수정
                        if self.todo_service.update_todo(todo_id, new_title):
                            print("\n" + "="*60)
                            print("                    🎉 할일 수정 완료!")
                            print("="*60)
                            print(f"  📝 이전 제목: {todo.title}")
                            print(f"  ✏️  새로운 제목: {new_title}")
                            print(f"  📅 수정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print("-"*60)
                            return
                        else:
                            self.show_error_message("할일 수정에 실패했습니다. 다시 시도해주세요.")
                            title_retry_count += 1
                            continue
                            
                    except ValueError as e:
                        self.show_error_message(str(e))
                        title_retry_count += 1
                        if title_retry_count >= max_retries:
                            self.show_error_message("최대 재시도 횟수를 초과했습니다.")
                            return
                        continue
                    except Exception as e:
                        self.show_error_message(f"예상치 못한 오류가 발생했습니다: {e}")
                        return
                
                # 제목 입력 재시도 횟수 초과
                if title_retry_count >= max_retries:
                    return
                    
            except Exception as e:
                self.show_error_message(f"할일 수정 중 오류가 발생했습니다: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    self.show_error_message("최대 재시도 횟수를 초과했습니다.")
                    return
    
    def handle_delete_todo(self) -> None:
        """
        할일 삭제 UI를 처리합니다.
        
        Requirements 3.1, 3.2, 3.3, 3.4: 할일 삭제 기능 및 폴더 삭제 옵션
        """
        print("\n" + "="*60)
        print("                    🗑️  할일 삭제")
        print("="*60)
        
        # 현재 할일 목록 표시
        todos = self.todo_service.get_all_todos()
        if not todos:
            print("                   📭 삭제할 할일이 없습니다")
            print("-"*60)
            self.show_info_message("💡 메뉴 1번을 통해 새로운 할일을 추가해보세요!")
            return
        
        print("                   삭제할 할일을 선택하세요")
        print("-"*60)
        for todo in todos:
            print(f"  {todo.id:2d}️⃣  {todo.title}")
        print("-"*60)
        
        # 삭제할 할일 선택
        while True:
            todo_id_str = self.get_user_input("🔢 삭제할 할일의 번호를 입력하세요 (취소하려면 Enter): ").strip()
            
            if not todo_id_str:
                print("✅ 할일 삭제를 취소했습니다.")
                return
            
            # ID 유효성 검사
            max_id = self.todo_service.get_max_todo_id()
            todo_id = TodoValidator.validate_todo_id(todo_id_str, max_id)
            
            if todo_id is None:
                self.show_error_message("유효하지 않은 할일 번호입니다.")
                continue
            
            # 할일 존재 확인
            todo = self.todo_service.get_todo_by_id(todo_id)
            if todo is None:
                # Requirements 3.4: 존재하지 않는 할일 선택 시 오류 메시지
                self.show_error_message("해당 번호의 할일을 찾을 수 없습니다.")
                continue
            
            # Requirements 3.2: 삭제 확인 요청
            print(f"\n🗑️  삭제할 할일: {todo.title}")
            print(f"📅 생성일: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-"*60)
            confirm = self.get_user_choice(
                "⚠️  정말로 이 할일을 삭제하시겠습니까? (y/n): ",
                ["y", "yes", "n", "no"]
            ).lower()
            
            if confirm in ["n", "no"]:
                print("✅ 할일 삭제를 취소했습니다.")
                return
            
            # Requirements 6.3: 관련 폴더 삭제 여부 확인
            delete_folder = False
            if todo.folder_path:
                print(f"\n📁 관련 폴더: {todo.folder_path}")
                self.show_info_message("💡 폴더를 삭제하면 안에 저장된 모든 파일이 함께 삭제됩니다.")
                folder_confirm = self.get_user_choice(
                    "📁 관련 폴더도 함께 삭제하시겠습니까? (y/n): ",
                    ["y", "yes", "n", "no"]
                ).lower()
                delete_folder = folder_confirm in ["y", "yes"]
            
            try:
                # Requirements 3.3: 할일 삭제 실행
                if self.todo_service.delete_todo(todo_id, delete_folder):
                    print("\n" + "="*60)
                    print("                    🎉 할일 삭제 완료!")
                    print("="*60)
                    print(f"  🗑️  삭제된 할일: {todo.title}")
                    print(f"  📅 삭제 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    if delete_folder:
                        print(f"  📁 폴더도 함께 삭제됨: {todo.folder_path}")
                    else:
                        print(f"  📁 폴더는 보존됨: {todo.folder_path}")
                    print("-"*60)
                    return
                else:
                    self.show_error_message("할일 삭제에 실패했습니다.")
                    return
                    
            except ValueError as e:
                self.show_error_message(str(e))
                return
    
    def handle_open_folder(self) -> None:
        """
        할일 폴더 열기 UI를 처리합니다.
        
        Requirements 5.5, 6.2: 할일 폴더 열기 기능
        """
        print("\n" + "="*60)
        print("                    📁 할일 폴더 열기")
        print("="*60)
        
        # 현재 할일 목록 표시
        todos = self.todo_service.get_all_todos()
        if not todos:
            print("                   📭 열 수 있는 할일 폴더가 없습니다")
            print("-"*60)
            self.show_info_message("💡 메뉴 1번을 통해 새로운 할일을 추가해보세요!")
            return
        
        print("                   폴더를 열 할일을 선택하세요")
        print("-"*60)
        for todo in todos:
            print(f"  {todo.id:2d}️⃣  {todo.title}")
        print("-"*60)
        self.show_info_message("💡 할일 폴더에는 관련 문서, 이미지, 파일 등을 저장할 수 있습니다.")
        
        # 폴더를 열 할일 선택
        while True:
            todo_id_str = self.get_user_input("🔢 폴더를 열 할일의 번호를 입력하세요 (취소하려면 Enter): ").strip()
            
            if not todo_id_str:
                print("✅ 폴더 열기를 취소했습니다.")
                return
            
            # ID 유효성 검사
            max_id = self.todo_service.get_max_todo_id()
            todo_id = TodoValidator.validate_todo_id(todo_id_str, max_id)
            
            if todo_id is None:
                self.show_error_message("유효하지 않은 할일 번호입니다.")
                continue
            
            # 할일 존재 확인
            todo = self.todo_service.get_todo_by_id(todo_id)
            if todo is None:
                self.show_error_message("해당 번호의 할일을 찾을 수 없습니다.")
                continue
            
            # 폴더 열기 시도
            try:
                # FileService를 통해 폴더 열기
                file_service = self.todo_service.file_service
                if file_service.open_todo_folder(todo.folder_path):
                    print("\n" + "="*60)
                    print("                    🎉 폴더 열기 완료!")
                    print("="*60)
                    print(f"  📝 할일: {todo.title}")
                    print(f"  📁 폴더 경로: {todo.folder_path}")
                    print(f"  📅 열기 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("-"*60)
                    self.show_info_message("💡 파일 탐색기에서 폴더가 열렸습니다. 관련 파일을 저장해보세요!")
                    return
                else:
                    self.show_error_message("폴더 열기에 실패했습니다.")
                    return
                    
            except Exception as e:
                self.show_error_message(f"폴더 열기 중 오류가 발생했습니다: {e}")
                return
    
    def get_user_input(self, prompt: str) -> str:
        """
        사용자로부터 입력을 받습니다.
        
        Args:
            prompt: 사용자에게 표시할 프롬프트 메시지
            
        Returns:
            str: 사용자가 입력한 문자열
        """
        try:
            return input(prompt)
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            sys.exit(0)
        except EOFError:
            print("\n\n입력이 종료되었습니다. 프로그램을 종료합니다.")
            sys.exit(0)
    
    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """
        사용자로부터 유효한 선택지 중 하나를 입력받습니다.
        
        Args:
            prompt: 사용자에게 표시할 프롬프트 메시지
            valid_choices: 유효한 선택지 목록
            
        Returns:
            str: 사용자가 선택한 유효한 값
        """
        while True:
            choice = self.get_user_input(prompt).strip().lower()
            
            if choice in [c.lower() for c in valid_choices]:
                return choice
            
            valid_str = "/".join(valid_choices)
            self.show_error_message(f"유효하지 않은 선택입니다. {valid_str} 중에서 선택해주세요.")
    
    def show_error_message(self, message: str) -> None:
        """
        오류 메시지를 사용자 친화적으로 표시합니다.
        
        Args:
            message: 표시할 오류 메시지
        """
        print(f"\n❌ 오류: {message}")
    
    def show_success_message(self, message: str) -> None:
        """
        성공 메시지를 표시합니다.
        
        Args:
            message: 표시할 성공 메시지
        """
        print(f"\n✅ {message}")
    
    def show_info_message(self, message: str) -> None:
        """
        정보 메시지를 표시합니다.
        
        Args:
            message: 표시할 정보 메시지
        """
        print(f"\n💡 {message}")
    
    def show_warning_message(self, message: str) -> None:
        """
        경고 메시지를 표시합니다.
        
        Args:
            message: 표시할 경고 메시지
        """
        print(f"\n⚠️  경고: {message}")