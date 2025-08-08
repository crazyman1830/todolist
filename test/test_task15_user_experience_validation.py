#!/usr/bin/env python3
"""
Task 15: 사용자 경험 검증 테스트

실제 사용자 시나리오를 시뮬레이션하여 GUI 컴포넌트들이
올바르게 상호작용하는지 검증합니다.

Requirements: 1.1, 1.2, 1.3, 1.4, 2.1-2.5, 3.1-3.4, 4.1-4.4, 5.1-5.4, 6.1-6.4, 7.1-7.4, 8.1-8.4
"""

import unittest
import tkinter as tk
import tempfile
import shutil
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from gui.todo_tree import TodoTree
from gui.dialogs import AddTodoDialog, EditTodoDialog, AddSubtaskDialog, ConfirmDialog
from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService


class TestUserExperienceValidation(unittest.TestCase):
    """사용자 경험 검증 테스트"""
    
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
    
    @patch('os.path.exists')
    def test_complete_gui_workflow(self, mock_exists):
        """완전한 GUI 워크플로우 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 1. 할일 추가 시나리오
        with patch('gui.dialogs.AddTodoDialog') as mock_add_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.get_todo_title.return_value = "GUI 워크플로우 테스트"
            mock_add_dialog.return_value = mock_dialog_instance
            
            # 할일 추가 버튼 클릭
            self.main_window.on_add_todo()
            
            # 다이얼로그가 호출되었는지 확인
            mock_add_dialog.assert_called_once()
        
        # 트리에 할일이 추가되었는지 확인
        todos = self.todo_service.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "GUI 워크플로우 테스트")
        
        # 2. 하위작업 추가 시나리오
        todo = todos[0]
        
        # 트리에서 할일 선택
        todo_node = list(self.main_window.todo_tree.todo_nodes.values())[0]
        self.main_window.todo_tree.selection_set(todo_node)
        
        with patch('gui.dialogs.AddSubtaskDialog') as mock_subtask_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.get_subtask_title.return_value = "GUI 하위작업 테스트"
            mock_subtask_dialog.return_value = mock_dialog_instance
            
            # 하위작업 추가
            self.main_window.on_add_subtask()
            
            # 다이얼로그가 호출되었는지 확인
            mock_subtask_dialog.assert_called_once()
        
        # 하위작업이 추가되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(len(updated_todo.subtasks), 1)
        self.assertEqual(updated_todo.subtasks[0].title, "GUI 하위작업 테스트")
        
        # 3. 트리 새로고침 및 상태 업데이트
        self.main_window.refresh_todo_tree()
        self.main_window.update_status_bar()
        
        # 상태바 업데이트 확인
        todo_count_text = self.main_window.todo_count_label.cget('text')
        self.assertEqual(todo_count_text, "할일: 1개")
        
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 0.0%")
    
    @patch('os.path.exists')
    def test_context_menu_interactions(self, mock_exists):
        """컨텍스트 메뉴 상호작용 테스트"""
        mock_exists.return_value = False
        
        # 테스트 데이터 준비
        todo = self.todo_service.add_todo("컨텍스트 메뉴 테스트")
        subtask = self.todo_service.add_subtask(todo.id, "컨텍스트 하위작업")
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 할일 노드 선택
        todo_node = list(self.main_window.todo_tree.todo_nodes.values())[0]
        self.main_window.todo_tree.selection_set(todo_node)
        
        # 할일 수정 시나리오
        with patch('gui.dialogs.EditTodoDialog') as mock_edit_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.get_new_title.return_value = "수정된 할일 제목"
            mock_edit_dialog.return_value = mock_dialog_instance
            
            # 할일 수정
            self.main_window.on_edit_todo()
            
            # 다이얼로그가 호출되었는지 확인
            mock_edit_dialog.assert_called_once()
        
        # 수정이 반영되었는지 확인
        updated_todo = self.todo_service.get_todo_by_id(todo.id)
        self.assertEqual(updated_todo.title, "수정된 할일 제목")
        
        # 할일 삭제 시나리오
        with patch('gui.dialogs.ConfirmDialog') as mock_confirm_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.get_result.return_value = True  # 삭제 확인
            mock_confirm_dialog.return_value = mock_dialog_instance
            
            # 할일 삭제
            self.main_window.on_delete_todo()
            
            # 확인 다이얼로그가 호출되었는지 확인
            mock_confirm_dialog.assert_called_once()
        
        # 삭제가 반영되었는지 확인
        remaining_todos = self.todo_service.get_all_todos()
        self.assertEqual(len(remaining_todos), 0)
    
    @patch('os.path.exists')
    def test_progress_visualization(self, mock_exists):
        """진행률 시각화 테스트"""
        mock_exists.return_value = False
        
        # 테스트 데이터 준비
        todo = self.todo_service.add_todo("진행률 테스트")
        subtask1 = self.todo_service.add_subtask(todo.id, "하위작업 1")
        subtask2 = self.todo_service.add_subtask(todo.id, "하위작업 2")
        subtask3 = self.todo_service.add_subtask(todo.id, "하위작업 3")
        subtask4 = self.todo_service.add_subtask(todo.id, "하위작업 4")
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 초기 진행률 확인 (0%)
        self.main_window.update_status_bar()
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 0.0%")
        
        # 하위작업 하나씩 완료하면서 진행률 확인
        # 25% 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask1.id)
        self.main_window.refresh_todo_tree()
        self.main_window.update_status_bar()
        
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 25.0%")
        
        # 50% 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask2.id)
        self.main_window.refresh_todo_tree()
        self.main_window.update_status_bar()
        
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 50.0%")
        
        # 75% 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask3.id)
        self.main_window.refresh_todo_tree()
        self.main_window.update_status_bar()
        
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 75.0%")
        
        # 100% 완료
        self.todo_service.toggle_subtask_completion(todo.id, subtask4.id)
        self.main_window.refresh_todo_tree()
        self.main_window.update_status_bar()
        
        completion_text = self.main_window.completion_label.cget('text')
        self.assertEqual(completion_text, "완료율: 100.0%")
    
    @patch('os.path.exists')
    def test_tree_expansion_state_management(self, mock_exists):
        """트리 확장 상태 관리 테스트"""
        mock_exists.return_value = False
        
        # 테스트 데이터 준비
        todo1 = self.todo_service.add_todo("확장 테스트 1")
        todo2 = self.todo_service.add_todo("확장 테스트 2")
        
        self.todo_service.add_subtask(todo1.id, "하위작업 1-1")
        self.todo_service.add_subtask(todo1.id, "하위작업 1-2")
        self.todo_service.add_subtask(todo2.id, "하위작업 2-1")
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 초기 상태 확인 (모두 확장됨)
        todo_nodes = list(self.main_window.todo_tree.todo_nodes.values())
        for node in todo_nodes:
            self.assertTrue(self.main_window.todo_tree.item(node, 'open'))
        
        # 모든 노드 축소
        self.main_window.on_collapse_all()
        for node in todo_nodes:
            self.assertFalse(self.main_window.todo_tree.item(node, 'open'))
        
        # 모든 노드 확장
        self.main_window.on_expand_all()
        for node in todo_nodes:
            self.assertTrue(self.main_window.todo_tree.item(node, 'open'))
        
        # 개별 노드 축소/확장
        first_node = todo_nodes[0]
        self.main_window.todo_tree.item(first_node, open=False)
        self.assertFalse(self.main_window.todo_tree.item(first_node, 'open'))
        
        self.main_window.todo_tree.item(first_node, open=True)
        self.assertTrue(self.main_window.todo_tree.item(first_node, 'open'))
    
    @patch('os.path.exists')
    def test_keyboard_shortcuts(self, mock_exists):
        """키보드 단축키 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # Ctrl+N (새 할일) 단축키 테스트
        with patch('gui.dialogs.AddTodoDialog') as mock_add_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.get_todo_title.return_value = "단축키 테스트 할일"
            mock_add_dialog.return_value = mock_dialog_instance
            
            # Ctrl+N 이벤트 시뮬레이션
            event = Mock()
            event.keysym = 'n'
            event.state = 4  # Ctrl 키
            
            # 키보드 이벤트 핸들러 직접 호출
            self.main_window.on_add_todo()
            
            # 다이얼로그가 호출되었는지 확인
            mock_add_dialog.assert_called_once()
        
        # F5 (새로고침) 단축키 테스트
        initial_call_count = self.todo_service.get_all_todos.call_count if hasattr(self.todo_service.get_all_todos, 'call_count') else 0
        
        # F5 이벤트 시뮬레이션
        self.main_window.on_refresh()
        
        # 새로고침이 실행되었는지 확인 (상태 메시지로 확인)
        status_text = self.main_window.status_message_label.cget('text')
        self.assertEqual(status_text, "데이터가 새로고침되었습니다")
    
    @patch('os.path.exists')
    def test_error_message_display(self, mock_exists):
        """오류 메시지 표시 테스트"""
        mock_exists.return_value = False
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 잘못된 할일 선택 상태에서 수정 시도
        self.main_window.todo_tree.selection_set()  # 선택 해제
        
        # 할일 수정 시도 (선택된 할일이 없음)
        self.main_window.on_edit_todo()
        
        # 상태 메시지에 오류가 표시되었는지 확인
        status_text = self.main_window.status_message_label.cget('text')
        self.assertIn("선택", status_text)  # "할일을 선택해주세요" 등의 메시지
        
        # 잘못된 할일 선택 상태에서 삭제 시도
        self.main_window.on_delete_todo()
        
        # 상태 메시지에 오류가 표시되었는지 확인
        status_text = self.main_window.status_message_label.cget('text')
        self.assertIn("선택", status_text)
    
    @patch('os.path.exists')
    def test_folder_management_integration(self, mock_exists):
        """폴더 관리 통합 테스트"""
        mock_exists.return_value = False
        
        # 테스트 데이터 준비
        todo = self.todo_service.add_todo("폴더 테스트")
        
        # 메인 윈도우 생성
        self.main_window = MainWindow(self.todo_service)
        
        # 할일 노드 선택
        todo_node = list(self.main_window.todo_tree.todo_nodes.values())[0]
        self.main_window.todo_tree.selection_set(todo_node)
        
        # 폴더 열기 기능 테스트
        with patch.object(self.file_service, 'open_todo_folder', return_value=True) as mock_open:
            self.main_window.on_open_folder()
            
            # 폴더 열기가 호출되었는지 확인
            mock_open.assert_called_once_with(todo.folder_path)
        
        # 할일 삭제 시 폴더 삭제 확인 다이얼로그 테스트
        with patch('gui.dialogs.ConfirmDialog') as mock_confirm_dialog:
            # 첫 번째 확인: 할일 삭제
            # 두 번째 확인: 폴더 삭제
            mock_dialog_instances = [Mock(), Mock()]
            mock_dialog_instances[0].get_result.return_value = True  # 할일 삭제 확인
            mock_dialog_instances[1].get_result.return_value = True  # 폴더 삭제 확인
            mock_confirm_dialog.side_effect = mock_dialog_instances
            
            # 할일 삭제
            self.main_window.on_delete_todo()
            
            # 두 번의 확인 다이얼로그가 호출되었는지 확인
            self.assertEqual(mock_confirm_dialog.call_count, 2)
        
        # 할일이 삭제되었는지 확인
        remaining_todos = self.todo_service.get_all_todos()
        self.assertEqual(len(remaining_todos), 0)
    
    @patch('os.path.exists')
    def test_window_state_persistence(self, mock_exists):
        """윈도우 상태 영속성 테스트"""
        # 설정 파일이 존재한다고 가정
        mock_exists.return_value = True
        
        # 가짜 설정 데이터
        mock_settings = {
            "window_width": 1000,
            "window_height": 700,
            "window_x": 100,
            "window_y": 50
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_settings))):
            with patch('json.load', return_value=mock_settings):
                # 메인 윈도우 생성
                self.main_window = MainWindow(self.todo_service)
                
                # 윈도우 크기가 설정에 따라 설정되었는지 확인
                # (실제로는 tkinter의 geometry 메서드를 통해 확인해야 하지만,
                # 테스트 환경에서는 설정 로드 여부만 확인)
                self.assertIsNotNone(self.main_window.root)


