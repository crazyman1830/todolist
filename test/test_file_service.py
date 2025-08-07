"""
FileService 단위 테스트
"""
import unittest
import tempfile
import shutil
import os
import sys
import subprocess
from datetime import datetime
from unittest.mock import patch, MagicMock

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from services.file_service import FileService


class TestFileService(unittest.TestCase):
    """FileService 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.file_service = FileService(self.temp_dir)
        
        # 테스트용 Todo 객체 생성
        self.test_todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path=""
        )
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_creates_base_folder(self):
        """초기화 시 기본 폴더가 생성되는지 테스트"""
        new_temp_dir = os.path.join(self.temp_dir, "new_base")
        file_service = FileService(new_temp_dir)
        
        self.assertTrue(os.path.exists(new_temp_dir))
        self.assertTrue(os.path.isdir(new_temp_dir))
    
    def test_create_todo_folder_success(self):
        """할일 폴더 생성 성공 테스트"""
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        self.assertTrue(os.path.exists(folder_path))
        self.assertTrue(os.path.isdir(folder_path))
        self.assertIn("todo_1_테스트_할일", folder_path)
    
    def test_create_todo_folder_already_exists(self):
        """이미 존재하는 폴더 생성 시 기존 폴더 유지 테스트"""
        # 첫 번째 생성
        folder_path1 = self.file_service.create_todo_folder(self.test_todo)
        
        # 테스트 파일 생성
        test_file = os.path.join(folder_path1, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("test content")
        
        # 두 번째 생성 (이미 존재)
        folder_path2 = self.file_service.create_todo_folder(self.test_todo)
        
        self.assertEqual(folder_path1, folder_path2)
        self.assertTrue(os.path.exists(test_file))  # 기존 파일이 유지되는지 확인
    
    def test_create_todo_folder_permission_error(self):
        """폴더 생성 권한 오류 테스트"""
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            with self.assertRaises(OSError):
                self.file_service.create_todo_folder(self.test_todo)
    
    def test_delete_todo_folder_success(self):
        """할일 폴더 삭제 성공 테스트"""
        # 폴더 생성
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        # 폴더 내에 파일 생성
        test_file = os.path.join(folder_path, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("test content")
        
        # 폴더 삭제
        result = self.file_service.delete_todo_folder(folder_path)
        
        self.assertTrue(result)
        self.assertFalse(os.path.exists(folder_path))
    
    def test_delete_todo_folder_not_exists(self):
        """존재하지 않는 폴더 삭제 테스트"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent")
        result = self.file_service.delete_todo_folder(non_existent_path)
        
        self.assertFalse(result)
    
    def test_delete_todo_folder_permission_error(self):
        """폴더 삭제 권한 오류 테스트"""
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        with patch('shutil.rmtree', side_effect=PermissionError("Permission denied")):
            result = self.file_service.delete_todo_folder(folder_path)
            self.assertFalse(result)
    
    def test_folder_exists_true(self):
        """폴더 존재 확인 - 존재하는 경우"""
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        result = self.file_service.folder_exists(folder_path)
        
        self.assertTrue(result)
    
    def test_folder_exists_false(self):
        """폴더 존재 확인 - 존재하지 않는 경우"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent")
        result = self.file_service.folder_exists(non_existent_path)
        
        self.assertFalse(result)
    
    def test_folder_exists_file_not_folder(self):
        """폴더 존재 확인 - 파일인 경우"""
        file_path = os.path.join(self.temp_dir, "test_file.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("test")
        
        result = self.file_service.folder_exists(file_path)
        self.assertFalse(result)
    
    def test_get_todo_folder_path(self):
        """할일 폴더 경로 생성 테스트"""
        expected_path = os.path.join(self.temp_dir, "todo_1_테스트_할일")
        actual_path = self.file_service.get_todo_folder_path(self.test_todo)
        
        self.assertEqual(expected_path, actual_path)
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_todo_folder_windows(self, mock_subprocess, mock_platform):
        """Windows에서 폴더 열기 테스트"""
        mock_platform.return_value = "Windows"
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        result = self.file_service.open_todo_folder(folder_path)
        
        self.assertTrue(result)
        mock_subprocess.assert_called_once_with(["explorer", folder_path], check=True)
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_todo_folder_macos(self, mock_subprocess, mock_platform):
        """macOS에서 폴더 열기 테스트"""
        mock_platform.return_value = "Darwin"
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        result = self.file_service.open_todo_folder(folder_path)
        
        self.assertTrue(result)
        mock_subprocess.assert_called_once_with(["open", folder_path], check=True)
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_todo_folder_linux(self, mock_subprocess, mock_platform):
        """Linux에서 폴더 열기 테스트"""
        mock_platform.return_value = "Linux"
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        result = self.file_service.open_todo_folder(folder_path)
        
        self.assertTrue(result)
        mock_subprocess.assert_called_once_with(["xdg-open", folder_path], check=True)
    
    @patch('platform.system')
    def test_open_todo_folder_unsupported_os(self, mock_platform):
        """지원하지 않는 OS에서 폴더 열기 테스트"""
        mock_platform.return_value = "UnsupportedOS"
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        result = self.file_service.open_todo_folder(folder_path)
        
        self.assertFalse(result)
    
    def test_open_todo_folder_not_exists(self):
        """존재하지 않는 폴더 열기 테스트"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent")
        result = self.file_service.open_todo_folder(non_existent_path)
        
        self.assertFalse(result)
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_todo_folder_subprocess_error(self, mock_subprocess, mock_platform):
        """subprocess 오류 시 폴더 열기 테스트"""
        mock_platform.return_value = "Windows"
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "explorer")
        folder_path = self.file_service.create_todo_folder(self.test_todo)
        
        result = self.file_service.open_todo_folder(folder_path)
        
        self.assertFalse(result)
    
    def test_ensure_base_folder_exists_success(self):
        """기본 폴더 생성 성공 테스트"""
        new_base_path = os.path.join(self.temp_dir, "new_base_folder")
        file_service = FileService(new_base_path)
        
        self.assertTrue(os.path.exists(new_base_path))
        self.assertTrue(os.path.isdir(new_base_path))
    
    @patch('os.makedirs')
    def test_ensure_base_folder_exists_error(self, mock_makedirs):
        """기본 폴더 생성 오류 테스트"""
        mock_makedirs.side_effect = OSError("Permission denied")
        
        # 오류가 발생해도 예외가 발생하지 않아야 함
        try:
            FileService("invalid_path")
        except Exception as e:
            self.fail(f"ensure_base_folder_exists should not raise exception: {e}")


if __name__ == '__main__':
    unittest.main()