#!/usr/bin/env python3
"""
할일 관리 프로그램 GUI 버전 메인 진입점

이 모듈은 GUI 할일 관리 프로그램의 진입점으로, 다음 기능을 제공합니다:
- 서비스 의존성 주입 및 초기화
- GUI 애플리케이션 루프 구현
- 예외 처리 및 오류 다이얼로그 표시
- 프로그램 종료 시 설정 저장
- 시스템 리소스 정리

Requirements: 1.1, 1.4, 7.1
"""

import sys
import os
import json
import logging
import traceback
import signal
import atexit
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Optional

from config import TODOS_FILE, TODO_FOLDERS_DIR
from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService
from gui.main_window import MainWindow


class TodoGUIApplication:
    """GUI 할일 관리 애플리케이션 메인 클래스"""
    
    def __init__(self):
        """애플리케이션 초기화"""
        self.todo_service: Optional[TodoService] = None
        self.main_window: Optional[MainWindow] = None
        self.app_settings_file = "app_settings.json"
        self.log_file = "app.log"
        
        # 로깅 설정
        self.setup_logging()
        
        # 종료 핸들러 등록
        self.register_exit_handlers()
        
        # 애플리케이션 설정 로드
        self.app_settings = self.load_app_settings()
        
        self.logger.info("TodoGUIApplication 초기화 완료")
    
    def setup_logging(self):
        """로깅 시스템 설정"""
        try:
            # 로그 디렉토리 생성
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            log_file_path = os.path.join(log_dir, self.log_file)
            
            # 로깅 설정
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file_path, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.logger = logging.getLogger(__name__)
            self.logger.info("로깅 시스템 초기화 완료")
            
        except Exception as e:
            # 로깅 설정 실패 시 기본 로거 사용
            self.logger = logging.getLogger(__name__)
            print(f"로깅 설정 실패: {e}")
    
    def register_exit_handlers(self):
        """프로그램 종료 시 호출될 핸들러들을 등록"""
        try:
            # atexit 핸들러 등록
            atexit.register(self.cleanup_on_exit)
            
            # 시그널 핸들러 등록 (Unix 계열 시스템)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, self.signal_handler)
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, self.signal_handler)
                
            self.logger.info("종료 핸들러 등록 완료")
            
        except Exception as e:
            self.logger.warning(f"종료 핸들러 등록 실패: {e}")
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        self.logger.info(f"시그널 {signum} 수신, 프로그램 종료 중...")
        self.shutdown_gracefully()
        sys.exit(0)
    
    def load_app_settings(self) -> dict:
        """애플리케이션 설정 로드"""
        default_settings = {
            "auto_save_enabled": True,
            "auto_backup_enabled": True,
            "log_level": "INFO",
            "theme": "default",
            "language": "ko",
            "startup_check_integrity": True,
            "last_run": None,
            "crash_count": 0,
            "performance_mode": False
        }
        
        try:
            if os.path.exists(self.app_settings_file):
                with open(self.app_settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 기본 설정과 병합
                default_settings.update(loaded_settings)
                self.logger.info("애플리케이션 설정 로드 완료")
            else:
                self.logger.info("설정 파일이 없어 기본 설정 사용")
                
        except Exception as e:
            self.logger.warning(f"설정 로드 실패, 기본 설정 사용: {e}")
        
        return default_settings
    
    def save_app_settings(self):
        """애플리케이션 설정 저장"""
        try:
            # 마지막 실행 시간 업데이트
            self.app_settings["last_run"] = datetime.now().isoformat()
            
            with open(self.app_settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_settings, f, ensure_ascii=False, indent=2)
            
            self.logger.info("애플리케이션 설정 저장 완료")
            
        except Exception as e:
            self.logger.error(f"설정 저장 실패: {e}")
    
    def initialize_services(self) -> TodoService:
        """
        서비스 의존성 주입 및 초기화
        
        Returns:
            TodoService: 초기화된 할일 서비스
            
        Raises:
            RuntimeError: 서비스 초기화에 실패한 경우
        """
        try:
            self.logger.info("서비스 초기화 시작")
            
            # 1. 저장 서비스 초기화
            auto_save_enabled = self.app_settings.get("auto_save_enabled", True)
            storage_service = StorageService(TODOS_FILE, auto_save_enabled=auto_save_enabled)
            self.logger.info(f"StorageService 초기화 완료 (자동저장: {auto_save_enabled})")
            
            # 2. 파일 서비스 초기화
            file_service = FileService(TODO_FOLDERS_DIR)
            self.logger.info("FileService 초기화 완료")
            
            # 3. 할일 서비스 초기화 (의존성 주입)
            todo_service = TodoService(storage_service, file_service)
            self.logger.info("TodoService 초기화 완료")
            
            # 4. 데이터 무결성 검사 (설정에 따라)
            if self.app_settings.get("startup_check_integrity", True):
                self.check_data_integrity(todo_service)
            
            self.logger.info("모든 서비스 초기화 완료")
            return todo_service
            
        except Exception as e:
            error_msg = f"서비스 초기화에 실패했습니다: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            raise RuntimeError(error_msg) from e
    
    def check_data_integrity(self, todo_service: TodoService):
        """데이터 무결성 검사 및 복구"""
        try:
            self.logger.info("데이터 무결성 검사 시작")
            
            status = todo_service.get_data_status()
            
            if not status["data_valid"]:
                self.logger.warning("데이터 무결성 문제 발견, 복구 시도")
                
                if todo_service.repair_data():
                    self.logger.info("데이터 무결성 복구 완료")
                else:
                    self.logger.error("데이터 무결성 복구 실패")
                    raise RuntimeError("데이터 파일이 손상되어 복구할 수 없습니다")
            
            if status["integrity_issues"]:
                self.logger.warning(f"무결성 문제 발견: {status['integrity_issues']}")
                
                # 자동 복구 시도
                if todo_service.repair_data():
                    self.logger.info("무결성 문제 자동 복구 완료")
                else:
                    self.logger.warning("일부 무결성 문제를 복구할 수 없습니다")
            
            self.logger.info("데이터 무결성 검사 완료")
            
        except Exception as e:
            self.logger.error(f"데이터 무결성 검사 중 오류: {e}")
            # 무결성 검사 실패는 치명적이지 않으므로 계속 진행
    
    def show_error_dialog(self, title: str, message: str, details: str = None):
        """오류 다이얼로그 표시"""
        try:
            root = tk.Tk()
            root.withdraw()  # 메인 윈도우 숨기기
            
            if details:
                full_message = f"{message}\n\n상세 정보:\n{details}"
            else:
                full_message = message
            
            messagebox.showerror(title, full_message)
            root.destroy()
            
        except Exception as e:
            # 다이얼로그 표시도 실패한 경우 콘솔에 출력
            print(f"오류 다이얼로그 표시 실패: {e}")
            print(f"원본 오류 - {title}: {message}")
            if details:
                print(f"상세 정보: {details}")
    
    def show_info_dialog(self, title: str, message: str):
        """정보 다이얼로그 표시"""
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(title, message)
            root.destroy()
        except Exception as e:
            print(f"정보 다이얼로그 표시 실패: {e}")
            print(f"메시지 - {title}: {message}")
    
    def handle_crash(self, exception: Exception):
        """프로그램 크래시 처리"""
        try:
            # 크래시 카운트 증가
            self.app_settings["crash_count"] = self.app_settings.get("crash_count", 0) + 1
            
            # 크래시 로그 기록
            crash_info = {
                "timestamp": datetime.now().isoformat(),
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc()
            }
            
            crash_log_file = f"crash_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(crash_log_file, 'w', encoding='utf-8') as f:
                    json.dump(crash_info, f, ensure_ascii=False, indent=2)
                self.logger.error(f"크래시 로그 저장: {crash_log_file}")
            except:
                pass
            
            # 긴급 데이터 저장 시도
            if self.todo_service:
                try:
                    self.todo_service.force_save()
                    self.logger.info("긴급 데이터 저장 완료")
                except Exception as save_error:
                    self.logger.error(f"긴급 데이터 저장 실패: {save_error}")
            
            # 설정 저장
            self.save_app_settings()
            
            self.logger.error(f"프로그램 크래시: {exception}")
            self.logger.error(traceback.format_exc())
            
        except Exception as e:
            print(f"크래시 처리 중 오류: {e}")
    
    def cleanup_on_exit(self):
        """프로그램 종료 시 정리 작업"""
        try:
            self.logger.info("프로그램 종료 정리 작업 시작")
            
            # 서비스 정리
            if self.todo_service:
                self.todo_service.shutdown()
                self.logger.info("TodoService 정리 완료")
            
            # 설정 저장
            self.save_app_settings()
            
            self.logger.info("프로그램 종료 정리 작업 완료")
            
        except Exception as e:
            print(f"종료 정리 작업 중 오류: {e}")
    
    def shutdown_gracefully(self):
        """우아한 종료 처리"""
        try:
            self.logger.info("우아한 종료 시작")
            
            # 메인 윈도우가 있으면 종료 처리
            if self.main_window and hasattr(self.main_window, 'root'):
                try:
                    # 윈도우 설정 저장
                    self.main_window.save_window_settings()
                    
                    # 윈도우 종료
                    self.main_window.root.quit()
                    self.main_window.root.destroy()
                    
                except Exception as e:
                    self.logger.warning(f"윈도우 종료 중 오류: {e}")
            
            # 정리 작업 수행
            self.cleanup_on_exit()
            
            self.logger.info("우아한 종료 완료")
            
        except Exception as e:
            self.logger.error(f"우아한 종료 중 오류: {e}")
    
    def run(self):
        """
        GUI 애플리케이션 실행
        
        메인 애플리케이션 루프를 시작하고 모든 예외를 처리합니다.
        """
        try:
            self.logger.info("GUI 애플리케이션 시작")
            
            # 서비스 초기화
            self.todo_service = self.initialize_services()
            
            # GUI 메인 윈도우 생성
            self.main_window = MainWindow(self.todo_service)
            self.logger.info("MainWindow 생성 완료")
            
            # 애플리케이션 루프 시작
            self.logger.info("GUI 애플리케이션 루프 시작")
            self.main_window.run()
            
            self.logger.info("GUI 애플리케이션 정상 종료")
            
        except RuntimeError as e:
            # 초기화 오류
            error_msg = f"서비스 초기화에 실패했습니다:\n{e}"
            self.logger.error(error_msg)
            self.handle_crash(e)
            self.show_error_dialog("초기화 오류", error_msg)
            sys.exit(1)
            
        except tk.TclError as e:
            # Tkinter 관련 오류
            error_msg = f"GUI 시스템 오류가 발생했습니다:\n{e}"
            self.logger.error(error_msg)
            self.handle_crash(e)
            self.show_error_dialog("GUI 시스템 오류", error_msg)
            sys.exit(1)
            
        except KeyboardInterrupt:
            # Ctrl+C 인터럽트
            self.logger.info("사용자 인터럽트로 프로그램 종료")
            self.shutdown_gracefully()
            sys.exit(0)
            
        except SystemExit:
            # 정상적인 시스템 종료
            self.logger.info("시스템 종료 신호 수신")
            self.shutdown_gracefully()
            
        except Exception as e:
            # 예상치 못한 오류
            error_msg = f"예상치 못한 오류가 발생했습니다:\n{e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            self.handle_crash(e)
            
            # 사용자에게 오류 표시
            details = traceback.format_exc() if self.app_settings.get("show_debug_info", False) else None
            self.show_error_dialog("예상치 못한 오류", error_msg, details)
            
            sys.exit(1)


def main():
    """
    GUI 프로그램 메인 함수
    
    애플리케이션 인스턴스를 생성하고 실행합니다.
    """
    try:
        # 애플리케이션 인스턴스 생성 및 실행
        app = TodoGUIApplication()
        app.run()
        
    except Exception as e:
        # 최상위 예외 처리
        print(f"프로그램 시작 실패: {e}")
        print(traceback.format_exc())
        
        # 긴급 오류 다이얼로그
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "치명적 오류", 
                f"프로그램을 시작할 수 없습니다:\n{e}\n\n프로그램을 다시 시작해주세요."
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()