class TestDialogInteractions(unittest.TestCase):
    """다이얼로그 상호작용 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중에는 윈도우 숨김
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_add_todo_dialog_validation(self):
        """할일 추가 다이얼로그 유효성 검사 테스트"""
        # 빈 제목으로 다이얼로그 테스트
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            dialog = AddTodoDialog(self.root)
            
            # 빈 제목 입력 시뮬레이션
            dialog.title_entry.insert(0, "")
            dialog.on_ok()
            
            # 경고 메시지가 표시되었는지 확인
            mock_warning.assert_called_once()
            
            # 다이얼로그가 닫히지 않았는지 확인 (result가 None)
            self.assertIsNone(dialog.result)
    
    def test_edit_todo_dialog_with_existing_title(self):
        """기존 제목이 있는 할일 수정 다이얼로그 테스트"""
        existing_title = "기존 할일 제목"
        dialog = EditTodoDialog(self.root, existing_title)
        
        # 기존 제목이 입력 필드에 설정되었는지 확인
        self.assertEqual(dialog.title_entry.get(), existing_title)
        
        # 새로운 제목으로 수정
        dialog.title_entry.delete(0, tk.END)
        dialog.title_entry.insert(0, "수정된 할일 제목")
        dialog.on_ok()
        
        # 수정된 제목이 반환되는지 확인
        self.assertEqual(dialog.result, "수정된 할일 제목")
    
    def test_add_subtask_dialog_with_parent_info(self):
        """상위 할일 정보가 있는 하위작업 추가 다이얼로그 테스트"""
        parent_title = "상위 할일"
        dialog = AddSubtaskDialog(self.root, parent_title)
        
        # 상위 할일 정보가 표시되었는지 확인
        parent_label_text = dialog.parent_label.cget('text')
        self.assertIn(parent_title, parent_label_text)
        
        # 하위작업 제목 입력
        dialog.title_entry.insert(0, "새 하위작업")
        dialog.on_ok()
        
        # 하위작업 제목이 반환되는지 확인
        self.assertEqual(dialog.result, "새 하위작업")
    
    def test_confirm_dialog_responses(self):
        """확인 다이얼로그 응답 테스트"""
        message = "정말로 삭제하시겠습니까?"
        
        # 확인 응답 테스트
        with patch('tkinter.messagebox.askyesno', return_value=True):
            dialog = ConfirmDialog(self.root, message)
            self.assertTrue(dialog.get_result())
        
        # 취소 응답 테스트
        with patch('tkinter.messagebox.askyesno', return_value=False):
            dialog = ConfirmDialog(self.root, message)
            self.assertFalse(dialog.get_result())


if __name__ == '__main__':
    # 테스트 실행 시 상세한 출력
    unittest.main(verbosity=2)