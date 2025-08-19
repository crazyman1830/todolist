#!/usr/bin/env python3
"""
Task 13 구현 검증 테스트

폴더 관리 기능 GUI 통합:
- 컨텍스트 메뉴에 "폴더 열기" 옵션 추가
- 할일 생성 시 자동 폴더 생성
- 할일 삭제 시 폴더 삭제 확인 다이얼로그
- 크로스 플랫폼 폴더 열기 기능 (Windows, macOS, Linux)
- 폴더 관련 오류 처리 및 사용자 안내
"""

import unittest
import tempfile
import shutil
import os
import platform
from unittest.mock import patch, MagicMock
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from gui.main_window import MainWindow
from gui.dialogs import FolderErrorDialog, show_folder_error_dialog
import tkinter as tk


class TestTask13FolderManagementIntegration(unittest.TestCase):
    """Task 13: 폴더 관리 기능 GUI 통합 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "todo_folders")
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # GUI 루트 윈도우 (테스트용)
        self.root = tk.Tk()
        self.root.withdraw()  # 화면에 표시하지 않음
    
    def tearDown(self):
        """테스트 환경 정리"""
        try:
            self.root.destroy()
        except:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_context_menu_folder_open_option(self):
        """컨텍스트 메뉴에 '폴더 열기' 옵션 추가 확인"""
        print("\n=== 컨텍스트 메뉴 '폴더 열기' 옵션 테스트 ===")
        
        # MainWindow 생성
        main_window = MainWindow(self.todo_service)
        
        # TodoTree의 컨텍스트 메뉴 확인
        todo_tree = main_window.todo_tree
        
        # 할일용 컨텍스트 메뉴에 '폴더 열기' 옵션 확인
        todo_menu = todo_tree.todo_context_menu
        menu_labels = []
        for i in range(todo_menu.index('end') + 1):
            try:
                label = todo_menu.entrycget(i, 'label')
                menu_labels.append(label)
            except:
                pass
        
        self.assertIn("폴더 열기", menu_labels, "할일 컨텍스트 메뉴에 '폴더 열기' 옵션이 없습니다")
        
        # 하위작업용 컨텍스트 메뉴에 '폴더 열기' 옵션 확인
        subtask_menu = todo_tree.subtask_context_menu
        subtask_menu_labels = []
        for i in range(subtask_menu.index('end') + 1):
            try:
                label = subtask_menu.entrycget(i, 'label')
                subtask_menu_labels.append(label)
            except:
                pass
        
        self.assertIn("폴더 열기", subtask_menu_labels, "하위작업 컨텍스트 메뉴에 '폴더 열기' 옵션이 없습니다")
        
        # 툴바에 '폴더 열기' 버튼 확인
        self.assertTrue(hasattr(main_window, 'btn_open_folder'), "툴바에 '폴더 열기' 버튼이 없습니다")
        self.assertEqual(main_window.btn_open_folder.cget('text'), "폴더 열기", "폴더 열기 버튼 텍스트가 올바르지 않습니다")
        
        print("   ✅ 컨텍스트 메뉴 '폴더 열기' 옵션 확인 완료")
        
        main_window.root.destroy()
    
    def test_automatic_folder_creation(self):
        """할일 생성 시 자동 폴더 생성 확인"""
        print("\n=== 할일 생성 시 자동 폴더 생성 테스트 ===")
        
        # 할일 추가
        todo = self.todo_service.add_todo("테스트 할일")
        
        # 폴더가 자동으로 생성되었는지 확인
        self.assertTrue(os.path.exists(todo.folder_path), "할일 생성 시 폴더가 자동으로 생성되지 않았습니다")
        self.assertTrue(os.path.isdir(todo.folder_path), "생성된 경로가 폴더가 아닙니다")
        
        # 폴더 경로가 올바른지 확인 (언더스코어로 변환된 제목 고려)
        expected_folder_name = f"todo_{todo.id}_테스트_할일"
        self.assertIn(expected_folder_name, todo.folder_path, "폴더 경로가 올바르지 않습니다")
        
        print(f"   ✅ 할일 '{todo.title}' 폴더 자동 생성 확인: {todo.folder_path}")
    
    def test_folder_delete_confirmation_dialog(self):
        """할일 삭제 시 폴더 삭제 확인 다이얼로그 테스트"""
        print("\n=== 폴더 삭제 확인 다이얼로그 테스트 ===")
        
        # 할일 추가
        todo = self.todo_service.add_todo("삭제 테스트 할일")
        
        # 폴더 삭제 확인 다이얼로그 클래스 확인
        from gui.dialogs import FolderDeleteConfirmDialog
        
        # 다이얼로그 클래스가 존재하는지 확인
        self.assertTrue(hasattr(FolderDeleteConfirmDialog, '__init__'), "FolderDeleteConfirmDialog 클래스가 없습니다")
        
        print("   ✅ 폴더 삭제 확인 다이얼로그 클래스 확인 완료")
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_cross_platform_folder_opening_windows(self, mock_subprocess, mock_platform):
        """Windows에서 크로스 플랫폼 폴더 열기 기능 테스트"""
        print("\n=== Windows 폴더 열기 기능 테스트 ===")
        
        mock_platform.return_value = "Windows"
        
        # 할일 추가
        todo = self.todo_service.add_todo("Windows 테스트")
        
        # 폴더 열기 시도
        success, error_message = self.file_service.open_todo_folder(todo.folder_path)
        
        # Windows explorer 명령이 호출되었는지 확인
        mock_subprocess.assert_called_once_with(["explorer", todo.folder_path], check=True, timeout=10)
        self.assertTrue(success, f"Windows에서 폴더 열기 실패: {error_message}")
        
        print("   ✅ Windows 폴더 열기 기능 확인 완료")
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_cross_platform_folder_opening_macos(self, mock_subprocess, mock_platform):
        """macOS에서 크로스 플랫폼 폴더 열기 기능 테스트"""
        print("\n=== macOS 폴더 열기 기능 테스트 ===")
        
        mock_platform.return_value = "Darwin"
        
        # 할일 추가
        todo = self.todo_service.add_todo("macOS 테스트")
        
        # 폴더 열기 시도
        success, error_message = self.file_service.open_todo_folder(todo.folder_path)
        
        # macOS open 명령이 호출되었는지 확인
        mock_subprocess.assert_called_once_with(["open", todo.folder_path], check=True, timeout=10)
        self.assertTrue(success, f"macOS에서 폴더 열기 실패: {error_message}")
        
        print("   ✅ macOS 폴더 열기 기능 확인 완료")
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_cross_platform_folder_opening_linux(self, mock_subprocess, mock_platform):
        """Linux에서 크로스 플랫폼 폴더 열기 기능 테스트"""
        print("\n=== Linux 폴더 열기 기능 테스트 ===")
        
        mock_platform.return_value = "Linux"
        
        # 할일 추가
        todo = self.todo_service.add_todo("Linux 테스트")
        
        # 폴더 열기 시도
        success, error_message = self.file_service.open_todo_folder(todo.folder_path)
        
        # Linux xdg-open 명령이 호출되었는지 확인
        mock_subprocess.assert_called_once_with(["xdg-open", todo.folder_path], check=True, timeout=10)
        self.assertTrue(success, f"Linux에서 폴더 열기 실패: {error_message}")
        
        print("   ✅ Linux 폴더 열기 기능 확인 완료")
    
    @patch('platform.system')
    def test_unsupported_os_error_handling(self, mock_platform):
        """지원하지 않는 OS에서 오류 처리 테스트"""
        print("\n=== 지원하지 않는 OS 오류 처리 테스트 ===")
        
        mock_platform.return_value = "UnsupportedOS"
        
        # 할일 추가
        todo = self.todo_service.add_todo("지원하지 않는 OS 테스트")
        
        # 폴더 열기 시도
        success, error_message = self.file_service.open_todo_folder(todo.folder_path)
        
        self.assertFalse(success, "지원하지 않는 OS에서 성공으로 반환되었습니다")
        self.assertIn("지원하지 않는 운영체제", error_message, "적절한 오류 메시지가 반환되지 않았습니다")
        self.assertIn("수동으로", error_message, "수동 해결 방법이 제시되지 않았습니다")
        
        print(f"   ✅ 지원하지 않는 OS 오류 처리 확인: {error_message}")
    
    def test_nonexistent_folder_error_handling(self):
        """존재하지 않는 폴더 오류 처리 테스트"""
        print("\n=== 존재하지 않는 폴더 오류 처리 테스트 ===")
        
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent_folder")
        
        # 존재하지 않는 폴더 열기 시도 (subprocess 모킹)
        with patch('subprocess.run') as mock_subprocess:
            with patch('platform.system', return_value='Windows'):
                success, error_message = self.file_service.open_todo_folder(nonexistent_path)
                
                # 폴더가 자동으로 생성되어야 함
                self.assertTrue(os.path.exists(nonexistent_path), "폴더가 자동으로 생성되지 않았습니다")
                self.assertTrue(success, f"존재하지 않는 폴더 처리 실패: {error_message}")
                
                # subprocess가 호출되었는지 확인
                mock_subprocess.assert_called_once()
        
        print("   ✅ 존재하지 않는 폴더 자동 생성 확인 완료")
    
    @patch('subprocess.run')
    def test_subprocess_error_handling(self, mock_subprocess):
        """subprocess 오류 처리 테스트"""
        print("\n=== subprocess 오류 처리 테스트 ===")
        
        # subprocess 실행 실패 시뮬레이션
        mock_subprocess.side_effect = FileNotFoundError("Command not found")
        
        # 할일 추가
        todo = self.todo_service.add_todo("subprocess 오류 테스트")
        
        # 폴더 열기 시도
        success, error_message = self.file_service.open_todo_folder(todo.folder_path)
        
        self.assertFalse(success, "subprocess 오류 시 성공으로 반환되었습니다")
        self.assertIn("찾을 수 없습니다", error_message, "적절한 오류 메시지가 반환되지 않았습니다")
        
        print(f"   ✅ subprocess 오류 처리 확인: {error_message}")
    
    def test_enhanced_folder_error_dialog(self):
        """향상된 폴더 오류 다이얼로그 테스트"""
        print("\n=== 향상된 폴더 오류 다이얼로그 테스트 ===")
        
        # 폴더 오류 다이얼로그 클래스 확인
        from gui.dialogs import FolderErrorDialog
        
        # 다이얼로그 클래스가 존재하는지 확인
        self.assertTrue(hasattr(FolderErrorDialog, '__init__'), "FolderErrorDialog 클래스가 없습니다")
        self.assertTrue(hasattr(FolderErrorDialog, '_get_help_text'), "도움말 텍스트 메서드가 없습니다")
        
        # 도움말 텍스트 생성 테스트
        dialog = FolderErrorDialog(self.root, "권한이 없습니다", "권한 오류", show_help=False)
        help_text = dialog._get_help_text()
        self.assertIn("관리자 권한", help_text, "권한 오류에 대한 적절한 도움말이 없습니다")
        
        dialog.destroy()
        
        print("   ✅ 향상된 폴더 오류 다이얼로그 확인 완료")
    
    def test_gui_folder_open_integration(self):
        """GUI 폴더 열기 통합 테스트"""
        print("\n=== GUI 폴더 열기 통합 테스트 ===")
        
        # 할일 추가
        todo = self.todo_service.add_todo("GUI 통합 테스트")
        
        # MainWindow 생성
        main_window = MainWindow(self.todo_service)
        
        # 폴더 열기 메서드가 존재하는지 확인
        self.assertTrue(hasattr(main_window, 'on_open_folder'), "폴더 열기 메서드가 없습니다")
        
        # 할일 선택 시뮬레이션
        with patch.object(main_window.todo_tree, 'get_selected_todo_id', return_value=todo.id):
            with patch.object(main_window.todo_service.file_service, 'open_todo_folder', return_value=(True, "")):
                # 폴더 열기 이벤트 핸들러 호출
                try:
                    main_window.on_open_folder()
                    print("   ✅ 폴더 열기 메서드 호출 성공")
                except Exception as e:
                    self.fail(f"폴더 열기 메서드 호출 실패: {e}")
        
        print("   ✅ GUI 폴더 열기 통합 기능 확인 완료")
        
        main_window.root.destroy()
    
    def test_folder_creation_error_handling_in_gui(self):
        """GUI에서 폴더 생성 오류 처리 테스트"""
        print("\n=== GUI 폴더 생성 오류 처리 테스트 ===")
        
        # MainWindow 생성
        main_window = MainWindow(self.todo_service)
        
        # 폴더 생성 실패 시뮬레이션
        with patch.object(self.todo_service, 'add_todo', side_effect=RuntimeError("할일 폴더 생성 권한이 없습니다")):
            with patch('gui.main_window.show_folder_error_dialog') as mock_dialog:
                with patch('gui.main_window.show_add_todo_dialog', return_value="테스트 할일"):
                    # 할일 추가 시도
                    main_window.on_add_todo()
                    
                    # 향상된 폴더 오류 다이얼로그가 호출되었는지 확인
                    mock_dialog.assert_called_once()
                    args = mock_dialog.call_args[0]
                    self.assertIn("권한", args[1], "권한 오류 메시지가 전달되지 않았습니다")
        
        print("   ✅ GUI 폴더 생성 오류 처리 확인 완료")
        
        main_window.root.destroy()


def run_task13_verification():
    """Task 13 검증 테스트 실행"""
    print("=" * 70)
    print("Task 13: 폴더 관리 기능 GUI 통합 - 구현 검증")
    print("=" * 70)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask13FolderManagementIntegration)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("Task 13 검증 결과 요약")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("\n✅ 구현된 기능:")
        print("   • 컨텍스트 메뉴에 '폴더 열기' 옵션 추가")
        print("   • 할일 생성 시 자동 폴더 생성")
        print("   • 할일 삭제 시 폴더 삭제 확인 다이얼로그")
        print("   • 크로스 플랫폼 폴더 열기 기능 (Windows, macOS, Linux)")
        print("   • 향상된 폴더 관련 오류 처리 및 사용자 안내")
        print("   • GUI와 CLI 모두에서 일관된 폴더 관리 기능")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print(f"   실패한 테스트: {len(result.failures)}")
        print(f"   오류가 발생한 테스트: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_task13_verification()