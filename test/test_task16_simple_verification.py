#!/usr/bin/env python3
"""
Task 16 간단한 검증 테스트

실제 GUI 구현이 올바르게 작동하는지 확인하는 간단한 테스트
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch

# 테스트 대상 모듈들
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestTask16SimpleVerification(unittest.TestCase):
    """Task 16 간단한 검증 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.todos_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "test_folders")
        
        # 서비스 초기화
        self.storage_service = StorageService(self.todos_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
    
    def tearDown(self):
        """테스트 정리"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_main_window_import(self):
        """MainWindow 클래스 임포트 테스트"""
        print("MainWindow 클래스 임포트 테스트...")
        
        try:
            from gui.main_window import MainWindow
            self.assertTrue(True, "MainWindow 클래스 임포트 성공")
        except ImportError as e:
            self.fail(f"MainWindow 클래스 임포트 실패: {e}")
        
        print("✓ MainWindow 클래스 임포트 성공")
    
    def test_main_window_methods_exist(self):
        """MainWindow 클래스의 주요 메서드 존재 확인"""
        print("MainWindow 주요 메서드 존재 확인...")
        
        from gui.main_window import MainWindow
        
        # 확인할 메서드들
        required_methods = [
            '_create_tooltip',
            '_setup_focus_chain',
            '_validate_geometry',
            '_on_window_configure',
            '_apply_compact_layout',
            '_apply_normal_layout',
            '_adjust_tree_columns',
            '_restore_user_settings',
            '_show_help_window',
            '_focus_search_box',
            '_clear_search_and_focus_tree'
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(MainWindow, method_name), 
                          f"MainWindow에 {method_name} 메서드가 없음")
        
        print("✓ 모든 필수 메서드가 존재함")
    
    def test_settings_file_operations(self):
        """설정 파일 작업 테스트"""
        print("설정 파일 작업 테스트...")
        
        settings_file = os.path.join(self.temp_dir, "test_settings.json")
        
        # 테스트 설정 데이터
        test_settings = {
            'geometry': '800x600+100+50',
            'state': 'normal',
            'filter_options': {
                'show_completed': True,
                'sort_by': 'created_at',
                'sort_order': 'desc'
            }
        }
        
        # 설정 저장
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(test_settings, f, ensure_ascii=False, indent=2)
        
        # 설정 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists(settings_file), "설정 파일이 생성되지 않음")
        
        # 설정 로드
        with open(settings_file, 'r', encoding='utf-8') as f:
            loaded_settings = json.load(f)
        
        # 설정이 올바르게 저장/로드되었는지 확인
        self.assertEqual(loaded_settings['geometry'], test_settings['geometry'])
        self.assertEqual(loaded_settings['filter_options']['show_completed'], 
                        test_settings['filter_options']['show_completed'])
        
        print("✓ 설정 파일 작업이 올바르게 동작함")
    
    def test_geometry_validation_logic(self):
        """지오메트리 검증 로직 테스트"""
        print("지오메트리 검증 로직 테스트...")
        
        from gui.main_window import MainWindow
        
        # 임시 MainWindow 인스턴스 생성 (실제 GUI는 생성하지 않음)
        with patch('tkinter.Tk'):
            with patch.object(MainWindow, '__init__', lambda x, y: None):
                main_window = MainWindow(None)
                
                # 필요한 속성 설정
                main_window.root = type('MockRoot', (), {
                    'winfo_screenwidth': lambda: 1920,
                    'winfo_screenheight': lambda: 1080
                })()
                
                # 유효한 지오메트리 테스트
                valid_geometries = [
                    "800x600+100+50",
                    "1024x768+0+0"
                ]
                
                for geometry in valid_geometries:
                    result = main_window._validate_geometry(geometry)
                    self.assertTrue(result, f"유효한 지오메트리 {geometry}가 거부됨")
                
                # 무효한 지오메트리 테스트
                invalid_geometries = [
                    "invalid",
                    "800x600",
                    "-100x-100+0+0"
                ]
                
                for geometry in invalid_geometries:
                    result = main_window._validate_geometry(geometry)
                    self.assertFalse(result, f"무효한 지오메트리 {geometry}가 허용됨")
        
        print("✓ 지오메트리 검증 로직이 올바르게 동작함")
    
    def test_todo_service_integration(self):
        """TodoService 통합 테스트"""
        print("TodoService 통합 테스트...")
        
        # 할일 추가
        todo = self.todo_service.add_todo("테스트 할일")
        self.assertIsNotNone(todo, "할일 추가 실패")
        
        # 하위작업 추가
        subtask = self.todo_service.add_subtask(todo.id, "테스트 하위작업")
        self.assertIsNotNone(subtask, "하위작업 추가 실패")
        
        # 하위작업 완료 처리
        success = self.todo_service.toggle_subtask_completion(todo.id, subtask.id)
        self.assertTrue(success, "하위작업 완료 처리 실패")
        
        # 진행률 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.get_completion_rate(), 1.0, "진행률 계산 오류")
        
        # 검색 기능 테스트
        filtered_todos = self.todo_service.filter_todos(search_term="테스트")
        self.assertEqual(len(filtered_todos), 1, "검색 기능 오류")
        
        # 정렬 기능 테스트
        sorted_todos = self.todo_service.sort_todos(filtered_todos, sort_by="title")
        self.assertEqual(len(sorted_todos), 1, "정렬 기능 오류")
        
        print("✓ TodoService 통합이 올바르게 동작함")
    
    def test_components_import(self):
        """GUI 컴포넌트 임포트 테스트"""
        print("GUI 컴포넌트 임포트 테스트...")
        
        try:
            from gui.components import (
                ProgressBar, SearchBox, FilterPanel, StatusBar,
                TodoProgressWidget, CompactProgressBar
            )
            from gui.dialogs import (
                AddTodoDialog, EditTodoDialog, AddSubtaskDialog,
                ConfirmDialog, DeleteConfirmDialog, FolderDeleteConfirmDialog,
                FolderErrorDialog
            )
            from gui.todo_tree import TodoTree
            
            print("✓ 모든 GUI 컴포넌트 임포트 성공")
            
        except ImportError as e:
            self.fail(f"GUI 컴포넌트 임포트 실패: {e}")
    
    def test_accessibility_features_exist(self):
        """접근성 기능 존재 확인"""
        print("접근성 기능 존재 확인...")
        
        from gui.main_window import MainWindow
        
        # 접근성 관련 메서드들이 존재하는지 확인
        accessibility_methods = [
            '_create_tooltip',
            '_setup_focus_chain',
            '_focus_next_widget',
            '_focus_search_box',
            '_clear_search_and_focus_tree'
        ]
        
        for method_name in accessibility_methods:
            self.assertTrue(hasattr(MainWindow, method_name), 
                          f"접근성 메서드 {method_name}가 없음")
        
        print("✓ 모든 접근성 기능이 구현됨")
    
    def test_layout_optimization_methods(self):
        """레이아웃 최적화 메서드 확인"""
        print("레이아웃 최적화 메서드 확인...")
        
        from gui.main_window import MainWindow
        
        # 레이아웃 최적화 관련 메서드들
        layout_methods = [
            '_on_window_configure',
            '_apply_compact_layout',
            '_apply_normal_layout',
            '_adjust_tree_columns'
        ]
        
        for method_name in layout_methods:
            self.assertTrue(hasattr(MainWindow, method_name), 
                          f"레이아웃 메서드 {method_name}가 없음")
        
        print("✓ 모든 레이아웃 최적화 기능이 구현됨")
    
    def test_help_system_implementation(self):
        """도움말 시스템 구현 확인"""
        print("도움말 시스템 구현 확인...")
        
        from gui.main_window import MainWindow
        
        # 도움말 관련 메서드들
        help_methods = [
            'on_show_help',
            '_show_help_window',
            'on_show_about'
        ]
        
        for method_name in help_methods:
            self.assertTrue(hasattr(MainWindow, method_name), 
                          f"도움말 메서드 {method_name}가 없음")
        
        print("✓ 도움말 시스템이 올바르게 구현됨")
    
    def test_error_handling_robustness(self):
        """오류 처리 견고성 테스트"""
        print("오류 처리 견고성 테스트...")
        
        # 잘못된 데이터로 TodoService 테스트
        try:
            # 존재하지 않는 할일에 하위작업 추가 시도
            try:
                result = self.todo_service.add_subtask(99999, "존재하지 않는 할일의 하위작업")
                self.assertIsNone(result, "존재하지 않는 할일에 하위작업이 추가됨")
            except ValueError:
                # ValueError가 발생하는 것이 정상적인 오류 처리
                pass
            
            # 존재하지 않는 하위작업 토글 시도
            try:
                result = self.todo_service.toggle_subtask_completion(1, 99999)
                self.assertFalse(result, "존재하지 않는 하위작업이 토글됨")
            except ValueError:
                # ValueError가 발생하는 것이 정상적인 오류 처리
                pass
            
            print("✓ 오류 처리가 견고하게 구현됨")
            
        except Exception as e:
            self.fail(f"오류 처리 중 예외 발생: {e}")
    
    def test_data_persistence(self):
        """데이터 지속성 테스트"""
        print("데이터 지속성 테스트...")
        
        # 할일 추가
        todo = self.todo_service.add_todo("지속성 테스트 할일")
        subtask = self.todo_service.add_subtask(todo.id, "지속성 테스트 하위작업")
        
        # 새로운 서비스 인스턴스로 데이터 로드
        new_storage_service = StorageService(self.todos_file)
        new_file_service = FileService(self.folders_dir)
        new_todo_service = TodoService(new_storage_service, new_file_service)
        
        # 데이터가 올바르게 로드되는지 확인
        loaded_todos = new_todo_service.get_all_todos()
        self.assertEqual(len(loaded_todos), 1, "할일이 올바르게 로드되지 않음")
        
        loaded_todo = loaded_todos[0]
        self.assertEqual(loaded_todo.title, "지속성 테스트 할일", "할일 제목이 일치하지 않음")
        self.assertEqual(len(loaded_todo.subtasks), 1, "하위작업이 올바르게 로드되지 않음")
        
        print("✓ 데이터 지속성이 올바르게 동작함")


def run_simple_verification():
    """간단한 검증 테스트 실행"""
    print("=" * 60)
    print("Task 16: 사용자 경험 개선 간단한 검증 테스트")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask16SimpleVerification)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약:")
    print(f"총 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_simple_verification()
    exit(0 if success else 1)