#!/usr/bin/env python3
"""
할일 리스트 새로고침 통합 테스트
실제 사용 시나리오에서 중복 누적 문제가 해결되었는지 확인
"""

import unittest
import tkinter as tk
import tempfile
import os
import json
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storage_service import StorageService
from services.file_service import FileService
from services.todo_service import TodoService
from gui.main_window import MainWindow


class TestRefreshIntegration(unittest.TestCase):
    """새로고침 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.temp_dir, "todo_folders")
        
        # 테스트용 데이터 파일 생성
        test_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "테스트 할일 1",
                    "created_at": datetime.now().isoformat(),
                    "folder_path": "todo_1",
                    "subtasks": [],
                    "is_expanded": True
                },
                {
                    "id": 2,
                    "title": "테스트 할일 2",
                    "created_at": datetime.now().isoformat(),
                    "folder_path": "todo_2",
                    "subtasks": [
                        {
                            "id": 21,
                            "todo_id": 2,
                            "title": "하위작업 1",
                            "is_completed": False,
                            "created_at": datetime.now().isoformat()
                        }
                    ],
                    "is_expanded": True
                }
            ]
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file, auto_save_enabled=False)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # GUI 초기화 (숨김 모드)
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.main_window = MainWindow(self.todo_service)
        self.main_window.root.withdraw()
    
    def tearDown(self):
        """테스트 정리"""
        try:
            self.main_window.root.destroy()
            self.root.destroy()
        except:
            pass
        
        # 임시 파일 정리
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_refresh_no_duplication(self):
        """새로고침 시 중복이 발생하지 않는지 테스트"""
        # 초기 상태 확인
        initial_children = self.main_window.todo_tree.get_children()
        initial_count = len(initial_children)
        self.assertEqual(initial_count, 2)  # 테스트 데이터에 2개 할일
        
        # 첫 번째 새로고침
        self.main_window.on_refresh()
        after_first_refresh = self.main_window.todo_tree.get_children()
        first_refresh_count = len(after_first_refresh)
        self.assertEqual(first_refresh_count, 2)  # 여전히 2개
        
        # 두 번째 새로고침
        self.main_window.on_refresh()
        after_second_refresh = self.main_window.todo_tree.get_children()
        second_refresh_count = len(after_second_refresh)
        self.assertEqual(second_refresh_count, 2)  # 여전히 2개 (중복 없음)
        
        # 세 번째 새로고침
        self.main_window.on_refresh()
        after_third_refresh = self.main_window.todo_tree.get_children()
        third_refresh_count = len(after_third_refresh)
        self.assertEqual(third_refresh_count, 2)  # 여전히 2개 (중복 없음)
    
    def test_data_change_refresh(self):
        """데이터 변경 후 새로고침 테스트"""
        # 초기 상태
        initial_children = self.main_window.todo_tree.get_children()
        self.assertEqual(len(initial_children), 2)
        
        # 새로운 할일 추가
        new_todo = self.todo_service.add_todo("새로운 할일")
        self.assertIsNotNone(new_todo)
        
        # 새로고침 후 확인
        self.main_window.on_refresh()
        after_add_refresh = self.main_window.todo_tree.get_children()
        self.assertEqual(len(after_add_refresh), 3)  # 3개로 증가
        
        # 다시 새로고침 (중복 확인)
        self.main_window.on_refresh()
        after_second_refresh = self.main_window.todo_tree.get_children()
        self.assertEqual(len(after_second_refresh), 3)  # 여전히 3개
    
    def test_filter_refresh_no_duplication(self):
        """필터 적용 후 새로고침 시 중복 없음 테스트"""
        # 필터 패널이 있는지 확인
        if not hasattr(self.main_window, 'filter_panel'):
            self.skipTest("필터 패널이 없어서 테스트를 건너뜁니다")
        
        # 초기 상태
        initial_count = len(self.main_window.todo_tree.get_children())
        self.assertEqual(initial_count, 2)
        
        # 필터 변경 (완료된 할일 숨기기)
        self.main_window.filter_panel.show_completed_var.set(False)
        filter_options = self.main_window.filter_panel.get_filter_options()
        self.main_window.on_filter_change(filter_options)
        
        # 새로고침
        self.main_window.on_refresh()
        after_filter_refresh = self.main_window.todo_tree.get_children()
        
        # 다시 새로고침 (중복 확인)
        self.main_window.on_refresh()
        after_second_refresh = self.main_window.todo_tree.get_children()
        
        # 개수가 같은지 확인 (중복 없음)
        self.assertEqual(len(after_filter_refresh), len(after_second_refresh))
    
    def test_search_refresh_no_duplication(self):
        """검색 후 새로고침 시 중복 없음 테스트"""
        # 검색 박스가 있는지 확인
        if not hasattr(self.main_window, 'search_box'):
            self.skipTest("검색 박스가 없어서 테스트를 건너뜁니다")
        
        # 초기 상태
        initial_count = len(self.main_window.todo_tree.get_children())
        self.assertEqual(initial_count, 2)
        
        # 검색어 입력
        self.main_window.search_box.search_var.set("테스트")
        self.main_window.on_search("테스트")
        
        # 새로고침
        self.main_window.on_refresh()
        after_search_refresh = self.main_window.todo_tree.get_children()
        
        # 다시 새로고침 (중복 확인)
        self.main_window.on_refresh()
        after_second_refresh = self.main_window.todo_tree.get_children()
        
        # 개수가 같은지 확인 (중복 없음)
        self.assertEqual(len(after_search_refresh), len(after_second_refresh))
    
    def test_node_data_consistency(self):
        """노드 데이터 일관성 테스트"""
        # 초기 상태
        self.main_window.on_refresh()
        
        # 노드 데이터 개수 확인
        tree_children_count = len(self.main_window.todo_tree.get_children())
        todo_nodes_count = len(self.main_window.todo_tree.todo_nodes)
        node_data_count = len(self.main_window.todo_tree.node_data)
        
        # 트리 자식 개수와 todo_nodes 개수가 일치해야 함
        self.assertEqual(tree_children_count, todo_nodes_count)
        
        # 새로고침 후에도 일관성 유지
        self.main_window.on_refresh()
        
        after_refresh_tree_count = len(self.main_window.todo_tree.get_children())
        after_refresh_todo_nodes = len(self.main_window.todo_tree.todo_nodes)
        after_refresh_node_data = len(self.main_window.todo_tree.node_data)
        
        self.assertEqual(after_refresh_tree_count, after_refresh_todo_nodes)
        self.assertEqual(tree_children_count, after_refresh_tree_count)


if __name__ == '__main__':
    unittest.main()