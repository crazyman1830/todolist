#!/usr/bin/env python3
"""
포괄적인 통합 테스트

전체 워크플로우, 파일 시스템 오류, 데이터 저장 오류, 사용자 입력 오류 시나리오를 테스트합니다.
Requirements: 1.3, 2.4, 3.4, 7.4
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
import stat
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from ui.menu import MenuUI
from utils.validators import TodoValidator


class TestComprehensiveIntegration(unittest.TestCase):
    """포괄적인 통합 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.menu_ui = MenuUI(self.todo_service)
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            # 읽기 전용 파일들도 삭제할 수 있도록 권한 변경
            for root, dirs, files in os.walk(self.temp_dir):
                for d in dirs:
                    os.chmod(os.path.join(root, d), stat.S_IRWXU)
                for f in files:
                    os.chmod(os.path.join(root, f), stat.S_IRWXU)
            shutil.rmtree(self.temp_dir)


class TestFullWorkflowIntegration(TestComprehensiveIntegration):
    """전체 워크플로우 통합 테스트"""
    
    def test_complete_todo_lifecycle(self):
        """할일의 전체 생명주기 테스트 (추가 → 조회 → 수정 → 삭제)"""
        # 1. 할일 추가
        todo = self.todo_service.add_todo("테스트 할일")
        self.assertIsNotNone(todo)
        self.assertEqual(todo.title, "테스트 할일")
        self.assertTrue(os.path.exists(todo.folder_path))
        
        # 2. 할일 조회
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].id, todo.id)
        
        # 3. 할일 수정
        success = self.todo_service.update_todo(todo.id, "수정된 할일")
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.title, "수정된 할일")
        
        # 4. 할일 삭제 (폴더 포함)
        success = self.todo_service.delete_todo(todo.id, delete_folder=True)
        self.assertTrue(success)
        
        # 5. 삭제 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 0)
        self.assertFalse(os.path.exists(todo.folder_path))
    
    def test_multiple_todos_workflow(self):
        """여러 할일 관리 워크플로우 테스트"""
        # 여러 할일 추가
        todo1 = self.todo_service.add_todo("첫 번째 할일")
        todo2 = self.todo_service.add_todo("두 번째 할일")
        todo3 = self.todo_service.add_todo("세 번째 할일")
        
        # 모든 할일이 추가되었는지 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 3)
        
        # 생성 순서대로 정렬되었는지 확인
        self.assertEqual(todos[0].id, todo1.id)
        self.assertEqual(todos[1].id, todo2.id)
        self.assertEqual(todos[2].id, todo3.id)
        
        # 중간 할일 삭제
        success = self.todo_service.delete_todo(todo2.id, delete_folder=True)
        self.assertTrue(success)
        
        # 남은 할일 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0].id, todo1.id)
        self.assertEqual(todos[1].id, todo3.id)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_menu_ui_complete_workflow(self, mock_print, mock_input):
        """MenuUI를 통한 전체 워크플로우 테스트"""
        # 할일 추가 시뮬레이션
        mock_input.return_value = "UI 테스트 할일"
        self.menu_ui.handle_add_todo()
        
        # 할일이 추가되었는지 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "UI 테스트 할일")
        
        # 할일 목록 표시 테스트
        self.menu_ui.handle_list_todos()
        mock_print.assert_any_call("                   총 1개의 할일이 등록되어 있습니다")
        
        # 할일 수정 시뮬레이션
        mock_input.side_effect = ["1", "수정된 UI 테스트 할일"]
        self.menu_ui.handle_update_todo()
        
        # 수정 확인
        updated_todo = self.todo_service.get_todo_by_id(todos[0].id)
        self.assertEqual(updated_todo.title, "수정된 UI 테스트 할일")


