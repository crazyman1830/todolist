import unittest
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storage_service import StorageService
from models.todo import Todo
from models.subtask import SubTask


class TestStorageServiceExtended(unittest.TestCase):
    """확장된 StorageService 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_todos.json")
        self.storage_service = StorageService(self.test_file)
    
    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_empty_file_with_subtask_id(self):
        """빈 파일 생성 시 next_subtask_id 포함 확인"""
        result = self.storage_service.create_empty_file()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.assertIn('next_subtask_id', data)
        self.assertEqual(data['next_subtask_id'], 1)
        self.assertEqual(data['next_id'], 1)
        self.assertEqual(data['todos'], [])
    
    def test_save_todos_with_subtasks(self):
        """하위 작업이 있는 할일 저장 테스트"""
        # 테스트 데이터 생성
        subtask1 = SubTask(1, 1, "하위 작업 1", False, datetime.now())
        subtask2 = SubTask(2, 1, "하위 작업 2", True, datetime.now())
        
        todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder",
            subtasks=[subtask1, subtask2],
            is_expanded=True
        )
        
        # 저장 테스트
        result = self.storage_service.save_todos([todo])
        self.assertTrue(result)
        
        # 파일 내용 확인
        with open(self.test_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.assertEqual(len(data['todos']), 1)
        self.assertEqual(data['next_id'], 2)
        self.assertEqual(data['next_subtask_id'], 3)
        
        saved_todo = data['todos'][0]
        self.assertEqual(len(saved_todo['subtasks']), 2)
        self.assertEqual(saved_todo['subtasks'][0]['title'], "하위 작업 1")
        self.assertEqual(saved_todo['subtasks'][1]['is_completed'], True)
    
    def test_load_todos_with_subtasks(self):
        """하위 작업이 있는 할일 로드 테스트"""
        # 테스트 데이터 파일 생성
        test_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "테스트 할일",
                    "created_at": "2025-01-08T10:00:00",
                    "folder_path": "test_folder",
                    "subtasks": [
                        {
                            "id": 1,
                            "todo_id": 1,
                            "title": "하위 작업 1",
                            "is_completed": False,
                            "created_at": "2025-01-08T10:05:00"
                        },
                        {
                            "id": 2,
                            "todo_id": 1,
                            "title": "하위 작업 2",
                            "is_completed": True,
                            "created_at": "2025-01-08T10:10:00"
                        }
                    ],
                    "is_expanded": True
                }
            ],
            "next_id": 2,
            "next_subtask_id": 3
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as file:
            json.dump(test_data, file, ensure_ascii=False, indent=2)
        
        # 로드 테스트
        todos = self.storage_service.load_todos()
        
        self.assertEqual(len(todos), 1)
        todo = todos[0]
        self.assertEqual(todo.title, "테스트 할일")
        self.assertEqual(len(todo.subtasks), 2)
        self.assertEqual(todo.subtasks[0].title, "하위 작업 1")
        self.assertFalse(todo.subtasks[0].is_completed)
        self.assertEqual(todo.subtasks[1].title, "하위 작업 2")
        self.assertTrue(todo.subtasks[1].is_completed)
    
    def test_get_next_subtask_id(self):
        """다음 하위 작업 ID 가져오기 테스트"""
        # 빈 파일일 때
        self.assertEqual(self.storage_service.get_next_subtask_id(), 1)
        
        # 데이터가 있는 파일일 때
        test_data = {
            "todos": [],
            "next_id": 1,
            "next_subtask_id": 5
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as file:
            json.dump(test_data, file, ensure_ascii=False, indent=2)
        
        self.assertEqual(self.storage_service.get_next_subtask_id(), 5)
    
    def test_migrate_legacy_data(self):
        """기존 CLI 데이터 마이그레이션 테스트"""
        # 기존 형식의 데이터 (subtasks 필드 없음)
        legacy_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "기존 할일",
                    "created_at": "2025-01-08T10:00:00",
                    "folder_path": "test_folder"
                }
            ],
            "next_id": 2
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as file:
            json.dump(legacy_data, file, ensure_ascii=False, indent=2)
        
        # 로드 시 자동 마이그레이션
        todos = self.storage_service.load_todos()
        
        # 마이그레이션된 파일 확인
        with open(self.test_file, 'r', encoding='utf-8') as file:
            migrated_data = json.load(file)
        
        self.assertIn('next_subtask_id', migrated_data)
        self.assertEqual(migrated_data['next_subtask_id'], 1)
        self.assertIn('subtasks', migrated_data['todos'][0])
        self.assertEqual(migrated_data['todos'][0]['subtasks'], [])
        self.assertIn('is_expanded', migrated_data['todos'][0])
        self.assertTrue(migrated_data['todos'][0]['is_expanded'])
        
        # 로드된 객체 확인
        self.assertEqual(len(todos), 1)
        self.assertEqual(len(todos[0].subtasks), 0)
        self.assertTrue(todos[0].is_expanded)
    
    def test_validate_and_repair_duplicate_todo_ids(self):
        """중복된 할일 ID 복구 테스트"""
        # 중복 ID를 가진 할일들
        todo1 = Todo(1, "할일 1", datetime.now(), "folder1")
        todo2 = Todo(1, "할일 2", datetime.now(), "folder2")  # 중복 ID
        
        result = self.storage_service.save_todos([todo1, todo2])
        self.assertTrue(result)
        
        # 로드하여 복구 확인
        todos = self.storage_service.load_todos()
        self.assertEqual(len(todos), 2)
        
        # ID가 서로 다른지 확인
        ids = [todo.id for todo in todos]
        self.assertEqual(len(set(ids)), 2)  # 중복 제거됨
    
    def test_validate_and_repair_subtask_todo_id_mismatch(self):
        """하위 작업의 todo_id 불일치 복구 테스트"""
        # 잘못된 todo_id를 가진 하위 작업
        subtask = SubTask(1, 999, "잘못된 하위 작업", False, datetime.now())  # 잘못된 todo_id
        todo = Todo(1, "할일", datetime.now(), "folder", [subtask])
        
        result = self.storage_service.save_todos([todo])
        self.assertTrue(result)
        
        # 로드하여 복구 확인
        todos = self.storage_service.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(len(todos[0].subtasks), 1)
        self.assertEqual(todos[0].subtasks[0].todo_id, 1)  # 복구됨
    
    def test_validate_and_repair_duplicate_subtask_ids(self):
        """중복된 하위 작업 ID 복구 테스트"""
        # 중복 ID를 가진 하위 작업들
        subtask1 = SubTask(1, 1, "하위 작업 1", False, datetime.now())
        subtask2 = SubTask(1, 1, "하위 작업 2", True, datetime.now())  # 중복 ID
        
        todo = Todo(1, "할일", datetime.now(), "folder", [subtask1, subtask2])
        
        result = self.storage_service.save_todos([todo])
        self.assertTrue(result)
        
        # 로드하여 복구 확인
        todos = self.storage_service.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(len(todos[0].subtasks), 2)
        
        # 하위 작업 ID가 서로 다른지 확인
        subtask_ids = [subtask.id for subtask in todos[0].subtasks]
        self.assertEqual(len(set(subtask_ids)), 2)  # 중복 제거됨
    
    def test_calculate_next_subtask_id(self):
        """다음 하위 작업 ID 계산 테스트"""
        # 하위 작업이 있는 할일들
        subtask1 = SubTask(3, 1, "하위 작업 1", False, datetime.now())
        subtask2 = SubTask(7, 1, "하위 작업 2", True, datetime.now())
        subtask3 = SubTask(5, 2, "하위 작업 3", False, datetime.now())
        
        todo1 = Todo(1, "할일 1", datetime.now(), "folder1", [subtask1, subtask2])
        todo2 = Todo(2, "할일 2", datetime.now(), "folder2", [subtask3])
        
        next_id = self.storage_service._calculate_next_subtask_id([todo1, todo2])
        self.assertEqual(next_id, 8)  # 최대 ID(7) + 1
    
    def test_calculate_next_subtask_id_empty(self):
        """하위 작업이 없을 때 다음 ID 계산 테스트"""
        todo = Todo(1, "할일", datetime.now(), "folder", [])
        
        next_id = self.storage_service._calculate_next_subtask_id([todo])
        self.assertEqual(next_id, 1)
    
    def test_data_integrity_with_backup_and_restore(self):
        """백업 및 복구와 함께 데이터 무결성 테스트"""
        # 정상 데이터로 시작
        subtask = SubTask(1, 1, "하위 작업", False, datetime.now())
        todo = Todo(1, "할일", datetime.now(), "folder", [subtask])
        
        # 첫 번째 저장 (파일이 없으므로 백업은 생성되지 않음)
        result = self.storage_service.save_todos([todo])
        self.assertTrue(result)
        
        # 두 번째 저장 (이제 백업이 생성됨)
        todo2 = Todo(2, "할일 2", datetime.now(), "folder2", [])
        result = self.storage_service.save_todos([todo, todo2])
        self.assertTrue(result)
        
        # 백업 파일 존재 확인
        backup_file = f"{self.test_file}.backup"
        self.assertTrue(os.path.exists(backup_file))
        
        # 손상된 데이터로 파일 덮어쓰기
        with open(self.test_file, 'w', encoding='utf-8') as file:
            file.write("invalid json")
        
        # 로드 시 백업에서 복구되는지 확인
        todos = self.storage_service.load_todos()
        self.assertEqual(len(todos), 1)  # 백업에는 첫 번째 저장 내용만 있음
        self.assertEqual(todos[0].title, "할일")
        self.assertEqual(len(todos[0].subtasks), 1)


if __name__ == '__main__':
    unittest.main()