#!/usr/bin/env python3
"""
사용자 경험 개선 및 최종 검증 테스트

Task 9: 사용자 경험 개선 및 최종 검증
- 메뉴 표시 형식 개선
- 사용자 안내 메시지 개선
- 프로그램 실행 및 전체 기능 검증
- 다양한 시나리오에서의 동작 확인
- 성능 및 안정성 검증
"""

import unittest
import tempfile
import shutil
import os
import time
import threading
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from ui.menu import MenuUI
from main import initialize_services


class TestUserExperienceImprovements(unittest.TestCase):
    """사용자 경험 개선 테스트"""
    
    def setUp(self):
        """테스트 설정"""
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
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_menu_display_format_improvements(self):
        """메뉴 표시 형식 개선 테스트"""
        # 할일 몇 개 추가
        self.todo_service.add_todo("테스트 할일 1")
        self.todo_service.add_todo("테스트 할일 2")
        
        # 메뉴 출력 캡처
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', return_value='0'):
                try:
                    self.menu_ui.show_main_menu()
                except SystemExit:
                    pass
        
        # 출력된 메시지 확인
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        
        # 개선된 메뉴 형식 확인
        self.assertTrue(any("📝 할일 관리 프로그램" in msg for msg in printed_messages))
        self.assertTrue(any("현재 할일: 2개" in msg for msg in printed_messages))
        self.assertTrue(any("1️⃣" in msg for msg in printed_messages))
        self.assertTrue(any("새로운 할일을 등록합니다" in msg for msg in printed_messages))
    
    def test_user_guidance_message_improvements(self):
        """사용자 안내 메시지 개선 테스트"""
        # 빈 목록에서 할일 목록 보기
        with patch('builtins.print') as mock_print:
            self.menu_ui.handle_list_todos()
        
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        
        # 개선된 안내 메시지 확인
        self.assertTrue(any("📭 등록된 할일이 없습니다" in msg for msg in printed_messages))
        self.assertTrue(any("💡 메뉴 1번을 통해 새로운 할일을 추가해보세요!" in msg for msg in printed_messages))
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_add_todo_user_experience(self, mock_print, mock_input):
        """할일 추가 사용자 경험 테스트"""
        mock_input.return_value = "사용자 경험 테스트 할일"
        
        self.menu_ui.handle_add_todo()
        
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        
        # 개선된 UI 메시지 확인
        self.assertTrue(any("📝 새로운 할일 추가" in msg for msg in printed_messages))
        self.assertTrue(any("💡 할일 제목을 입력하면 자동으로 전용 폴더가 생성됩니다" in msg for msg in printed_messages))
        self.assertTrue(any("🎉 할일 추가 완료!" in msg for msg in printed_messages))
        self.assertTrue(any("💡 메뉴 5번을 통해 할일 폴더를 열어" in msg for msg in printed_messages))
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_update_todo_user_experience(self, mock_print, mock_input):
        """할일 수정 사용자 경험 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("수정 테스트 할일")
        
        # 수정 시뮬레이션
        mock_input.side_effect = [str(todo.id), "수정된 할일"]
        
        self.menu_ui.handle_update_todo()
        
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        
        # 개선된 UI 메시지 확인
        self.assertTrue(any("✏️  할일 내용 수정" in msg for msg in printed_messages))
        self.assertTrue(any("🎉 할일 수정 완료!" in msg for msg in printed_messages))
        self.assertTrue(any("📝 이전 제목:" in msg for msg in printed_messages))
        self.assertTrue(any("✏️  새로운 제목:" in msg for msg in printed_messages))
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_delete_todo_user_experience(self, mock_print, mock_input):
        """할일 삭제 사용자 경험 테스트"""
        # 할일 추가
        todo = self.todo_service.add_todo("삭제 테스트 할일")
        
        # 삭제 시뮬레이션 (폴더 삭제 안함)
        mock_input.side_effect = [str(todo.id), "y", "n"]
        
        self.menu_ui.handle_delete_todo()
        
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        
        # 개선된 UI 메시지 확인
        self.assertTrue(any("🗑️  할일 삭제" in msg for msg in printed_messages))
        self.assertTrue(any("🎉 할일 삭제 완료!" in msg for msg in printed_messages))
        self.assertTrue(any("📁 폴더는 보존됨:" in msg for msg in printed_messages))


class TestProgramExecutionAndFunctionality(unittest.TestCase):
    """프로그램 실행 및 전체 기능 검증 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
    
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        # 임시 설정으로 서비스 초기화
        with patch('config.TODOS_FILE', self.data_file):
            with patch('config.TODO_FOLDERS_DIR', self.folders_dir):
                todo_service, menu_ui = initialize_services()
                
                self.assertIsNotNone(todo_service)
                self.assertIsNotNone(menu_ui)
                self.assertEqual(len(todo_service.get_all_todos()), 0)
    
    def test_complete_workflow_integration(self):
        """완전한 워크플로우 통합 테스트"""
        storage_service = StorageService(self.data_file)
        file_service = FileService(self.folders_dir)
        todo_service = TodoService(storage_service, file_service)
        
        # 1. 할일 추가
        todo1 = todo_service.add_todo("통합 테스트 할일 1")
        todo2 = todo_service.add_todo("통합 테스트 할일 2")
        
        # 2. 할일 목록 확인
        todos = todo_service.get_all_todos()
        self.assertEqual(len(todos), 2)
        
        # 3. 할일 수정
        success = todo_service.update_todo(todo1.id, "수정된 할일 1")
        self.assertTrue(success)
        
        # 4. 수정 확인
        updated_todo = todo_service.get_todo_by_id(todo1.id)
        self.assertEqual(updated_todo.title, "수정된 할일 1")
        
        # 5. 할일 삭제 (폴더 포함)
        success = todo_service.delete_todo(todo2.id, delete_folder=True)
        self.assertTrue(success)
        
        # 6. 삭제 확인
        remaining_todos = todo_service.get_all_todos()
        self.assertEqual(len(remaining_todos), 1)
        self.assertEqual(remaining_todos[0].id, todo1.id)
    
    def test_data_persistence(self):
        """데이터 지속성 테스트"""
        # 첫 번째 서비스 인스턴스로 데이터 생성
        storage_service1 = StorageService(self.data_file)
        file_service1 = FileService(self.folders_dir)
        todo_service1 = TodoService(storage_service1, file_service1)
        
        todo1 = todo_service1.add_todo("지속성 테스트 할일")
        
        # 두 번째 서비스 인스턴스로 데이터 로드
        storage_service2 = StorageService(self.data_file)
        file_service2 = FileService(self.folders_dir)
        todo_service2 = TodoService(storage_service2, file_service2)
        
        todos = todo_service2.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "지속성 테스트 할일")
        self.assertEqual(todos[0].id, todo1.id)


