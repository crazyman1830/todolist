import unittest
import os
import json
import tempfile
import shutil
import sys
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.storage_service import StorageService
from models.todo import Todo


class TestStorageService(unittest.TestCase):
    """StorageService에 대한 단위 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.test_dir, 'test_todos.json')
        self.storage_service = StorageService(self.test_file_path)
        
        # 테스트용 할일 데이터
        self.sample_todos = [
            Todo(
                id=1,
                title="테스트 할일 1",
                created_at=datetime(2025, 1, 8, 10, 30, 0),
                folder_path="todo_folders/todo_1_테스트_할일_1"
            ),
            Todo(
                id=2,
                title="테스트 할일 2",
                created_at=datetime(2025, 1, 8, 11, 0, 0),
                folder_path="todo_folders/todo_2_테스트_할일_2"
            )
        ]
    
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_file_exists_when_file_not_exists(self):
        """파일이 존재하지 않을 때 file_exists() 테스트"""
        self.assertFalse(self.storage_service.file_exists())
    
    def test_file_exists_when_file_exists(self):
        """파일이 존재할 때 file_exists() 테스트"""
        # 빈 파일 생성
        self.storage_service.create_empty_file()
        self.assertTrue(self.storage_service.file_exists())
    
    def test_create_empty_file_success(self):
        """빈 파일 생성 성공 테스트"""
        result = self.storage_service.create_empty_file()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_file_path))
        
        # 파일 내용 확인
        with open(self.test_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        expected_data = {
            "todos": [],
            "next_id": 1
        }
        self.assertEqual(data, expected_data) 
   
    def test_create_empty_file_in_nonexistent_directory(self):
        """존재하지 않는 디렉토리에 빈 파일 생성 테스트"""
        # 새로운 경로 설정 (존재하지 않는 디렉토리)
        new_dir = os.path.join(self.test_dir, 'new_subdir')
        new_file_path = os.path.join(new_dir, 'todos.json')
        new_storage_service = StorageService(new_file_path)
        
        result = new_storage_service.create_empty_file()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_file_path))
        self.assertTrue(os.path.exists(new_dir))
    
    def test_save_todos_success(self):
        """할일 저장 성공 테스트"""
        result = self.storage_service.save_todos(self.sample_todos)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_file_path))
        
        # 저장된 데이터 확인
        with open(self.test_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.assertEqual(len(data['todos']), 2)
        self.assertEqual(data['next_id'], 3)
        self.assertEqual(data['todos'][0]['title'], "테스트 할일 1")
        self.assertEqual(data['todos'][1]['title'], "테스트 할일 2")
    
    def test_save_empty_todos_list(self):
        """빈 할일 목록 저장 테스트"""
        result = self.storage_service.save_todos([])
        
        self.assertTrue(result)
        
        with open(self.test_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.assertEqual(data['todos'], [])
        self.assertEqual(data['next_id'], 1)
    
    def test_load_todos_from_empty_file(self):
        """빈 파일에서 할일 로드 테스트"""
        # 빈 파일 생성
        self.storage_service.create_empty_file()
        
        todos = self.storage_service.load_todos()
        
        self.assertEqual(len(todos), 0)
        self.assertIsInstance(todos, list)
    
    def test_load_todos_from_nonexistent_file(self):
        """존재하지 않는 파일에서 할일 로드 테스트"""
        todos = self.storage_service.load_todos()
        
        self.assertEqual(len(todos), 0)
        # 빈 파일이 자동 생성되었는지 확인
        self.assertTrue(os.path.exists(self.test_file_path))
    
    def test_load_todos_success(self):
        """할일 로드 성공 테스트"""
        # 먼저 데이터 저장
        self.storage_service.save_todos(self.sample_todos)
        
        # 데이터 로드
        loaded_todos = self.storage_service.load_todos()
        
        self.assertEqual(len(loaded_todos), 2)
        self.assertEqual(loaded_todos[0].id, 1)
        self.assertEqual(loaded_todos[0].title, "테스트 할일 1")
        self.assertEqual(loaded_todos[1].id, 2)
        self.assertEqual(loaded_todos[1].title, "테스트 할일 2")    

    def test_load_todos_with_corrupted_json(self):
        """손상된 JSON 파일에서 할일 로드 테스트"""
        # 손상된 JSON 파일 생성
        with open(self.test_file_path, 'w', encoding='utf-8') as file:
            file.write('{"invalid": json content}')
        
        todos = self.storage_service.load_todos()
        
        # 손상된 파일의 경우 빈 목록 반환
        self.assertEqual(len(todos), 0)
        self.assertIsInstance(todos, list)
    
    def test_load_todos_with_invalid_structure(self):
        """잘못된 구조의 JSON 파일에서 할일 로드 테스트"""
        # 잘못된 구조의 JSON 파일 생성
        invalid_data = {"wrong_key": "wrong_value"}
        with open(self.test_file_path, 'w', encoding='utf-8') as file:
            json.dump(invalid_data, file)
        
        todos = self.storage_service.load_todos()
        
        self.assertEqual(len(todos), 0)
        self.assertIsInstance(todos, list)
    
    def test_load_todos_with_partial_corruption(self):
        """일부 할일 데이터가 손상된 경우 테스트"""
        # 일부 데이터가 손상된 JSON 생성
        corrupted_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "정상 할일",
                    "created_at": "2025-01-08T10:30:00",
                    "folder_path": "todo_folders/todo_1"
                },
                {
                    "id": 2,
                    "title": "손상된 할일",
                    # created_at 누락
                    "folder_path": "todo_folders/todo_2"
                },
                {
                    "id": 3,
                    "title": "또 다른 정상 할일",
                    "created_at": "2025-01-08T11:00:00",
                    "folder_path": "todo_folders/todo_3"
                }
            ],
            "next_id": 4
        }
        
        with open(self.test_file_path, 'w', encoding='utf-8') as file:
            json.dump(corrupted_data, file)
        
        todos = self.storage_service.load_todos()
        
        # 정상적인 할일만 로드되어야 함
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0].title, "정상 할일")
        self.assertEqual(todos[1].title, "또 다른 정상 할일")
    
    def test_get_next_id_from_empty_file(self):
        """빈 파일에서 다음 ID 가져오기 테스트"""
        self.storage_service.create_empty_file()
        
        next_id = self.storage_service.get_next_id()
        
        self.assertEqual(next_id, 1)
    
    def test_get_next_id_from_existing_data(self):
        """기존 데이터에서 다음 ID 가져오기 테스트"""
        self.storage_service.save_todos(self.sample_todos)
        
        next_id = self.storage_service.get_next_id()
        
        self.assertEqual(next_id, 3)
    
    def test_get_next_id_from_nonexistent_file(self):
        """존재하지 않는 파일에서 다음 ID 가져오기 테스트"""
        next_id = self.storage_service.get_next_id()
        
        self.assertEqual(next_id, 1) 
   
    def test_backup_creation(self):
        """백업 파일 생성 테스트"""
        # 초기 데이터 저장
        self.storage_service.save_todos(self.sample_todos)
        
        # 백업 파일이 생성되었는지 확인
        backup_path = f"{self.test_file_path}.backup"
        
        # 새로운 데이터로 다시 저장 (백업 생성 트리거)
        new_todo = Todo(
            id=3,
            title="새로운 할일",
            created_at=datetime.now(),
            folder_path="todo_folders/todo_3"
        )
        self.storage_service.save_todos([new_todo])
        
        # 백업 파일 존재 확인
        self.assertTrue(os.path.exists(backup_path))
    
    def test_backup_restoration(self):
        """백업에서 복구 테스트"""
        # 정상 데이터 저장 (백업 생성됨)
        self.storage_service.save_todos(self.sample_todos)
        
        # 백업 파일 경로
        backup_path = f"{self.test_file_path}.backup"
        
        # 메인 파일을 손상시킴
        with open(self.test_file_path, 'w', encoding='utf-8') as file:
            file.write('invalid json')
        
        # 백업 파일을 수동으로 생성 (정상 데이터로)
        backup_data = {
            "todos": [todo.to_dict() for todo in self.sample_todos],
            "next_id": 3
        }
        with open(backup_path, 'w', encoding='utf-8') as file:
            json.dump(backup_data, file, default=str)
        
        # 데이터 로드 시도 (백업에서 복구되어야 함)
        todos = self.storage_service.load_todos()
        
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0].title, "테스트 할일 1")
        self.assertEqual(todos[1].title, "테스트 할일 2")
    
    def test_ensure_data_directory_creation(self):
        """데이터 디렉토리 자동 생성 테스트"""
        # 존재하지 않는 깊은 경로
        deep_path = os.path.join(self.test_dir, 'level1', 'level2', 'todos.json')
        storage_service = StorageService(deep_path)
        
        # 파일 생성
        result = storage_service.create_empty_file()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(deep_path))
        self.assertTrue(os.path.exists(os.path.dirname(deep_path)))


if __name__ == '__main__':
    unittest.main()