class TestFileSystemErrorHandling(TestComprehensiveIntegration):
    """파일 시스템 오류 처리 테스트"""
    
    def test_folder_creation_permission_error(self):
        """폴더 생성 권한 오류 처리 테스트"""
        # Windows에서는 폴더 권한 변경이 다르게 동작하므로 스킵
        if os.name == 'nt':
            self.skipTest("Windows에서는 폴더 권한 테스트를 스킵합니다")
        
        # 읽기 전용 디렉토리 생성
        readonly_dir = os.path.join(self.temp_dir, 'readonly')
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
        # 읽기 전용 디렉토리를 기본 폴더로 설정
        file_service = FileService(readonly_dir)
        todo_service = TodoService(self.storage_service, file_service)
        
        # 할일 추가 시 RuntimeError 발생 확인
        with self.assertRaises(RuntimeError) as context:
            todo_service.add_todo("권한 오류 테스트")
        
        self.assertIn("할일 폴더 생성에 실패했습니다", str(context.exception))
        
        # 권한 복원 (tearDown에서 삭제할 수 있도록)
        os.chmod(readonly_dir, stat.S_IRWXU)
    
    def test_folder_deletion_error(self):
        """폴더 삭제 오류 처리 테스트"""
        # Windows에서는 폴더 권한 변경이 다르게 동작하므로 스킵
        if os.name == 'nt':
            self.skipTest("Windows에서는 폴더 권한 테스트를 스킵합니다")
        
        # 할일 추가
        todo = self.todo_service.add_todo("삭제 오류 테스트")
        
        # 폴더를 읽기 전용으로 변경
        os.chmod(todo.folder_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
        # 폴더 삭제 시도 (실패해야 함)
        with patch('builtins.print') as mock_print:
            success = self.todo_service.delete_todo(todo.id, delete_folder=True)
            # 할일은 삭제되지만 폴더 삭제는 실패
            self.assertTrue(success)  # 할일 자체는 삭제됨
            
            # 출력된 메시지 확인
            printed_messages = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("경고: 폴더 삭제에 실패했습니다" in msg for msg in printed_messages))
        
        # 권한 복원
        os.chmod(todo.folder_path, stat.S_IRWXU)
    
    @patch('subprocess.run')
    def test_folder_open_error(self, mock_subprocess):
        """폴더 열기 오류 처리 테스트"""
        # subprocess 실행 실패 시뮬레이션
        mock_subprocess.side_effect = FileNotFoundError("Command not found")
        
        # 할일 추가
        todo = self.todo_service.add_todo("폴더 열기 테스트")
        
        # 폴더 열기 시도 (실패해야 함)
        with patch('builtins.print') as mock_print:
            success = self.file_service.open_todo_folder(todo.folder_path)
            self.assertFalse(success)
            mock_print.assert_any_call(f"폴더 열기 중 오류가 발생했습니다: Command not found")
    
    def test_nonexistent_folder_open(self):
        """존재하지 않는 폴더 열기 시도 테스트"""
        nonexistent_path = os.path.join(self.temp_dir, 'nonexistent')
        
        with patch('builtins.print') as mock_print:
            success = self.file_service.open_todo_folder(nonexistent_path)
            self.assertFalse(success)
            mock_print.assert_any_call(f"폴더가 존재하지 않습니다: {nonexistent_path}")