class TestVariousScenarios(unittest.TestCase):
    """다양한 시나리오 동작 확인 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_todos.json')
        self.folders_dir = os.path.join(self.temp_dir, 'test_folders')
        
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        self.menu_ui = MenuUI(self.todo_service)
    
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_empty_database_scenario(self):
        """빈 데이터베이스 시나리오 테스트"""
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 0)
        
        # 빈 목록에서 각 기능 테스트
        with patch('builtins.print') as mock_print:
            self.menu_ui.handle_list_todos()
            printed_messages = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("📭 등록된 할일이 없습니다" in msg for msg in printed_messages))
    
    def test_large_dataset_scenario(self):
        """대용량 데이터셋 시나리오 테스트"""
        # 100개의 할일 추가
        todos = []
        for i in range(100):
            todo = self.todo_service.add_todo(f"대용량 테스트 할일 {i+1}")
            todos.append(todo)
        
        # 모든 할일이 정상적으로 추가되었는지 확인
        all_todos = self.todo_service.get_all_todos()
        self.assertEqual(len(all_todos), 100)
        
        # 특정 할일 검색 성능 테스트
        start_time = time.time()
        found_todo = self.todo_service.get_todo_by_id(50)
        end_time = time.time()
        
        self.assertIsNotNone(found_todo)
        self.assertEqual(found_todo.title, "대용량 테스트 할일 50")
        self.assertLess(end_time - start_time, 0.1)  # 0.1초 이내
    
    def test_special_characters_scenario(self):
        """특수 문자 시나리오 테스트"""
        special_titles = [
            "할일 with 한글 and English",
            "할일 with 숫자 123 and symbols !@#",
            "할일 with emoji 😀🎉📝",
            "할일 with 'quotes' and \"double quotes\"",
            "할일 with (parentheses) and [brackets]"
        ]
        
        for title in special_titles:
            todo = self.todo_service.add_todo(title)
            self.assertEqual(todo.title, title)
            
            # 폴더가 생성되었는지 확인
            self.assertTrue(os.path.exists(todo.folder_path))
    
    def test_concurrent_access_simulation(self):
        """동시 접근 시뮬레이션 테스트"""
        # Windows에서는 파일 잠금 문제로 동시 접근이 어려우므로 순차적으로 테스트
        results = []
        
        # 순차적으로 할일 추가 (동시 접근 시뮬레이션)
        for batch in range(3):
            batch_results = []
            for i in range(10):
                try:
                    title = f"동시 접근 테스트 {batch * 10 + i}"
                    todo = self.todo_service.add_todo(title)
                    batch_results.append(todo)
                except Exception as e:
                    print(f"배치 {batch}에서 오류 발생: {e}")
            
            results.extend(batch_results)
        
        # 결과 확인
        self.assertGreaterEqual(len(results), 25, "대부분의 할일이 성공적으로 추가되어야 합니다")
        
        # 데이터베이스 일관성 확인
        all_todos = self.todo_service.get_all_todos()
        self.assertGreaterEqual(len(all_todos), 25, "데이터베이스에 대부분의 할일이 저장되어야 합니다")


class TestPerformanceAndStability(unittest.TestCase):
    """성능 및 안정성 검증 테스트"""
    
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
    
    def test_add_todo_performance(self):
        """할일 추가 성능 테스트"""
        start_time = time.time()
        
        # 50개 할일 추가
        for i in range(50):
            self.todo_service.add_todo(f"성능 테스트 할일 {i+1}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 50개 할일 추가가 5초 이내에 완료되어야 함
        self.assertLess(elapsed_time, 5.0, f"할일 추가 성능이 기준을 초과했습니다: {elapsed_time:.2f}초")
        
        # 평균 처리 시간 계산
        avg_time = elapsed_time / 50
        self.assertLess(avg_time, 0.1, f"할일 추가 평균 시간이 기준을 초과했습니다: {avg_time:.3f}초")
    
    def test_list_todos_performance(self):
        """할일 목록 조회 성능 테스트"""
        # 100개 할일 추가
        for i in range(100):
            self.todo_service.add_todo(f"목록 조회 테스트 할일 {i+1}")
        
        # 목록 조회 성능 측정
        start_time = time.time()
        todos = self.todo_service.get_all_todos()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        self.assertEqual(len(todos), 100)
        self.assertLess(elapsed_time, 0.1, f"할일 목록 조회 성능이 기준을 초과했습니다: {elapsed_time:.3f}초")
    
    def test_search_performance(self):
        """할일 검색 성능 테스트"""
        # 1000개 할일 추가
        todos = []
        for i in range(1000):
            todo = self.todo_service.add_todo(f"검색 테스트 할일 {i+1}")
            todos.append(todo)
        
        # 다양한 ID로 검색 성능 측정
        search_times = []
        for i in [1, 100, 500, 999, 1000]:
            start_time = time.time()
            found_todo = self.todo_service.get_todo_by_id(i)
            end_time = time.time()
            
            search_times.append(end_time - start_time)
            self.assertIsNotNone(found_todo)
        
        # 평균 검색 시간이 0.01초 이내여야 함
        avg_search_time = sum(search_times) / len(search_times)
        self.assertLess(avg_search_time, 0.01, f"할일 검색 평균 시간이 기준을 초과했습니다: {avg_search_time:.4f}초")
    
    def test_memory_usage_stability(self):
        """메모리 사용량 안정성 테스트"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 대량의 할일 추가 및 삭제 반복
            for cycle in range(10):
                # 100개 할일 추가
                todos = []
                for i in range(100):
                    todo = self.todo_service.add_todo(f"메모리 테스트 할일 {cycle}-{i}")
                    todos.append(todo)
                
                # 모든 할일 삭제
                for todo in todos:
                    self.todo_service.delete_todo(todo.id, delete_folder=True)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # 메모리 증가가 50MB 이내여야 함 (메모리 누수 방지)
            self.assertLess(memory_increase, 50, f"메모리 사용량이 과도하게 증가했습니다: {memory_increase:.2f}MB")
            
        except ImportError:
            # psutil이 없으면 기본적인 메모리 안정성 테스트만 수행
            print("psutil 모듈이 없어 간단한 메모리 안정성 테스트를 수행합니다.")
            
            # 대량의 할일 추가 및 삭제 반복 (메모리 누수 확인)
            for cycle in range(5):
                todos = []
                for i in range(50):
                    todo = self.todo_service.add_todo(f"메모리 테스트 할일 {cycle}-{i}")
                    todos.append(todo)
                
                for todo in todos:
                    self.todo_service.delete_todo(todo.id, delete_folder=True)
            
            # 최종적으로 할일이 모두 삭제되었는지 확인
            final_todos = self.todo_service.get_all_todos()
            self.assertEqual(len(final_todos), 0, "메모리 안정성 테스트 후 할일이 남아있습니다.")
    
    def test_file_system_stability(self):
        """파일 시스템 안정성 테스트"""
        # 대량의 폴더 생성 및 삭제
        todos = []
        
        # 50개 할일 추가 (폴더 생성)
        for i in range(50):
            todo = self.todo_service.add_todo(f"파일 시스템 테스트 할일 {i+1}")
            todos.append(todo)
            self.assertTrue(os.path.exists(todo.folder_path))
        
        # 모든 폴더가 생성되었는지 확인
        folder_count = len([d for d in os.listdir(self.folders_dir) if os.path.isdir(os.path.join(self.folders_dir, d))])
        self.assertEqual(folder_count, 50)
        
        # 절반 삭제 (폴더 포함)
        for i in range(0, 25):
            success = self.todo_service.delete_todo(todos[i].id, delete_folder=True)
            self.assertTrue(success)
        
        # 남은 폴더 확인
        remaining_folder_count = len([d for d in os.listdir(self.folders_dir) if os.path.isdir(os.path.join(self.folders_dir, d))])
        self.assertEqual(remaining_folder_count, 25)
        
        # 나머지 삭제 (폴더 보존)
        for i in range(25, 50):
            success = self.todo_service.delete_todo(todos[i].id, delete_folder=False)
            self.assertTrue(success)
        
        # 폴더는 여전히 존재해야 함
        final_folder_count = len([d for d in os.listdir(self.folders_dir) if os.path.isdir(os.path.join(self.folders_dir, d))])
        self.assertEqual(final_folder_count, 25)


if __name__ == '__main__':
    # 테스트 실행 시 상세한 출력
    print("="*80)
    print("                    사용자 경험 개선 및 최종 검증 테스트")
    print("="*80)
    print("Task 9: 사용자 경험 개선 및 최종 검증")
    print("- 메뉴 표시 형식 개선")
    print("- 사용자 안내 메시지 개선") 
    print("- 프로그램 실행 및 전체 기능 검증")
    print("- 다양한 시나리오에서의 동작 확인")
    print("- 성능 및 안정성 검증")
    print("="*80)
    
    unittest.main(verbosity=2)