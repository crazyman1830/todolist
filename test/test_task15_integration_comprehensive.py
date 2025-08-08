#!/usr/bin/env python3
"""
Task 15: 통합 테스트 및 사용자 시나리오 검증

GUI와 서비스 계층 통합 테스트, 사용자 시나리오 기반 테스트,
데이터 저장/로드 통합 테스트, 오류 상황 처리 테스트, 성능 테스트를 포함합니다.

Requirements: 모든 요구사항 검증
"""

import unittest
import tkinter as tk
import tempfile
import shutil
import os
import sys
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from gui.todo_tree import TodoTree
from gui.dialogs import AddTodoDialog, EditTodoDialog, AddSubtaskDialog
from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestGUIServiceIntegration(unittest.TestCase):
    """GUI와 서비스 계층 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
        
        # 실제 서비스 인스턴스 생성
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # GUI 컴포넌트는 테스트에서 필요할 때만 생성
        self.main_window = None
    
    def tearDown(self):
        """테스트 정리"""
        if self.main_window:
            try:
                self.main_window.root.destroy()
            except:
                pass
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('os.path.exists')
    def test_gui_service_data_flow(self, mock_exists):
        """GUI와 서비스 간 데이터 흐름 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 서비스를 통해 할일 추가
        todo = self.todo_service.add_todo("GUI Integration Test")
        subtask = self.todo_service.add_subtask(todo.id, "Subtask Test")
        
        # GUI 새로고침
        self.main_window.refresh_todo_tree()
        
        # 트리에 데이터가 반영되었는지 확인
        root_children = self.main_window.todo_tree.get_children()
        self.assertEqual(len(root_children), 1)
        
        # 할일 노드 확인
        todo_node = root_children[0]
        todo_text = self.main_window.todo_tree.item(todo_node, 'text')
        self.assertEqual(todo_text, "GUI Integration Test")
        
        # 하위작업 노드 확인
        subtask_children = self.main_window.todo_tree.get_children(todo_node)
        self.assertEqual(len(subtask_children), 1)
        
        subtask_node = subtask_children[0]
        subtask_text = self.main_window.todo_tree.item(subtask_node, 'text')
        self.assertEqual(subtask_text, "Subtask Test")
    
    @patch('os.path.exists')
    def test_gui_event_service_integration(self, mock_exists):
        """GUI 이벤트와 서비스 통합 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 할일 추가 이벤트 시뮬레이션
        with patch('gui.dialogs.AddTodoDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.get_todo_title.return_value = "Event Test Todo"
            mock_dialog.return_value = mock_dialog_instance
            
            # 할일 추가 버튼 클릭 시뮬레이션
            self.main_window.on_add_todo()
            
            # 서비스에 할일이 추가되었는지 확인
            todos = self.todo_service.get_all_todos()
            self.assertEqual(len(todos), 1)
            self.assertEqual(todos[0].title, "Event Test Todo")
    
    @patch('os.path.exists')
    def test_tree_selection_service_sync(self, mock_exists):
        """트리 선택과 서비스 동기화 테스트"""
        mock_exists.return_value = False
        
        # 테스트 데이터 준비
        todo = self.todo_service.add_todo("Selection Test")
        subtask = self.todo_service.add_subtask(todo.id, "Selection Subtask")
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 트리에서 할일 선택
        todo_nodes = list(self.main_window.todo_tree.todo_nodes.values())
        if todo_nodes:
            todo_node = todo_nodes[0]
            self.main_window.todo_tree.selection_set(todo_node)
            
            # 선택된 할일 ID 확인
            selected_id = self.main_window.todo_tree.get_selected_todo_id()
            self.assertEqual(selected_id, todo.id)


class TestUserScenarioWorkflow(unittest.TestCase):
    """사용자 시나리오 기반 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
        
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.main_window = None
    
    def tearDown(self):
        """테스트 정리"""
        if self.main_window:
            try:
                self.main_window.root.destroy()
            except:
                pass
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_user_workflow(self):
        """완전한 사용자 워크플로우 테스트: 할일 추가 → 하위작업 추가 → 완료 처리"""
        # 1단계: 할일 추가
        todo = self.todo_service.add_todo("프로젝트 완료하기")
        self.assertIsNotNone(todo)
        self.assertEqual(todo.title, "프로젝트 완료하기")
        self.assertTrue(os.path.exists(todo.folder_path))
        
        # 2단계: 하위작업들 추가
        subtask1 = self.todo_service.add_subtask(todo.id, "요구사항 분석")
        subtask2 = self.todo_service.add_subtask(todo.id, "설계 문서 작성")
        subtask3 = self.todo_service.add_subtask(todo.id, "코드 구현")
        subtask4 = self.todo_service.add_subtask(todo.id, "테스트 작성")
        
        self.assertIsNotNone(subtask1)
        self.assertIsNotNone(subtask2)
        self.assertIsNotNone(subtask3)
        self.assertIsNotNone(subtask4)
        
        # 할일의 초기 완료율 확인 (0%)
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.0)
        self.assertFalse(updated_todo.is_completed())
        
        # 3단계: 하위작업들을 순차적으로 완료
        # 첫 번째 하위작업 완료 (25%)
        success = self.todo_service.toggle_subtask_completion(todo.id, subtask1.id)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.25)
        self.assertFalse(updated_todo.is_completed())
        
        # 두 번째 하위작업 완료 (50%)
        success = self.todo_service.toggle_subtask_completion(todo.id, subtask2.id)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 50.0)
        self.assertFalse(updated_todo.is_completed())
        
        # 세 번째 하위작업 완료 (75%)
        success = self.todo_service.toggle_subtask_completion(todo.id, subtask3.id)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.75)
        self.assertFalse(updated_todo.is_completed())
        
        # 마지막 하위작업 완료 (100%)
        success = self.todo_service.toggle_subtask_completion(todo.id, subtask4.id)
        self.assertTrue(success)
        
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 1.0)
        self.assertTrue(updated_todo.is_completed())
        
        # 4단계: 데이터 영속성 확인
        # 새로운 서비스 인스턴스로 데이터 로드
        new_storage_service = StorageService(self.data_file)
        new_todo_service = TodoService(new_storage_service, self.file_service)
        
        loaded_todos = new_todo_service.get_all_todos()
        self.assertEqual(len(loaded_todos), 1)
        
        loaded_todo = loaded_todos[0]
        self.assertEqual(loaded_todo.title, "프로젝트 완료하기")
        self.assertEqual(loaded_todo.get_completion_rate(), 1.0)
        self.assertTrue(loaded_todo.is_completed())
        self.assertEqual(len(loaded_todo.subtasks), 4)
        
        # 모든 하위작업이 완료 상태인지 확인
        for subtask in loaded_todo.subtasks:
            self.assertTrue(subtask.is_completed)
    
    def test_partial_completion_workflow(self):
        """부분 완료 워크플로우 테스트"""
        # 할일과 하위작업 생성
        todo = self.todo_service.add_todo("부분 완료 테스트")
        subtask1 = self.todo_service.add_subtask(todo.id, "완료될 작업")
        subtask2 = self.todo_service.add_subtask(todo.id, "미완료 작업")
        
        # 첫 번째 하위작업만 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask1.id)
        
        # 완료율 확인 (50%)
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.5)
        self.assertFalse(updated_todo.is_completed())
        
        # 완료된 하위작업을 다시 미완료로 변경
        self.todo_service.toggle_subtask_completion(todo.id, subtask1.id)
        
        # 완료율 확인 (0%)
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 0.0)
        self.assertFalse(updated_todo.is_completed())
    
    def test_subtask_management_workflow(self):
        """하위작업 관리 워크플로우 테스트"""
        # 할일 생성
        todo = self.todo_service.add_todo("하위작업 관리 테스트")
        
        # 하위작업 추가
        subtask1 = self.todo_service.add_subtask(todo.id, "첫 번째 하위작업")
        subtask2 = self.todo_service.add_subtask(todo.id, "두 번째 하위작업")
        
        # 하위작업 수정
        success = self.todo_service.update_subtask(todo.id, subtask1.id, "수정된 첫 번째 하위작업")
        self.assertTrue(success)
        
        # 수정 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        updated_subtask = next(s for s in updated_todo.subtasks if s.id == subtask1.id)
        self.assertEqual(updated_subtask.title, "수정된 첫 번째 하위작업")
        
        # 하위작업 삭제
        success = self.todo_service.delete_subtask(todo.id, subtask2.id)
        self.assertTrue(success)
        
        # 삭제 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(len(updated_todo.subtasks), 1)
        self.assertEqual(updated_todo.subtasks[0].id, subtask1.id)