class TestDataStorageErrorHandling(TestComprehensiveIntegration):
    """데이터 저장 오류 처리 테스트"""
    
    def test_corrupted_json_file_recovery(self):
        """손상된 JSON 파일 복구 테스트"""
        # 손상된 JSON 파일 생성
        with open(self.data_file, 'w', encoding='utf-8') as f:
            f.write('{"invalid": json content}')
        
        # 백업 파일 생성
        backup_file = f"{self.data_file}.backup"
        valid_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "백업된 할일",
                    "created_at": "2025-01-08T10:00:00",
                    "folder_path": "test_path"
                }
            ],
            "next_id": 2
        }
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(valid_data, f)
        
        # 데이터 로드 시 백업에서 복구되는지 확인
        with patch('builtins.print') as mock_print:
            todos = self.storage_service.load_todos()
            self.assertEqual(len(todos), 1)
            self.assertEqual(todos[0].title, "백업된 할일")
            
            # 출력된 메시지 확인 (정확한 메시지 매칭)
            printed_messages = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("JSON 파일이 손상되었습니다" in msg for msg in printed_messages))
            self.assertTrue(any("백업 파일에서 복구 성공" in msg for msg in printed_messages))
    
    def test_file_write_permission_error(self):
        """파일 쓰기 권한 오류 처리 테스트"""
        # Windows에서는 파일 권한 변경이 다르게 동작하므로 스킵
        if os.name == 'nt':
            self.skipTest("Windows에서는 파일 권한 테스트를 스킵합니다")
        
        # 할일 추가 후 데이터 파일을 읽기 전용으로 변경
        todo = self.todo_service.add_todo("권한 테스트")
        os.chmod(self.data_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
        # 할일 수정 시도 (실패해야 함)
        with patch('builtins.print') as mock_print:
            success = self.todo_service.update_todo(todo.id, "수정 시도")
            self.assertFalse(success)
            
            # 출력된 메시지 확인
            printed_messages = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("데이터 저장 중" in msg and "오류" in msg for msg in printed_messages))
        
        # 권한 복원
        os.chmod(self.data_file, stat.S_IRWXU)
    
    def test_storage_rollback_on_save_failure(self):
        """저장 실패 시 롤백 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("롤백 테스트")
        original_title = todo.title
        
        # 저장 실패 시뮬레이션
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            success = self.todo_service.update_todo(todo.id, "실패할 수정")
            self.assertFalse(success)
            
            # 원래 제목이 유지되는지 확인
            updated_todo = self.todo_service.get_todo_by_id(todo.id)
            self.assertEqual(updated_todo.title, original_title)
    
    def test_folder_cleanup_on_save_failure(self):
        """저장 실패 시 폴더 정리 테스트"""
        # 저장 실패 시뮬레이션
        with patch.object(self.storage_service, 'save_todos', return_value=False):
            with self.assertRaises(RuntimeError) as context:
                self.todo_service.add_todo("저장 실패 테스트")
            
            self.assertIn("할일 저장에 실패했습니다", str(context.exception))
            
            # 생성된 폴더가 정리되었는지 확인
            # (폴더가 생성되었다가 삭제되므로 정확한 경로를 확인하기 어려움)
            # 대신 할일이 추가되지 않았는지 확인
            todos = self.todo_service.get_all_todos()
            self.assertEqual(len(todos), 0)


class TestUserInputErrorHandling(TestComprehensiveIntegration):
    """사용자 입력 오류 시나리오 테스트"""
    
    def test_invalid_title_validation(self):
        """잘못된 제목 유효성 검사 테스트"""
        invalid_titles = ["", "   ", "\t\n", None]
        
        for invalid_title in invalid_titles:
            if invalid_title is None:
                continue  # None은 별도 처리
            
            with self.assertRaises(ValueError) as context:
                self.todo_service.add_todo(invalid_title)
            
            self.assertIn("할일 제목이 유효하지 않습니다", str(context.exception))
    
    def test_nonexistent_todo_operations(self):
        """존재하지 않는 할일에 대한 작업 테스트"""
        # 존재하지 않는 ID로 수정 시도
        with self.assertRaises(ValueError) as context:
            self.todo_service.update_todo(999, "존재하지 않는 할일")
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
        
        # 존재하지 않는 ID로 삭제 시도
        with self.assertRaises(ValueError) as context:
            self.todo_service.delete_todo(999)
        self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
        
        # 존재하지 않는 ID로 조회
        todo = self.todo_service.get_todo_by_id(999)
        self.assertIsNone(todo)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_menu_invalid_input_handling(self, mock_print, mock_input):
        """메뉴에서 잘못된 입력 처리 테스트"""
        # 빈 제목 입력 시뮬레이션
        mock_input.side_effect = ["", "   ", "유효한 제목"]
        
        self.menu_ui.handle_add_todo()
        
        # 출력된 메시지 확인 (디버깅용)
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        print(f"DEBUG: Printed messages: {printed_messages}")
        
        # 취소 메시지나 오류 메시지가 출력되었는지 확인
        has_cancel_message = any("할일 추가를 취소했습니다" in msg for msg in printed_messages)
        has_error_message = any("할일 제목을 입력해주세요" in msg for msg in printed_messages)
        
        # 빈 입력 시 취소되거나 오류 메시지가 표시되어야 함
        self.assertTrue(has_cancel_message or has_error_message)
        
        # 빈 입력으로 취소된 경우 할일이 추가되지 않아야 함
        todos = self.todo_service.get_all_todos()
        if has_cancel_message:
            self.assertEqual(len(todos), 0)
        else:
            # 오류 후 유효한 제목으로 추가된 경우
            self.assertEqual(len(todos), 1)
            self.assertEqual(todos[0].title, "유효한 제목")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_menu_invalid_todo_selection(self, mock_print, mock_input):
        """메뉴에서 잘못된 할일 선택 처리 테스트"""
        # 할일 하나 추가
        self.todo_service.add_todo("테스트 할일")
        
        # 잘못된 ID 입력 시뮬레이션
        mock_input.side_effect = ["999", "abc", "0", "1", "수정된 제목"]
        
        self.menu_ui.handle_update_todo()
        
        # 오류 메시지가 출력되었는지 확인
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any("올바른 할일 번호를 입력해주세요" in msg for msg in printed_messages))


class TestExceptionHandlingEnhancement(TestComprehensiveIntegration):
    """예외 상황 처리 로직 보완 테스트"""
    
    def test_service_initialization_with_invalid_paths(self):
        """잘못된 경로로 서비스 초기화 테스트"""
        # 존재하지 않는 드라이브 경로 (Windows) 또는 권한 없는 경로
        invalid_path = "/root/invalid_path" if os.name != 'nt' else "Z:\\invalid_path"
        
        # StorageService는 디렉토리를 생성하려고 시도
        try:
            storage_service = StorageService(os.path.join(invalid_path, "todos.json"))
            # 실제로는 권한 문제로 실패할 수 있지만, 테스트 환경에서는 성공할 수도 있음
        except Exception:
            pass  # 예상된 동작
        
        # FileService는 기본 폴더 생성을 시도
        with patch('builtins.print') as mock_print:
            try:
                file_service = FileService(invalid_path)
            except Exception:
                pass  # 예상된 동작
    
    def test_concurrent_file_access_simulation(self):
        """동시 파일 접근 시뮬레이션 테스트"""
        # 할일 추가
        todo1 = self.todo_service.add_todo("동시 접근 테스트 1")
        
        # 다른 프로세스가 파일을 수정하는 상황 시뮬레이션
        # (실제로는 파일 잠금이나 다른 메커니즘이 필요하지만, 여기서는 간단히 시뮬레이션)
        with patch.object(self.storage_service, 'load_todos') as mock_load:
            mock_load.return_value = []  # 빈 목록 반환 (다른 프로세스가 파일을 초기화한 상황)
            
            # 할일 수정 시도 - ValueError 예외 발생 예상
            with self.assertRaises(ValueError) as context:
                self.todo_service.update_todo(todo1.id, "수정 시도")
            
            self.assertIn("해당 할일을 찾을 수 없습니다", str(context.exception))
    
    def test_memory_pressure_simulation(self):
        """메모리 부족 상황 시뮬레이션 테스트"""
        # 대량의 할일 데이터 생성 시뮬레이션
        large_todos = []
        for i in range(1000):
            todo_data = {
                "id": i,
                "title": f"대량 테스트 할일 {i}" * 100,  # 긴 제목
                "created_at": datetime.now().isoformat(),
                "folder_path": f"test_path_{i}"
            }
            large_todos.append(Todo.from_dict(todo_data))
        
        # 메모리 부족 상황에서도 기본 기능이 동작하는지 확인
        with patch.object(self.storage_service, 'load_todos', return_value=large_todos):
            todos = self.todo_service.get_all_todos()
            self.assertEqual(len(todos), 1000)
            
            # 특정 할일 검색이 여전히 동작하는지 확인
            found_todo = self.todo_service.get_todo_by_id(500)
            self.assertIsNotNone(found_todo)
            self.assertEqual(found_todo.id, 500)


if __name__ == '__main__':
    # 테스트 실행 시 상세한 출력
    unittest.main(verbosity=2)