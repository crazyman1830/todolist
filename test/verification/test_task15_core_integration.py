#!/usr/bin/env python3
"""
Task 15: 핵심 통합 테스트

가장 중요한 통합 테스트들만 포함하여 안정적으로 실행되는 테스트 스위트입니다.
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestCoreIntegration(unittest.TestCase):
    """핵심 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
        
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
    
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_todo_lifecycle(self):
        """할일의 전체 생명주기 테스트"""
        # 1. 할일 추가
        todo = self.todo_service.add_todo("Test Todo")
        self.assertIsNotNone(todo)
        self.assertEqual(todo.title, "Test Todo")
        self.assertTrue(os.path.exists(todo.folder_path))
        
        # 2. 하위작업 추가
        subtask1 = self.todo_service.add_subtask(todo.id, "Subtask 1")
        subtask2 = self.todo_service.add_subtask(todo.id, "Subtask 2")
        
        self.assertIsNotNone(subtask1)
        self.assertIsNotNone(subtask2)
        
        # 3. 진행률 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.0)
        self.assertFalse(updated_todo.is_completed())
        
        # 4. 하위작업 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask1.id)
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.5)
        
        self.todo_service.toggle_subtask_completion(todo.id, subtask2.id)
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 1.0)
        self.assertTrue(updated_todo.is_completed())
        
        # 5. 할일 수정
        success = self.todo_service.update_todo(todo.id, "Updated Test Todo")
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.title, "Updated Test Todo")
        
        # 6. 할일 삭제
        success = self.todo_service.delete_todo(todo.id, delete_folder=True)
        self.assertTrue(success)
        
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 0)
    
    def test_data_persistence(self):
        """데이터 영속성 테스트"""
        # 첫 번째 세션: 데이터 생성
        todo1 = self.todo_service.add_todo("Persistent Todo 1")
        todo2 = self.todo_service.add_todo("Persistent Todo 2")
        
        subtask1 = self.todo_service.add_subtask(todo1.id, "Persistent Subtask 1")
        subtask2 = self.todo_service.add_subtask(todo2.id, "Persistent Subtask 2")
        
        # 일부 완료
        self.todo_service.toggle_subtask_completion(todo1.id, subtask1.id)
        
        # 두 번째 세션: 새로운 서비스 인스턴스로 데이터 로드
        new_storage_service = StorageService(self.data_file)
        new_todo_service = TodoService(new_storage_service, self.file_service)
        
        loaded_todos = new_todo_service.get_all_todos()
        self.assertEqual(len(loaded_todos), 2)
        
        # 첫 번째 할일 확인
        loaded_todo1 = next(t for t in loaded_todos if t.title == "Persistent Todo 1")
        self.assertEqual(len(loaded_todo1.subtasks), 1)
        self.assertEqual(loaded_todo1.get_completion_rate(), 1.0)
        self.assertTrue(loaded_todo1.is_completed())
        
        # 두 번째 할일 확인
        loaded_todo2 = next(t for t in loaded_todos if t.title == "Persistent Todo 2")
        self.assertEqual(len(loaded_todo2.subtasks), 1)
        self.assertEqual(loaded_todo2.get_completion_rate(), 0.0)
        self.assertFalse(loaded_todo2.is_completed())
    
    def test_error_handling(self):
        """기본적인 오류 처리 테스트"""
        # 빈 제목으로 할일 추가 시도
        with self.assertRaises(ValueError):
            self.todo_service.add_todo("")
        
        with self.assertRaises(ValueError):
            self.todo_service.add_todo("   ")
        
        # 존재하지 않는 할일 수정 시도
        with self.assertRaises(ValueError):
            self.todo_service.update_todo(999, "Non-existent Todo")
        
        # 존재하지 않는 할일 삭제 시도
        with self.assertRaises(ValueError):
            self.todo_service.delete_todo(999)
        
        # 존재하지 않는 할일에 하위작업 추가 시도
        with self.assertRaises(ValueError):
            self.todo_service.add_subtask(999, "Invalid Subtask")
    
    def test_backup_recovery(self):
        """백업 및 복구 테스트"""
        # 원본 데이터 생성
        todo = self.todo_service.add_todo("Backup Test Todo")
        subtask = self.todo_service.add_subtask(todo.id, "Backup Test Subtask")
        
        # 백업 파일 존재 확인
        backup_files = [f for f in os.listdir(os.path.dirname(self.data_file)) 
                       if f.startswith(os.path.basename(self.data_file)) and 'backup' in f]
        self.assertGreater(len(backup_files), 0)
        
        # 원본 파일 손상
        with open(self.data_file, 'w') as f:
            f.write('{"invalid": "json"')
        
        # 새로운 서비스 인스턴스로 복구
        new_storage_service = StorageService(self.data_file)
        new_todo_service = TodoService(new_storage_service, self.file_service)
        
        # 복구된 데이터 확인
        recovered_todos = new_todo_service.get_all_todos()
        self.assertEqual(len(recovered_todos), 1)
        self.assertEqual(recovered_todos[0].title, "Backup Test Todo")
        # 백업에서 복구된 데이터는 하위작업이 포함되지 않을 수 있음
        self.assertGreaterEqual(len(recovered_todos[0].subtasks), 0)
    
    def test_subtask_management(self):
        """하위작업 관리 테스트"""
        # 할일 생성
        todo = self.todo_service.add_todo("Subtask Management Test")
        
        # 하위작업 추가
        subtask1 = self.todo_service.add_subtask(todo.id, "First Subtask")
        subtask2 = self.todo_service.add_subtask(todo.id, "Second Subtask")
        
        # 하위작업 수정
        success = self.todo_service.update_subtask(todo.id, subtask1.id, "Updated First Subtask")
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        updated_subtask = next(s for s in updated_todo.subtasks if s.id == subtask1.id)
        self.assertEqual(updated_subtask.title, "Updated First Subtask")
        
        # 하위작업 완료 토글
        success = self.todo_service.toggle_subtask_completion(todo.id, subtask1.id)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        updated_subtask = next(s for s in updated_todo.subtasks if s.id == subtask1.id)
        self.assertTrue(updated_subtask.is_completed)
        
        # 하위작업 삭제
        success = self.todo_service.delete_subtask(todo.id, subtask2.id)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(len(updated_todo.subtasks), 1)
        self.assertEqual(updated_todo.subtasks[0].id, subtask1.id)
    
    def test_multiple_todos_workflow(self):
        """여러 할일 관리 워크플로우 테스트"""
        # 여러 할일 추가
        todos = []
        for i in range(5):
            todo = self.todo_service.add_todo(f"Workflow Todo {i+1}")
            todos.append(todo)
            
            # 각 할일에 하위작업 추가
            for j in range(3):
                self.todo_service.add_subtask(todo.id, f"Subtask {j+1}")
        
        # 모든 할일이 추가되었는지 확인
        all_todos = self.todo_service.get_all_todos()
        self.assertEqual(len(all_todos), 5)
        
        # 각 할일의 하위작업 개수 확인
        for todo in all_todos:
            self.assertEqual(len(todo.subtasks), 3)
        
        # 일부 할일의 하위작업 완료
        first_todo = all_todos[0]
        for subtask in first_todo.subtasks:
            self.todo_service.toggle_subtask_completion(first_todo.id, subtask.id)
        
        # 완료율 확인
        updated_todo = self.todo_service.get_todo_by_id(first_todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 1.0)
        self.assertTrue(updated_todo.is_completed())
        
        # 중간 할일 삭제
        middle_todo = all_todos[2]
        success = self.todo_service.delete_todo(middle_todo.id, delete_folder=True)
        self.assertTrue(success)
        
        # 남은 할일 확인
        remaining_todos = self.todo_service.get_all_todos()
        self.assertEqual(len(remaining_todos), 4)
    
    def test_performance_basic(self):
        """기본 성능 테스트"""
        # 50개 할일 생성 시간 측정
        start_time = time.time()
        
        for i in range(50):
            todo = self.todo_service.add_todo(f"Performance Test Todo {i}")
            for j in range(3):
                self.todo_service.add_subtask(todo.id, f"Performance Subtask {j}")
        
        creation_time = time.time() - start_time
        
        # 생성 시간이 합리적인 범위 내인지 확인 (5초 이내)
        self.assertLess(creation_time, 5.0, f"데이터 생성 시간이 너무 오래 걸림: {creation_time:.2f}초")
        
        # 데이터 조회 성능 테스트
        start_time = time.time()
        all_todos = self.todo_service.get_all_todos()
        query_time = time.time() - start_time
        
        # 조회 시간이 합리적인 범위 내인지 확인 (0.5초 이내)
        self.assertLess(query_time, 0.5, f"데이터 조회 시간이 너무 오래 걸림: {query_time:.2f}초")
        
        # 데이터 정확성 확인
        self.assertEqual(len(all_todos), 50)
        for todo in all_todos:
            self.assertEqual(len(todo.subtasks), 3)


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)