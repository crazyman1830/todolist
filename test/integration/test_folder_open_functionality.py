#!/usr/bin/env python3
"""
폴더 열기 기능 종합 테스트
"""

import unittest
import tempfile
import shutil
import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_service import FileService
from services.storage_service import StorageService
from services.todo_service import TodoService


class TestFolderOpenFunctionality(unittest.TestCase):
    """폴더 열기 기능 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_service = FileService(self.temp_dir)
        
        # 테스트용 폴더들 생성
        self.test_folders = {
            'normal': os.path.join(self.temp_dir, 'normal_folder'),
            'korean': os.path.join(self.temp_dir, '한글_폴더'),
            'spaces': os.path.join(self.temp_dir, 'folder with spaces'),
            'special': os.path.join(self.temp_dir, 'folder-with_special.chars'),
        }
        
        for folder_path in self.test_folders.values():
            os.makedirs(folder_path, exist_ok=True)
    
    def tearDown(self):
        """테스트 정리"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"임시 디렉토리 정리 실패: {e}")
    
    def test_open_normal_folder(self):
        """일반 폴더 열기 테스트"""
        success, error = self.file_service.open_todo_folder(self.test_folders['normal'])
        self.assertTrue(success, f"일반 폴더 열기 실패: {error}")
    
    def test_open_korean_folder(self):
        """한글 폴더명 열기 테스트"""
        success, error = self.file_service.open_todo_folder(self.test_folders['korean'])
        self.assertTrue(success, f"한글 폴더 열기 실패: {error}")
    
    def test_open_folder_with_spaces(self):
        """공백이 포함된 폴더명 열기 테스트"""
        success, error = self.file_service.open_todo_folder(self.test_folders['spaces'])
        self.assertTrue(success, f"공백 포함 폴더 열기 실패: {error}")
    
    def test_open_folder_with_special_chars(self):
        """특수문자가 포함된 폴더명 열기 테스트"""
        success, error = self.file_service.open_todo_folder(self.test_folders['special'])
        self.assertTrue(success, f"특수문자 포함 폴더 열기 실패: {error}")
    
    def test_open_relative_path(self):
        """상대 경로 폴더 열기 테스트"""
        # 상대 경로 테스트용 폴더 생성
        relative_folder = 'relative_test_folder'
        relative_path = os.path.join(self.temp_dir, relative_folder)
        os.makedirs(relative_path, exist_ok=True)
        
        success, error = self.file_service.open_todo_folder(relative_folder)
        self.assertTrue(success, f"상대 경로 폴더 열기 실패: {error}")
    
    def test_open_nonexistent_folder(self):
        """존재하지 않는 폴더 열기 테스트 (자동 생성)"""
        nonexistent_path = os.path.join(self.temp_dir, 'nonexistent_folder')
        
        # 폴더가 존재하지 않는지 확인
        self.assertFalse(os.path.exists(nonexistent_path))
        
        success, error = self.file_service.open_todo_folder(nonexistent_path)
        
        # 폴더가 자동 생성되고 열기가 성공해야 함
        self.assertTrue(success, f"존재하지 않는 폴더 열기 실패: {error}")
        self.assertTrue(os.path.exists(nonexistent_path), "폴더가 자동 생성되지 않음")
    
    def test_open_empty_path(self):
        """빈 경로 처리 테스트"""
        success, error = self.file_service.open_todo_folder("")
        self.assertFalse(success)
        self.assertIn("비어있습니다", error)
        
        success, error = self.file_service.open_todo_folder("   ")
        self.assertFalse(success)
        self.assertIn("비어있습니다", error)
    
    def test_open_none_path(self):
        """None 경로 처리 테스트"""
        success, error = self.file_service.open_todo_folder(None)
        self.assertFalse(success)
        self.assertIn("비어있습니다", error)


class TestTodoServiceFolderIntegration(unittest.TestCase):
    """TodoService와 폴더 열기 기능 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_todos.json")
        
        self.storage_service = StorageService(self.data_file, auto_save_enabled=False)
        self.file_service = FileService(self.temp_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
    
    def tearDown(self):
        """테스트 정리"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"임시 디렉토리 정리 실패: {e}")
    
    def test_todo_folder_creation_and_opening(self):
        """할일 생성 후 폴더 열기 테스트"""
        # 할일 생성
        todo = self.todo_service.add_todo("테스트 할일")
        self.assertIsNotNone(todo)
        
        # 폴더 경로 확인
        folder_path = todo.folder_path
        self.assertIsNotNone(folder_path)
        
        # 폴더 열기 테스트
        success, error = self.file_service.open_todo_folder(folder_path)
        self.assertTrue(success, f"할일 폴더 열기 실패: {error}")
    
    def test_korean_todo_folder_opening(self):
        """한글 할일명 폴더 열기 테스트"""
        # 한글 할일 생성
        todo = self.todo_service.add_todo("한글 할일 테스트")
        self.assertIsNotNone(todo)
        
        # 폴더 열기 테스트
        success, error = self.file_service.open_todo_folder(todo.folder_path)
        self.assertTrue(success, f"한글 할일 폴더 열기 실패: {error}")
    
    def test_special_chars_todo_folder_opening(self):
        """특수문자 포함 할일명 폴더 열기 테스트"""
        # 특수문자 포함 할일 생성
        todo = self.todo_service.add_todo("특수문자!@#$%^&*()_+ 할일")
        self.assertIsNotNone(todo)
        
        # 폴더 열기 테스트
        success, error = self.file_service.open_todo_folder(todo.folder_path)
        self.assertTrue(success, f"특수문자 포함 할일 폴더 열기 실패: {error}")


if __name__ == '__main__':
    # 테스트 실행 전 안내 메시지
    print("폴더 열기 기능 종합 테스트 시작")
    print("=" * 50)
    print("주의: 이 테스트는 실제로 폴더를 열어서 시각적으로 확인이 필요할 수 있습니다.")
    print("테스트 중에 여러 개의 폴더 창이 열릴 수 있습니다.")
    print("=" * 50)
    
    unittest.main(verbosity=2)