class TestDataStorageLoadIntegration(unittest.TestCase):
    """데이터 저장/로드 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
    
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_data_persistence_across_sessions(self):
        """세션 간 데이터 영속성 테스트"""
        # 첫 번째 세션: 데이터 생성 및 저장
        storage_service1 = StorageService(self.data_file)
        file_service1 = FileService(self.folders_dir)
        todo_service1 = TodoService(storage_service1, file_service1)
        
        # 복잡한 데이터 구조 생성
        todo1 = todo_service1.add_todo("세션 테스트 할일 1")
        todo2 = todo_service1.add_todo("세션 테스트 할일 2")
        
        subtask1_1 = todo_service1.add_subtask(todo1.id, "할일1의 하위작업1")
        subtask1_2 = todo_service1.add_subtask(todo1.id, "할일1의 하위작업2")
        subtask2_1 = todo_service1.add_subtask(todo2.id, "할일2의 하위작업1")
        
        # 일부 하위작업 완료
        todo_service1.toggle_subtask_completion(todo1.id, subtask1_1.id)
        todo_service1.toggle_subtask_completion(todo2.id, subtask2_1.id)
        
        # 첫 번째 세션 종료 (명시적으로 저장)
        del todo_service1, file_service1, storage_service1
        
        # 두 번째 세션: 데이터 로드 및 검증
        storage_service2 = StorageService(self.data_file)
        file_service2 = FileService(self.folders_dir)
        todo_service2 = TodoService(storage_service2, file_service2)
        
        # 데이터 로드 확인
        loaded_todos = todo_service2.get_all_todos()
        self.assertEqual(len(loaded_todos), 2)
        
        # 첫 번째 할일 확인
        loaded_todo1 = next(t for t in loaded_todos if t.title == "세션 테스트 할일 1")
        self.assertEqual(len(loaded_todo1.subtasks), 2)
        self.assertEqual(loaded_todo1.get_completion_rate(), 0.5)
        
        # 두 번째 할일 확인
        loaded_todo2 = next(t for t in loaded_todos if t.title == "세션 테스트 할일 2")
        self.assertEqual(len(loaded_todo2.subtasks), 1)
        self.assertEqual(loaded_todo2.get_completion_rate(), 1.0)
        
        # 폴더 존재 확인
        self.assertTrue(os.path.exists(loaded_todo1.folder_path))
        self.assertTrue(os.path.exists(loaded_todo2.folder_path))
    
    def test_backup_and_recovery(self):
        """백업 및 복구 테스트"""
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 원본 데이터 생성
        original_todo = todo_service.add_todo("백업 테스트 할일")
        original_subtask = todo_service.add_subtask(original_todo.id, "백업 테스트 하위작업")
        
        # 백업 파일 확인
        backup_files = [f for f in os.listdir(os.path.dirname(self.data_file)) 
                       if f.startswith(os.path.basename(self.data_file)) and 'backup' in f]
        self.assertGreater(len(backup_files), 0)
        
        # 원본 파일 손상 시뮬레이션
        with open(self.data_file, 'w') as f:
            f.write("corrupted data")
        
        # 새로운 서비스 인스턴스로 복구 테스트
        new_storage_service = StorageService(self.data_file)
        new_todo_service = TodoService(new_storage_service, file_service)
        
        # 백업에서 복구된 데이터 확인
        recovered_todos = new_todo_service.get_all_todos()
        self.assertEqual(len(recovered_todos), 1)
        self.assertEqual(recovered_todos[0].title, "백업 테스트 할일")
        self.assertEqual(len(recovered_todos[0].subtasks), 1)
    
    def test_concurrent_access_simulation(self):
        """동시 접근 시뮬레이션 테스트"""
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 초기 데이터 생성
        todo = todo_service.add_todo("동시 접근 테스트")
        
        # 동시 수정 시뮬레이션을 위한 함수
        def modify_todo(service, todo_id, new_title):
            try:
                service.update_todo(todo_id, new_title)
                return True
            except Exception:
                return False
        
        # 여러 스레드에서 동시 수정 시도
        results = []
        threads = []
        
        for i in range(5):
            thread = threading.Thread(
                target=lambda i=i: results.append(
                    modify_todo(todo_service, todo.id, f"동시 수정 {i}")
                )
            )
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 최소한 하나의 수정은 성공해야 함
        self.assertTrue(any(results))
        
        # 최종 상태 확인
        final_todo = todo_service.get_todo_by_id(todo.id)
        self.assertIsNotNone(final_todo)
        self.assertTrue(final_todo.title.startswith("동시 수정"))


class TestErrorHandlingScenarios(unittest.TestCase):
    """오류 상황 처리 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
    
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_disk_space_simulation(self):
        """디스크 공간 부족 시뮬레이션"""
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 정상적으로 할일 추가
        todo = todo_service.add_todo("디스크 공간 테스트")
        
        # 디스크 공간 부족 시뮬레이션 (저장 실패)
        with patch.object(storage_service, 'save_todos', return_value=False):
            # 할일 수정 시도 (실패해야 함)
            success = todo_service.update_todo(todo.id, "수정 시도")
            self.assertFalse(success)
            
            # 원본 데이터가 보존되었는지 확인
            original_todo = todo_service.get_todo_by_id(todo.id)
            self.assertEqual(original_todo.title, "디스크 공간 테스트")
    
    def test_file_permission_errors(self):
        """파일 권한 오류 처리 테스트"""
        # Windows에서는 파일 권한 테스트를 다르게 처리
        if os.name == 'nt':
            self.skipTest("Windows에서는 파일 권한 테스트를 스킵합니다")
        
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 정상적으로 할일 추가
        todo = todo_service.add_todo("권한 테스트")
        
        # 데이터 파일을 읽기 전용으로 변경
        import stat
        os.chmod(self.data_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
        try:
            # 할일 수정 시도 (실패해야 함)
            success = todo_service.update_todo(todo.id, "권한 오류 수정")
            self.assertFalse(success)
        finally:
            # 권한 복원
            os.chmod(self.data_file, stat.S_IRWXU)
    
    def test_corrupted_data_recovery(self):
        """손상된 데이터 복구 테스트"""
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 정상 데이터 생성
        todo = todo_service.add_todo("복구 테스트")
        subtask = todo_service.add_subtask(todo.id, "복구 테스트 하위작업")
        
        # 백업 파일 생성 확인
        backup_file = f"{self.data_file}.backup"
        self.assertTrue(os.path.exists(backup_file))
        
        # 원본 파일 손상
        with open(self.data_file, 'w') as f:
            f.write('{"invalid": "json"')
        
        # 새로운 서비스 인스턴스로 복구
        new_storage_service = StorageService(self.data_file)
        new_todo_service = TodoService(new_storage_service, file_service)
        
        # 복구된 데이터 확인
        recovered_todos = new_todo_service.get_all_todos()
        self.assertEqual(len(recovered_todos), 1)
        self.assertEqual(recovered_todos[0].title, "복구 테스트")
    
    def test_invalid_user_input_handling(self):
        """잘못된 사용자 입력 처리 테스트"""
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 빈 제목으로 할일 추가 시도
        with self.assertRaises(ValueError):
            todo_service.add_todo("")
        
        with self.assertRaises(ValueError):
            todo_service.add_todo("   ")
        
        with self.assertRaises(ValueError):
            todo_service.add_todo("\t\n")
        
        # 존재하지 않는 할일 수정 시도
        with self.assertRaises(ValueError):
            todo_service.update_todo(999, "존재하지 않는 할일")
        
        # 존재하지 않는 할일 삭제 시도
        with self.assertRaises(ValueError):
            todo_service.delete_todo(999)


class TestPerformanceScenarios(unittest.TestCase):
    """성능 테스트"""
    
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
    
    def test_large_dataset_performance(self):
        """대량 데이터 처리 성능 테스트"""
        # 대량의 할일 생성 (100개)
        start_time = time.time()
        
        todos = []
        for i in range(100):
            todo = self.todo_service.add_todo(f"성능 테스트 할일 {i}")
            todos.append(todo)
            
            # 각 할일에 5개의 하위작업 추가
            for j in range(5):
                self.todo_service.add_subtask(todo.id, f"하위작업 {j}")
        
        creation_time = time.time() - start_time
        
        # 생성 시간이 합리적인 범위 내인지 확인 (10초 이내)
        self.assertLess(creation_time, 10.0, f"대량 데이터 생성 시간이 너무 오래 걸림: {creation_time:.2f}초")
        
        # 데이터 조회 성능 테스트
        start_time = time.time()
        all_todos = self.todo_service.get_all_todos()
        query_time = time.time() - start_time
        
        # 조회 시간이 합리적인 범위 내인지 확인 (1초 이내)
        self.assertLess(query_time, 1.0, f"대량 데이터 조회 시간이 너무 오래 걸림: {query_time:.2f}초")
        
        # 데이터 정확성 확인
        self.assertEqual(len(all_todos), 100)
        
        # 각 할일의 하위작업 개수 확인
        for todo in all_todos:
            self.assertEqual(len(todo.subtasks), 5)
    
    def test_frequent_updates_performance(self):
        """빈번한 업데이트 성능 테스트"""
        # 기본 할일 생성
        todo = self.todo_service.add_todo("업데이트 성능 테스트")
        
        # 하위작업 10개 추가
        subtasks = []
        for i in range(10):
            subtask = self.todo_service.add_subtask(todo.id, f"업데이트 테스트 하위작업 {i}")
            subtasks.append(subtask)
        
        # 빈번한 완료 상태 토글 (100회)
        start_time = time.time()
        
        for _ in range(100):
            for subtask in subtasks:
                self.todo_service.toggle_subtask_completion(todo.id, subtask.id)
        
        update_time = time.time() - start_time
        
        # 업데이트 시간이 합리적인 범위 내인지 확인 (10초 이내)
        self.assertLess(update_time, 10.0, f"빈번한 업데이트 시간이 너무 오래 걸림: {update_time:.2f}초")
        
        # 최종 상태 확인 (모든 하위작업이 완료 상태여야 함)
        final_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertTrue(final_todo.is_completed())
    
    def test_memory_usage_with_large_dataset(self):
        """대량 데이터셋에서의 메모리 사용량 테스트"""
        try:
            import psutil
            import os
            
            # 초기 메모리 사용량 측정
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 대량 데이터 생성 (100개 할일, 각각 5개 하위작업) - 축소된 테스트
            for i in range(100):
                todo = self.todo_service.add_todo(f"메모리 테스트 할일 {i}")
                for j in range(5):
                    self.todo_service.add_subtask(todo.id, f"메모리 테스트 하위작업 {j}")
            
            # 최종 메모리 사용량 측정
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # 메모리 증가량이 합리적인 범위 내인지 확인 (50MB 이내)
            self.assertLess(memory_increase, 50, 
                           f"메모리 사용량이 너무 많이 증가함: {memory_increase:.2f}MB")
            
            # 데이터 정확성 확인
            all_todos = self.todo_service.get_all_todos()
            self.assertEqual(len(all_todos), 100)
            
        except ImportError:
            self.skipTest("psutil 모듈이 설치되지 않아 메모리 테스트를 건너뜁니다")


if __name__ == '__main__':
    # 테스트 실행 시 상세한 출력
    unittest.main(verbosity=2)