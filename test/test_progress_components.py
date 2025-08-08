"""
진행률 표시 및 시각적 피드백 컴포넌트 테스트
"""

import unittest
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from gui.components import (
    ProgressBar, SearchBox, FilterPanel, StatusBar, 
    TodoProgressWidget, CompactProgressBar
)
from models.todo import Todo
from models.subtask import SubTask


class TestProgressComponents(unittest.TestCase):
    """진행률 컴포넌트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 윈도우 숨기기
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_progress_bar_creation(self):
        """ProgressBar 생성 테스트"""
        progress_bar = ProgressBar(self.root)
        self.assertIsInstance(progress_bar, ttk.Progressbar)
        self.assertEqual(progress_bar.get_progress(), 0.0)
    
    def test_progress_bar_set_progress(self):
        """ProgressBar 진행률 설정 테스트"""
        progress_bar = ProgressBar(self.root)
        
        # 정상 범위 테스트
        progress_bar.set_progress(0.5)
        self.assertEqual(progress_bar.get_progress(), 0.5)
        self.assertEqual(progress_bar['value'], 50.0)
        
        progress_bar.set_progress(1.0)
        self.assertEqual(progress_bar.get_progress(), 1.0)
        self.assertEqual(progress_bar['value'], 100.0)
        
        progress_bar.set_progress(0.0)
        self.assertEqual(progress_bar.get_progress(), 0.0)
        self.assertEqual(progress_bar['value'], 0.0)
    
    def test_progress_bar_invalid_range(self):
        """ProgressBar 잘못된 범위 테스트"""
        progress_bar = ProgressBar(self.root)
        
        # 범위 초과 테스트
        with self.assertRaises(ValueError):
            progress_bar.set_progress(-0.1)
        
        with self.assertRaises(ValueError):
            progress_bar.set_progress(1.1)
    
    def test_search_box_creation(self):
        """SearchBox 생성 테스트"""
        callback_called = False
        search_term = ""
        
        def on_search(term):
            nonlocal callback_called, search_term
            callback_called = True
            search_term = term
        
        search_box = SearchBox(self.root, on_search)
        self.assertIsInstance(search_box, ttk.Frame)
        
        # 검색어 설정 테스트
        search_box.search_var.set("test search")
        self.root.update()  # 이벤트 처리
        
        self.assertTrue(callback_called)
        self.assertEqual(search_term, "test search")
        self.assertEqual(search_box.get_search_term(), "test search")
    
    def test_search_box_clear(self):
        """SearchBox 클리어 테스트"""
        def on_search(term):
            pass
        
        search_box = SearchBox(self.root, on_search)
        search_box.search_var.set("test")
        search_box.clear()
        
        self.assertEqual(search_box.get_search_term(), "")
    
    def test_filter_panel_creation(self):
        """FilterPanel 생성 테스트"""
        filter_options = {}
        
        def on_filter(options):
            nonlocal filter_options
            filter_options = options
        
        filter_panel = FilterPanel(self.root, on_filter)
        self.assertIsInstance(filter_panel, ttk.Frame)
        
        # 기본 옵션 확인
        options = filter_panel.get_filter_options()
        self.assertTrue(options['show_completed'])
        self.assertEqual(options['sort_by'], 'created_at')
        self.assertEqual(options['sort_order'], 'desc')
    
    def test_filter_panel_reset(self):
        """FilterPanel 리셋 테스트"""
        def on_filter(options):
            pass
        
        filter_panel = FilterPanel(self.root, on_filter)
        
        # 옵션 변경
        filter_panel.show_completed_var.set(False)
        filter_panel.sort_by_var.set('title')
        filter_panel.sort_order_var.set('asc')
        
        # 리셋
        filter_panel.reset_filters()
        
        options = filter_panel.get_filter_options()
        self.assertTrue(options['show_completed'])
        self.assertEqual(options['sort_by'], 'created_at')
        self.assertEqual(options['sort_order'], 'desc')
    
    def test_status_bar_creation(self):
        """StatusBar 생성 테스트"""
        status_bar = StatusBar(self.root)
        self.assertIsInstance(status_bar, ttk.Frame)
    
    def test_status_bar_updates(self):
        """StatusBar 업데이트 테스트"""
        status_bar = StatusBar(self.root)
        
        # 상태 메시지 업데이트
        status_bar.update_status("테스트 메시지")
        self.assertEqual(status_bar.status_message_label.cget('text'), "테스트 메시지")
        
        # 할일 개수 업데이트
        status_bar.update_todo_count(5, 2)
        self.assertEqual(status_bar.todo_count_label.cget('text'), "할일: 5개")
        self.assertEqual(status_bar.completion_label.cget('text'), "완료율: 40.0%")
        
        # 마지막 저장 시간 업데이트
        status_bar.update_last_saved("저장됨")
        self.assertEqual(status_bar.last_saved_label.cget('text'), "저장됨")
    
    def test_todo_progress_widget_creation(self):
        """TodoProgressWidget 생성 테스트"""
        widget = TodoProgressWidget(self.root, "테스트 할일", 0.5)
        self.assertIsInstance(widget, ttk.Frame)
        self.assertEqual(widget.progress, 0.5)
    
    def test_todo_progress_widget_update(self):
        """TodoProgressWidget 업데이트 테스트"""
        widget = TodoProgressWidget(self.root, "테스트 할일", 0.0)
        
        # 진행률 업데이트
        widget.update_progress(0.75)
        self.assertEqual(widget.progress, 0.75)
        self.assertEqual(widget.progress_label.cget('text'), "75%")
        
        # 완료 상태 테스트
        widget.update_progress(1.0)
        self.assertEqual(widget.progress, 1.0)
        self.assertEqual(widget.progress_label.cget('text'), "100%")
        # 완료된 할일은 회색으로 표시
        self.assertEqual(widget.title_label.cget('foreground'), 'gray')
    
    def test_compact_progress_bar_creation(self):
        """CompactProgressBar 생성 테스트"""
        progress_bar = CompactProgressBar(self.root, 0.3, width=100, height=20)
        self.assertIsInstance(progress_bar, ttk.Frame)
        self.assertEqual(progress_bar.get_progress(), 0.3)
    
    def test_compact_progress_bar_update(self):
        """CompactProgressBar 업데이트 테스트"""
        progress_bar = CompactProgressBar(self.root, 0.0)
        
        # 진행률 업데이트
        progress_bar.update_progress(0.6)
        self.assertEqual(progress_bar.get_progress(), 0.6)
        
        # 잘못된 범위는 무시
        progress_bar.update_progress(-0.1)
        self.assertEqual(progress_bar.get_progress(), 0.6)  # 변경되지 않음
        
        progress_bar.update_progress(1.1)
        self.assertEqual(progress_bar.get_progress(), 0.6)  # 변경되지 않음


class TestVisualFeedback(unittest.TestCase):
    """시각적 피드백 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """테스트 정리"""
        self.root.destroy()
    
    def test_progress_color_changes(self):
        """진행률에 따른 색상 변경 테스트"""
        progress_bar = ProgressBar(self.root)
        
        # 빨간색 범위 (0-33%)
        progress_bar.set_progress(0.2)
        self.assertIn("Red", progress_bar.cget('style'))
        
        # 노란색 범위 (34-66%)
        progress_bar.set_progress(0.5)
        self.assertIn("Yellow", progress_bar.cget('style'))
        
        # 초록색 범위 (67-99%)
        progress_bar.set_progress(0.8)
        self.assertIn("Green", progress_bar.cget('style'))
        
        # 완료 (100%)
        progress_bar.set_progress(1.0)
        self.assertIn("Complete", progress_bar.cget('style'))
    
    def test_todo_completion_visual_feedback(self):
        """할일 완료 시각적 피드백 테스트"""
        # 완료된 할일 생성
        todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder",
            subtasks=[
                SubTask(1, 1, "하위작업 1", True, datetime.now()),
                SubTask(2, 1, "하위작업 2", True, datetime.now())
            ]
        )
        
        widget = TodoProgressWidget(self.root, todo.title, todo.get_completion_rate())
        
        # 완료된 할일은 회색으로 표시되고 체크 마크가 있어야 함
        self.assertEqual(widget.progress, 1.0)
        self.assertEqual(widget.title_label.cget('foreground'), 'gray')
        self.assertTrue(widget.title_label.cget('text').startswith('✓'))
    
    def test_subtask_completion_visual_feedback(self):
        """하위작업 완료 시각적 피드백 테스트"""
        # 부분 완료된 할일 생성
        todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder",
            subtasks=[
                SubTask(1, 1, "하위작업 1", True, datetime.now()),
                SubTask(2, 1, "하위작업 2", False, datetime.now())
            ]
        )
        
        widget = TodoProgressWidget(self.root, todo.title, todo.get_completion_rate())
        
        # 부분 완료된 할일은 기본 색상이어야 함
        self.assertEqual(widget.progress, 0.5)
        self.assertEqual(widget.title_label.cget('foreground'), 'black')
        self.assertFalse(widget.title_label.cget('text').startswith('✓'))


if __name__ == '__main__':
    unittest.main()