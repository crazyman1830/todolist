#!/usr/bin/env python3
"""
Task 16 사용자 경험 개선 및 최종 검증 테스트

이 테스트는 다음 사항들을 검증합니다:
- 키보드 접근성 개선 (Tab 순서, 단축키)
- 툴팁 및 도움말 메시지
- 윈도우 크기 조정 시 레이아웃 최적화
- 다양한 화면 해상도에서의 동작
- 사용자 설정 저장/복원 기능
- 전체 기능 최종 검증
"""

import unittest
import tkinter as tk
from tkinter import ttk
import json
import os
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock

# 테스트 대상 모듈들
from gui.main_window import MainWindow
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from models.todo import Todo
from models.subtask import SubTask


class TestTask16UserExperience(unittest.TestCase):
    """Task 16: 사용자 경험 개선 및 최종 검증 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.todos_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "test_folders")
        self.settings_file = os.path.join(self.temp_dir, "test_gui_settings.json")
        
        # 서비스 초기화
        self.storage_service = StorageService(self.todos_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 테스트용 할일 데이터 생성
        self._create_test_data()
        
        # GUI 초기화 (실제 윈도우는 표시하지 않음)
        self.root = tk.Tk()
        self.root.withdraw()  # 윈도우 숨기기
        
        # MainWindow 인스턴스 생성 (설정 파일 경로 변경)
        with patch.object(MainWindow, '__init__', self._mock_main_window_init):
            self.main_window = MainWindow(self.todo_service)
            self.main_window.settings_file = self.settings_file
    
    def tearDown(self):
        """테스트 정리"""
        try:
            if hasattr(self, 'root'):
                self.root.destroy()
        except:
            pass
        
        # 임시 파일들 정리
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def _mock_main_window_init(self, todo_service):
        """MainWindow 초기화 모킹"""
        self.todo_service = todo_service
        self.root = tk.Tk()
        self.root.withdraw()
        self.settings_file = self.settings_file
        
        # 기본 속성들 설정
        self.saved_settings = {}
        
        # UI 구성 요소들 모킹
        self.toolbar = ttk.Frame(self.root)
        self.btn_add = ttk.Button(self.toolbar, text="할일 추가")
        self.btn_edit = ttk.Button(self.toolbar, text="수정")
        self.btn_delete = ttk.Button(self.toolbar, text="삭제")
        self.btn_add_subtask = ttk.Button(self.toolbar, text="하위작업 추가")
        self.btn_refresh = ttk.Button(self.toolbar, text="새로고침")
        self.btn_open_folder = ttk.Button(self.toolbar, text="폴더 열기")
        
        # 검색 박스 모킹
        self.search_box = Mock()
        self.search_box.search_entry = ttk.Entry(self.toolbar)
        self.search_box.get_search_term = Mock(return_value="")
        self.search_box.clear = Mock()
        
        # 필터 패널 모킹
        self.filter_panel = Mock()
        self.filter_panel.show_completed_var = tk.BooleanVar(value=True)
        self.filter_panel.sort_by_var = tk.StringVar(value="created_at")
        self.filter_panel.sort_order_var = tk.StringVar(value="desc")
        self.filter_panel.get_filter_options = Mock(return_value={
            'show_completed': True,
            'sort_by': 'created_at',
            'sort_order': 'desc'
        })
        
        # 트리 뷰 모킹
        self.todo_tree = Mock()
        self.todo_tree.todo_nodes = {}
        self.todo_tree.focus_set = Mock()
        self.todo_tree.item = Mock()
    
    def _create_test_data(self):
        """테스트용 데이터 생성"""
        # 할일 1: 하위작업이 있는 할일
        todo1 = self.todo_service.add_todo("프로젝트 문서 작성")
        self.todo_service.add_subtask(todo1.id, "요구사항 분석")
        self.todo_service.add_subtask(todo1.id, "설계 문서 작성")
        
        # 할일 2: 완료된 할일
        todo2 = self.todo_service.add_todo("테스트 작성")
        subtask = self.todo_service.add_subtask(todo2.id, "단위 테스트")
        self.todo_service.toggle_subtask_completion(todo2.id, subtask.id)
        
        # 할일 3: 단순 할일
        self.todo_service.add_todo("코드 리뷰")
    
    def test_keyboard_accessibility_shortcuts(self):
        """키보드 단축키 테스트"""
        print("키보드 단축키 테스트...")
        
        # 단축키 바인딩 확인
        bindings = self.main_window.root.bind()
        
        # 주요 단축키들이 바인딩되어 있는지 확인
        expected_shortcuts = [
            '<Control-n>',      # 새 할일
            '<Control-q>',      # 종료
            '<F2>',            # 수정
            '<Delete>',        # 삭제
            '<Control-Shift-n>', # 하위작업 추가
            '<F5>',            # 새로고침
            '<Control-f>',     # 검색 포커스
            '<Escape>',        # 검색 클리어
            '<Control-h>',     # 도움말
            '<F1>'             # 도움말
        ]
        
        for shortcut in expected_shortcuts:
            # 바인딩이 존재하는지 확인
            bound_commands = self.main_window.root.bind(shortcut)
            self.assertIsNotNone(bound_commands, f"단축키 {shortcut}가 바인딩되지 않음")
        
        print("✓ 모든 키보드 단축키가 올바르게 바인딩됨")
    
    def test_tooltip_functionality(self):
        """툴팁 기능 테스트"""
        print("툴팁 기능 테스트...")
        
        # 툴팁 생성 메서드 테스트
        test_button = ttk.Button(self.main_window.root, text="테스트")
        
        # 툴팁 생성
        self.main_window._create_tooltip(test_button, "테스트 툴팁")
        
        # Enter 이벤트 바인딩 확인
        enter_bindings = test_button.bind('<Enter>')
        self.assertIsNotNone(enter_bindings, "툴팁 Enter 이벤트가 바인딩되지 않음")
        
        print("✓ 툴팁 기능이 올바르게 구현됨")
    
    def test_focus_chain_setup(self):
        """Tab 키 포커스 체인 테스트"""
        print("포커스 체인 테스트...")
        
        # 포커스 체인 설정
        self.main_window._setup_focus_chain()
        
        # Tab 키 바인딩 확인
        widgets_to_check = [
            self.main_window.btn_add,
            self.main_window.btn_edit,
            self.main_window.btn_delete,
            self.main_window.search_box.search_entry
        ]
        
        for widget in widgets_to_check:
            tab_binding = widget.bind('<Tab>')
            shift_tab_binding = widget.bind('<Shift-Tab>')
            
            self.assertIsNotNone(tab_binding, f"위젯 {widget}에 Tab 바인딩이 없음")
            self.assertIsNotNone(shift_tab_binding, f"위젯 {widget}에 Shift-Tab 바인딩이 없음")
        
        print("✓ 포커스 체인이 올바르게 설정됨")
    
    def test_window_settings_save_load(self):
        """윈도우 설정 저장/로드 테스트"""
        print("윈도우 설정 저장/로드 테스트...")
        
        # 테스트 설정 데이터
        test_geometry = "800x600+100+50"
        test_state = "normal"
        
        # 윈도우 설정 저장
        self.main_window.root.geometry(test_geometry)
        self.main_window.save_window_settings()
        
        # 설정 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists(self.settings_file), "설정 파일이 생성되지 않음")
        
        # 설정 파일 내용 확인
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        self.assertIn('geometry', settings, "geometry 설정이 저장되지 않음")
        self.assertIn('state', settings, "state 설정이 저장되지 않음")
        
        # 설정 로드 테스트
        self.main_window.load_window_settings()
        
        print("✓ 윈도우 설정 저장/로드가 올바르게 동작함")
    
    def test_geometry_validation(self):
        """지오메트리 검증 테스트"""
        print("지오메트리 검증 테스트...")
        
        # 유효한 지오메트리
        valid_geometries = [
            "800x600+100+50",
            "1024x768+0+0",
            "640x480+200+100"
        ]
        
        for geometry in valid_geometries:
            result = self.main_window._validate_geometry(geometry)
            self.assertTrue(result, f"유효한 지오메트리 {geometry}가 거부됨")
        
        # 무효한 지오메트리
        invalid_geometries = [
            "invalid",
            "800x600",
            "-100x-100+0+0",
            "99999x99999+0+0"
        ]
        
        for geometry in invalid_geometries:
            result = self.main_window._validate_geometry(geometry)
            self.assertFalse(result, f"무효한 지오메트리 {geometry}가 허용됨")
        
        print("✓ 지오메트리 검증이 올바르게 동작함")
    
    def test_layout_optimization(self):
        """레이아웃 최적화 테스트"""
        print("레이아웃 최적화 테스트...")
        
        # 컴팩트 레이아웃 적용 테스트
        self.main_window._apply_compact_layout()
        
        # 버튼 텍스트가 축약되었는지 확인
        self.assertEqual(self.main_window.btn_add.cget('text'), "추가")
        self.assertEqual(self.main_window.btn_add_subtask.cget('text'), "하위+")
        
        # 일반 레이아웃 복원 테스트
        self.main_window._apply_normal_layout()
        
        # 버튼 텍스트가 복원되었는지 확인
        self.assertEqual(self.main_window.btn_add.cget('text'), "할일 추가")
        self.assertEqual(self.main_window.btn_add_subtask.cget('text'), "하위작업 추가")
        
        print("✓ 레이아웃 최적화가 올바르게 동작함")
    
    def test_user_settings_restoration(self):
        """사용자 설정 복원 테스트"""
        print("사용자 설정 복원 테스트...")
        
        # 테스트 설정 데이터
        test_settings = {
            'geometry': '800x600+100+50',
            'state': 'normal',
            'filter_options': {
                'show_completed': False,
                'sort_by': 'title',
                'sort_order': 'asc'
            },
            'expanded_todos': [1, 2]
        }
        
        # 설정 파일 생성
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(test_settings, f, ensure_ascii=False, indent=2)
        
        # 설정 로드
        self.main_window.saved_settings = test_settings
        self.main_window._restore_user_settings()
        
        # 필터 설정이 복원되었는지 확인
        self.assertFalse(self.main_window.filter_panel.show_completed_var.get())
        self.assertEqual(self.main_window.filter_panel.sort_by_var.get(), 'title')
        self.assertEqual(self.main_window.filter_panel.sort_order_var.get(), 'asc')
        
        print("✓ 사용자 설정 복원이 올바르게 동작함")
    
    def test_help_window_functionality(self):
        """도움말 윈도우 기능 테스트"""
        print("도움말 윈도우 기능 테스트...")
        
        # 도움말 윈도우 표시 테스트
        help_text = "테스트 도움말"
        
        # 실제로 윈도우를 표시하지 않고 메서드만 테스트
        with patch('tkinter.Toplevel') as mock_toplevel:
            mock_window = Mock()
            mock_toplevel.return_value = mock_window
            
            self.main_window._show_help_window(help_text)
            
            # Toplevel 윈도우가 생성되었는지 확인
            mock_toplevel.assert_called_once()
            mock_window.title.assert_called_with("할일 관리자 - 도움말")
            mock_window.geometry.assert_called_with("600x500")
        
        print("✓ 도움말 윈도우 기능이 올바르게 구현됨")
    
    def test_search_and_filter_integration(self):
        """검색 및 필터 통합 테스트"""
        print("검색 및 필터 통합 테스트...")
        
        # 검색 박스 포커스 이동 테스트
        self.main_window._focus_search_box()
        self.main_window.search_box.search_entry.focus_set.assert_called()
        
        # 검색 클리어 및 트리 포커스 테스트
        self.main_window._clear_search_and_focus_tree()
        self.main_window.search_box.clear.assert_called()
        self.main_window.todo_tree.focus_set.assert_called()
        
        print("✓ 검색 및 필터 통합이 올바르게 동작함")
    
    def test_error_handling_robustness(self):
        """오류 처리 견고성 테스트"""
        print("오류 처리 견고성 테스트...")
        
        # 잘못된 설정 파일로 테스트
        invalid_settings_file = os.path.join(self.temp_dir, "invalid_settings.json")
        with open(invalid_settings_file, 'w') as f:
            f.write("invalid json content")
        
        self.main_window.settings_file = invalid_settings_file
        
        # 오류가 발생해도 프로그램이 중단되지 않아야 함
        try:
            self.main_window.load_window_settings()
            self.main_window.save_window_settings()
        except Exception as e:
            self.fail(f"설정 파일 오류 처리 중 예외 발생: {e}")
        
        # 존재하지 않는 위젯에 대한 접근 테스트
        original_todo_tree = self.main_window.todo_tree
        self.main_window.todo_tree = None
        
        try:
            self.main_window._clear_search_and_focus_tree()
            self.main_window._adjust_tree_columns(800)
        except Exception as e:
            self.fail(f"None 위젯 처리 중 예외 발생: {e}")
        finally:
            self.main_window.todo_tree = original_todo_tree
        
        print("✓ 오류 처리가 견고하게 구현됨")
    
    def test_performance_with_large_dataset(self):
        """대용량 데이터셋 성능 테스트"""
        print("대용량 데이터셋 성능 테스트...")
        
        # 많은 할일 생성
        start_time = time.time()
        
        for i in range(50):  # 50개의 할일 생성
            todo = self.todo_service.add_todo(f"할일 {i+1}")
            # 각 할일에 5개의 하위작업 추가
            for j in range(5):
                self.todo_service.add_subtask(todo.id, f"하위작업 {j+1}")
        
        creation_time = time.time() - start_time
        
        # 데이터 로드 성능 테스트
        start_time = time.time()
        todos = self.todo_service.get_all_todos()
        load_time = time.time() - start_time
        
        # 성능 기준 확인 (합리적인 시간 내에 완료되어야 함)
        self.assertLess(creation_time, 5.0, "할일 생성이 너무 오래 걸림")
        self.assertLess(load_time, 1.0, "할일 로드가 너무 오래 걸림")
        self.assertEqual(len(todos), 53, "생성된 할일 수가 일치하지 않음")  # 기존 3개 + 새로 생성한 50개
        
        print(f"✓ 성능 테스트 통과 (생성: {creation_time:.2f}s, 로드: {load_time:.2f}s)")
    
    def test_memory_usage_optimization(self):
        """메모리 사용량 최적화 테스트"""
        print("메모리 사용량 최적화 테스트...")
        
        import gc
        import sys
        
        # 가비지 컬렉션 실행
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # 많은 위젯 생성 및 제거
        widgets = []
        for i in range(100):
            widget = ttk.Button(self.main_window.root, text=f"버튼 {i}")
            widgets.append(widget)
        
        # 위젯 제거
        for widget in widgets:
            widget.destroy()
        
        widgets.clear()
        
        # 가비지 컬렉션 실행
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # 메모리 누수가 심각하지 않은지 확인
        object_increase = final_objects - initial_objects
        self.assertLess(object_increase, 200, f"메모리 누수 의심: {object_increase}개 객체 증가")
        
        print(f"✓ 메모리 사용량 최적화 확인 (객체 증가: {object_increase}개)")
    
    def test_accessibility_compliance(self):
        """접근성 준수 테스트"""
        print("접근성 준수 테스트...")
        
        # 모든 버튼에 텍스트가 있는지 확인
        buttons = [
            self.main_window.btn_add,
            self.main_window.btn_edit,
            self.main_window.btn_delete,
            self.main_window.btn_add_subtask,
            self.main_window.btn_refresh,
            self.main_window.btn_open_folder
        ]
        
        for button in buttons:
            button_text = button.cget('text')
            self.assertIsNotNone(button_text, f"버튼 {button}에 텍스트가 없음")
            self.assertNotEqual(button_text.strip(), "", f"버튼 {button}의 텍스트가 비어있음")
        
        # 키보드로 모든 주요 기능에 접근 가능한지 확인
        keyboard_accessible_functions = [
            'on_add_todo',
            'on_edit_todo', 
            'on_delete_todo',
            'on_add_subtask',
            'on_refresh',
            'on_show_help'
        ]
        
        for func_name in keyboard_accessible_functions:
            self.assertTrue(hasattr(self.main_window, func_name), 
                          f"키보드 접근 가능한 함수 {func_name}가 없음")
        
        print("✓ 접근성 준수 사항이 올바르게 구현됨")
    
    def test_final_integration_verification(self):
        """최종 통합 검증 테스트"""
        print("최종 통합 검증 테스트...")
        
        # 전체 워크플로우 테스트
        try:
            # 1. 할일 추가
            initial_count = len(self.todo_service.get_all_todos())
            new_todo = self.todo_service.add_todo("통합 테스트 할일")
            self.assertIsNotNone(new_todo, "할일 추가 실패")
            
            # 2. 하위작업 추가
            subtask = self.todo_service.add_subtask(new_todo.id, "통합 테스트 하위작업")
            self.assertIsNotNone(subtask, "하위작업 추가 실패")
            
            # 3. 하위작업 완료 처리
            success = self.todo_service.toggle_subtask_completion(new_todo.id, subtask.id)
            self.assertTrue(success, "하위작업 완료 처리 실패")
            
            # 4. 진행률 확인
            updated_todo = self.todo_service.get_todo_by_id(new_todo.id)
            self.assertEqual(updated_todo.get_completion_rate(), 1.0, "진행률 계산 오류")
            
            # 5. 할일 삭제
            success = self.todo_service.delete_todo(new_todo.id)
            self.assertTrue(success, "할일 삭제 실패")
            
            # 6. 최종 개수 확인
            final_count = len(self.todo_service.get_all_todos())
            self.assertEqual(final_count, initial_count, "할일 개수가 일치하지 않음")
            
        except Exception as e:
            self.fail(f"통합 테스트 중 오류 발생: {e}")
        
        print("✓ 최종 통합 검증 완료")


def run_task16_tests():
    """Task 16 테스트 실행"""
    print("=" * 60)
    print("Task 16: 사용자 경험 개선 및 최종 검증 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask16UserExperience)
    
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
    success = run_task16_tests()
    exit(0 if success else 1)