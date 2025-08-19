#!/usr/bin/env python3
"""
Task 9 구현 검증 스크립트

컨텍스트 메뉴 및 사용자 상호작용 구현 검증:
- 우클릭 컨텍스트 메뉴 구현 (수정, 삭제, 하위작업 추가, 폴더 열기)
- 키보드 단축키 구현 (Ctrl+N, Del, F2 등)
- 드래그 앤 드롭 기능 구현 (할일 순서 변경)
- 더블클릭으로 할일 수정 기능
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
import tkinter as tk
from unittest.mock import Mock

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.todo_tree import TodoTree
from gui.main_window import MainWindow
from services.todo_service import TodoService


def test_context_menu_implementation():
    """컨텍스트 메뉴 구현 검증"""
    print("1. 컨텍스트 메뉴 구현 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # TodoTree 생성
        frame = tk.Frame(root)
        tree = TodoTree(frame, mock_service)
        
        # 컨텍스트 메뉴 존재 확인
        assert hasattr(tree, 'todo_context_menu'), "할일용 컨텍스트 메뉴가 없습니다"
        assert hasattr(tree, 'subtask_context_menu'), "하위작업용 컨텍스트 메뉴가 없습니다"
        assert hasattr(tree, 'empty_context_menu'), "빈 공간용 컨텍스트 메뉴가 없습니다"
        
        # 메뉴 타입 확인
        assert isinstance(tree.todo_context_menu, tk.Menu), "할일 컨텍스트 메뉴가 Menu 타입이 아닙니다"
        assert isinstance(tree.subtask_context_menu, tk.Menu), "하위작업 컨텍스트 메뉴가 Menu 타입이 아닙니다"
        assert isinstance(tree.empty_context_menu, tk.Menu), "빈 공간 컨텍스트 메뉴가 Menu 타입이 아닙니다"
        
        print("   ✅ 컨텍스트 메뉴 구현 완료")
        
    finally:
        root.destroy()


def test_keyboard_shortcuts_implementation():
    """키보드 단축키 구현 검증"""
    print("2. 키보드 단축키 구현 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # MainWindow 생성
        main_window = MainWindow(mock_service)
        
        # 메인 윈도우 키보드 바인딩 확인
        main_bindings = main_window.root.bind()
        expected_main_bindings = [
            '<Control-Key-n>',  # Ctrl+N
            '<Control-Key-q>',  # Ctrl+Q
            '<Key-F2>',         # F2
            '<Key-Delete>',     # Del
            '<Control-Shift-Key-n>',  # Ctrl+Shift+N
            '<Key-F5>'          # F5
        ]
        
        for binding in expected_main_bindings:
            assert binding in main_bindings, f"메인 윈도우에 {binding} 바인딩이 없습니다"
        
        # TodoTree 키보드 바인딩 확인
        tree_bindings = main_window.todo_tree.bind()
        expected_tree_bindings = [
            '<Key-Return>',     # Enter
            '<Key-Delete>',     # Delete
            '<Key-F2>',         # F2
            '<Key-space>',      # Space
            '<Key-Up>',         # Up arrow
            '<Key-Down>',       # Down arrow
            '<Key-Left>',       # Left arrow
            '<Key-Right>'       # Right arrow
        ]
        
        for binding in expected_tree_bindings:
            assert binding in tree_bindings, f"TodoTree에 {binding} 바인딩이 없습니다"
        
        print("   ✅ 키보드 단축키 구현 완료")
        
    finally:
        main_window.root.destroy()


def test_drag_and_drop_implementation():
    """드래그 앤 드롭 구현 검증"""
    print("3. 드래그 앤 드롭 구현 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # TodoTree 생성
        frame = tk.Frame(root)
        tree = TodoTree(frame, mock_service)
        
        # 드래그 데이터 구조 확인
        assert hasattr(tree, '_drag_data'), "드래그 데이터 구조가 없습니다"
        assert 'item' in tree._drag_data, "드래그 데이터에 item 필드가 없습니다"
        assert 'start_x' in tree._drag_data, "드래그 데이터에 start_x 필드가 없습니다"
        assert 'start_y' in tree._drag_data, "드래그 데이터에 start_y 필드가 없습니다"
        assert 'is_dragging' in tree._drag_data, "드래그 데이터에 is_dragging 필드가 없습니다"
        assert 'drag_threshold' in tree._drag_data, "드래그 데이터에 drag_threshold 필드가 없습니다"
        
        # 드래그 이벤트 바인딩 확인
        bindings = tree.bind()
        assert '<B1-Motion>' in bindings, "드래그 모션 이벤트가 바인딩되지 않았습니다"
        assert '<ButtonRelease-1>' in bindings, "드래그 릴리스 이벤트가 바인딩되지 않았습니다"
        
        # 드래그 관련 메서드 존재 확인
        assert hasattr(tree, 'on_drag_motion'), "on_drag_motion 메서드가 없습니다"
        assert hasattr(tree, 'on_drag_release'), "on_drag_release 메서드가 없습니다"
        assert hasattr(tree, '_handle_drop'), "_handle_drop 메서드가 없습니다"
        assert hasattr(tree, '_reorder_todos'), "_reorder_todos 메서드가 없습니다"
        
        print("   ✅ 드래그 앤 드롭 구현 완료")
        
    finally:
        root.destroy()


def test_double_click_implementation():
    """더블클릭 수정 기능 구현 검증"""
    print("4. 더블클릭 수정 기능 구현 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # TodoTree 생성
        frame = tk.Frame(root)
        tree = TodoTree(frame, mock_service)
        
        # 더블클릭 이벤트 바인딩 확인
        bindings = tree.bind()
        assert '<Double-Button-1>' in bindings, "더블클릭 이벤트가 바인딩되지 않았습니다"
        
        # 더블클릭 핸들러 메서드 존재 확인
        assert hasattr(tree, 'on_double_click'), "on_double_click 메서드가 없습니다"
        
        print("   ✅ 더블클릭 수정 기능 구현 완료")
        
    finally:
        root.destroy()


def test_event_handler_connections():
    """이벤트 핸들러 연결 검증"""
    print("5. 이벤트 핸들러 연결 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # MainWindow 생성
        main_window = MainWindow(mock_service)
        
        # TodoTree 이벤트 핸들러 연결 확인
        tree = main_window.todo_tree
        
        # 핸들러 메서드들이 메인 윈도우 메서드와 연결되었는지 확인
        assert tree.on_edit_todo == main_window.on_edit_todo, "on_edit_todo 핸들러가 연결되지 않았습니다"
        assert tree.on_delete_todo == main_window.on_delete_todo, "on_delete_todo 핸들러가 연결되지 않았습니다"
        assert tree.on_add_subtask == main_window.on_add_subtask, "on_add_subtask 핸들러가 연결되지 않았습니다"
        assert tree.on_edit_subtask == main_window.on_edit_subtask, "on_edit_subtask 핸들러가 연결되지 않았습니다"
        assert tree.on_delete_subtask == main_window.on_delete_subtask, "on_delete_subtask 핸들러가 연결되지 않았습니다"
        assert tree.on_open_folder == main_window.on_open_folder, "on_open_folder 핸들러가 연결되지 않았습니다"
        assert tree.on_add_new_todo == main_window.on_add_todo, "on_add_new_todo 핸들러가 연결되지 않았습니다"
        assert tree.on_todo_reordered == main_window.on_todo_reordered, "on_todo_reordered 핸들러가 연결되지 않았습니다"
        
        print("   ✅ 이벤트 핸들러 연결 완료")
        
    finally:
        main_window.root.destroy()


def test_dialog_integration():
    """다이얼로그 통합 검증"""
    print("6. 다이얼로그 통합 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # MainWindow 생성
        main_window = MainWindow(mock_service)
        
        # 다이얼로그 import 확인
        from gui.dialogs import (
            show_add_todo_dialog, show_edit_todo_dialog, show_add_subtask_dialog,
            show_delete_confirm_dialog, show_folder_delete_confirm_dialog
        )
        
        # 메인 윈도우에서 다이얼로그 함수들이 import되었는지 확인
        import gui.main_window
        assert hasattr(gui.main_window, 'show_add_todo_dialog'), "show_add_todo_dialog가 import되지 않았습니다"
        assert hasattr(gui.main_window, 'show_edit_todo_dialog'), "show_edit_todo_dialog가 import되지 않았습니다"
        assert hasattr(gui.main_window, 'show_add_subtask_dialog'), "show_add_subtask_dialog가 import되지 않았습니다"
        assert hasattr(gui.main_window, 'show_delete_confirm_dialog'), "show_delete_confirm_dialog가 import되지 않았습니다"
        
        print("   ✅ 다이얼로그 통합 완료")
        
    finally:
        main_window.root.destroy()


def test_menu_functionality():
    """메뉴 기능 검증"""
    print("7. 메뉴 기능 검증...")
    
    # Mock 서비스 생성
    mock_service = Mock(spec=TodoService)
    mock_service.get_all_todos.return_value = []
    
    # Tkinter 루트 생성
    root = tk.Tk()
    root.withdraw()
    
    try:
        # MainWindow 생성
        main_window = MainWindow(mock_service)
        
        # 메뉴바 존재 확인
        assert hasattr(main_window, 'menubar'), "메뉴바가 없습니다"
        assert isinstance(main_window.menubar, tk.Menu), "메뉴바가 Menu 타입이 아닙니다"
        
        # 툴바 존재 확인
        assert hasattr(main_window, 'toolbar'), "툴바가 없습니다"
        
        # 주요 버튼들 존재 확인
        assert hasattr(main_window, 'btn_add'), "할일 추가 버튼이 없습니다"
        assert hasattr(main_window, 'btn_edit'), "수정 버튼이 없습니다"
        assert hasattr(main_window, 'btn_delete'), "삭제 버튼이 없습니다"
        assert hasattr(main_window, 'btn_add_subtask'), "하위작업 추가 버튼이 없습니다"
        assert hasattr(main_window, 'btn_open_folder'), "폴더 열기 버튼이 없습니다"
        
        print("   ✅ 메뉴 기능 완료")
        
    finally:
        main_window.root.destroy()


def main():
    """메인 검증 함수"""
    print("="*70)
    print("           Task 9: 컨텍스트 메뉴 및 사용자 상호작용 구현 검증")
    print("="*70)
    
    try:
        test_context_menu_implementation()
        test_keyboard_shortcuts_implementation()
        test_drag_and_drop_implementation()
        test_double_click_implementation()
        test_event_handler_connections()
        test_dialog_integration()
        test_menu_functionality()
        
        print("\n" + "="*70)
        print("                        🎉 모든 검증 완료!")
        print("="*70)
        print("구현된 기능:")
        print("✅ 우클릭 컨텍스트 메뉴 (할일/하위작업/빈공간별 다른 메뉴)")
        print("✅ 키보드 단축키 (Ctrl+N, Del, F2, Ctrl+Shift+N, F5, Space, 방향키)")
        print("✅ 드래그 앤 드롭 기능 (할일 순서 변경)")
        print("✅ 더블클릭으로 할일/하위작업 수정")
        print("✅ 이벤트 핸들러 연결")
        print("✅ 다이얼로그 통합")
        print("✅ 메뉴 및 툴바 기능")
        print("\nRequirements 4.2, 4.3, 8.1, 8.2가 모두 구현되었습니다!")
        print("="*70)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 검증 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())