#!/usr/bin/env python3
"""
Unit tests for GUI dialog classes.
Tests all dialog functionality including validation and error handling.
"""

import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.dialogs import (
    BaseDialog,
    AddTodoDialog,
    EditTodoDialog,
    AddSubtaskDialog,
    ConfirmDialog,
    DeleteConfirmDialog,
    FolderDeleteConfirmDialog,
    show_add_todo_dialog,
    show_edit_todo_dialog,
    show_add_subtask_dialog,
    show_delete_confirm_dialog,
    show_folder_delete_confirm_dialog
)


class TestBaseDialog(unittest.TestCase):
    """Test the BaseDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window during tests
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_base_dialog_creation(self):
        """Test that BaseDialog can be created."""
        dialog = BaseDialog(self.root, "Test Dialog")
        self.assertEqual(dialog.title(), "Test Dialog")
        self.assertIsNone(dialog.result)
        dialog.destroy()
    
    def test_base_dialog_center_on_parent(self):
        """Test that dialog centers on parent."""
        dialog = BaseDialog(self.root, "Test Dialog")
        # Just verify the method exists and can be called
        dialog.center_on_parent()
        dialog.destroy()


class TestAddTodoDialog(unittest.TestCase):
    """Test the AddTodoDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_add_todo_dialog_creation(self):
        """Test that AddTodoDialog can be created."""
        dialog = AddTodoDialog(self.root)
        self.assertEqual(dialog.title(), "할일 추가")
        self.assertEqual(dialog.title_var.get(), "")
        dialog.destroy()
    
    def test_add_todo_dialog_validation_empty_title(self):
        """Test validation with empty title."""
        dialog = AddTodoDialog(self.root)
        dialog.title_var.set("")
        
        with patch.object(dialog, 'show_error') as mock_error:
            result = dialog.validate_input()
            self.assertFalse(result)
            mock_error.assert_called_once_with("할일 제목을 입력해주세요.")
        
        dialog.destroy()
    
    def test_add_todo_dialog_validation_long_title(self):
        """Test validation with title too long."""
        dialog = AddTodoDialog(self.root)
        long_title = "a" * 101  # 101 characters
        dialog.title_var.set(long_title)
        
        with patch.object(dialog, 'show_error') as mock_error:
            result = dialog.validate_input()
            self.assertFalse(result)
            mock_error.assert_called_once_with("할일 제목은 100자를 초과할 수 없습니다.")
        
        dialog.destroy()
    
    def test_add_todo_dialog_validation_valid_title(self):
        """Test validation with valid title."""
        dialog = AddTodoDialog(self.root)
        dialog.title_var.set("Valid Todo Title")
        
        result = dialog.validate_input()
        self.assertTrue(result)
        
        dialog.destroy()
    
    def test_add_todo_dialog_clean_title(self):
        """Test title cleaning functionality."""
        dialog = AddTodoDialog(self.root)
        
        # Test cleaning special characters
        dirty_title = "Test<>Title:/\\|?*"
        cleaned = dialog._clean_title(dirty_title)
        self.assertEqual(cleaned, "Test__Title______")
        
        # Test cleaning multiple spaces
        spaced_title = "Test   Multiple    Spaces"
        cleaned = dialog._clean_title(spaced_title)
        self.assertEqual(cleaned, "Test Multiple Spaces")
        
        dialog.destroy()
    
    def test_add_todo_dialog_get_result(self):
        """Test getting dialog result."""
        dialog = AddTodoDialog(self.root)
        dialog.title_var.set("  Test Todo  ")
        
        result = dialog.get_result()
        self.assertEqual(result, "Test Todo")
        
        dialog.destroy()


class TestEditTodoDialog(unittest.TestCase):
    """Test the EditTodoDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_edit_todo_dialog_creation(self):
        """Test that EditTodoDialog can be created."""
        current_title = "Current Todo"
        dialog = EditTodoDialog(self.root, current_title)
        self.assertEqual(dialog.title(), "할일 수정")
        self.assertEqual(dialog.title_var.get(), current_title)
        self.assertEqual(dialog.current_title, current_title)
        dialog.destroy()
    
    def test_edit_todo_dialog_validation(self):
        """Test validation functionality."""
        dialog = EditTodoDialog(self.root, "Current Todo")
        
        # Test empty title
        dialog.title_var.set("")
        with patch.object(dialog, 'show_error') as mock_error:
            result = dialog.validate_input()
            self.assertFalse(result)
            mock_error.assert_called_once_with("할일 제목을 입력해주세요.")
        
        dialog.destroy()
    
    def test_edit_todo_dialog_get_result_unchanged(self):
        """Test getting result when title is unchanged."""
        current_title = "Current Todo"
        dialog = EditTodoDialog(self.root, current_title)
        dialog.title_var.set(current_title)
        
        result = dialog.get_result()
        self.assertIsNone(result)  # Should return None if unchanged
        
        dialog.destroy()
    
    def test_edit_todo_dialog_get_result_changed(self):
        """Test getting result when title is changed."""
        current_title = "Current Todo"
        dialog = EditTodoDialog(self.root, current_title)
        dialog.title_var.set("New Todo Title")
        
        result = dialog.get_result()
        self.assertEqual(result, "New Todo Title")
        
        dialog.destroy()


class TestAddSubtaskDialog(unittest.TestCase):
    """Test the AddSubtaskDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_add_subtask_dialog_creation(self):
        """Test that AddSubtaskDialog can be created."""
        todo_title = "Parent Todo"
        dialog = AddSubtaskDialog(self.root, todo_title)
        self.assertEqual(dialog.title(), "하위작업 추가")
        self.assertEqual(dialog.todo_title, todo_title)
        self.assertEqual(dialog.subtask_var.get(), "")
        dialog.destroy()
    
    def test_add_subtask_dialog_validation_empty(self):
        """Test validation with empty subtask."""
        dialog = AddSubtaskDialog(self.root, "Parent Todo")
        dialog.subtask_var.set("")
        
        with patch.object(dialog, 'show_error') as mock_error:
            result = dialog.validate_input()
            self.assertFalse(result)
            mock_error.assert_called_once_with("하위작업 내용을 입력해주세요.")
        
        dialog.destroy()
    
    def test_add_subtask_dialog_validation_too_long(self):
        """Test validation with subtask too long."""
        dialog = AddSubtaskDialog(self.root, "Parent Todo")
        long_subtask = "a" * 201  # 201 characters
        dialog.subtask_var.set(long_subtask)
        
        with patch.object(dialog, 'show_error') as mock_error:
            result = dialog.validate_input()
            self.assertFalse(result)
            mock_error.assert_called_once_with("하위작업 내용은 200자를 초과할 수 없습니다.")
        
        dialog.destroy()
    
    def test_add_subtask_dialog_validation_valid(self):
        """Test validation with valid subtask."""
        dialog = AddSubtaskDialog(self.root, "Parent Todo")
        dialog.subtask_var.set("Valid Subtask")
        
        result = dialog.validate_input()
        self.assertTrue(result)
        
        dialog.destroy()
    
    def test_add_subtask_dialog_get_result(self):
        """Test getting dialog result."""
        dialog = AddSubtaskDialog(self.root, "Parent Todo")
        dialog.subtask_var.set("  Test Subtask  ")
        
        result = dialog.get_result()
        self.assertEqual(result, "Test Subtask")
        
        dialog.destroy()


class TestConfirmDialog(unittest.TestCase):
    """Test the ConfirmDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_confirm_dialog_creation(self):
        """Test that ConfirmDialog can be created."""
        message = "Are you sure?"
        dialog = ConfirmDialog(self.root, message)
        self.assertEqual(dialog.title(), "확인")
        self.assertEqual(dialog.message, message)
        dialog.destroy()
    
    def test_confirm_dialog_custom_params(self):
        """Test ConfirmDialog with custom parameters."""
        message = "Custom message"
        title = "Custom Title"
        ok_text = "Yes"
        cancel_text = "No"
        
        dialog = ConfirmDialog(self.root, message, title, ok_text, cancel_text)
        self.assertEqual(dialog.title(), title)
        self.assertEqual(dialog.message, message)
        self.assertEqual(dialog.ok_text, ok_text)
        self.assertEqual(dialog.cancel_text, cancel_text)
        dialog.destroy()
    
    def test_confirm_dialog_get_result(self):
        """Test getting dialog result."""
        dialog = ConfirmDialog(self.root, "Test message")
        result = dialog.get_result()
        self.assertTrue(result)
        dialog.destroy()


class TestDeleteConfirmDialog(unittest.TestCase):
    """Test the DeleteConfirmDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_delete_confirm_dialog_creation(self):
        """Test that DeleteConfirmDialog can be created."""
        item_name = "Test Item"
        dialog = DeleteConfirmDialog(self.root, item_name)
        self.assertEqual(dialog.title(), "삭제 확인")
        self.assertIn(item_name, dialog.message)
        dialog.destroy()
    
    def test_delete_confirm_dialog_custom_type(self):
        """Test DeleteConfirmDialog with custom item type."""
        item_name = "Test Item"
        item_type = "하위작업"
        dialog = DeleteConfirmDialog(self.root, item_name, item_type)
        self.assertIn(item_name, dialog.message)
        self.assertIn(item_type, dialog.message)
        dialog.destroy()


class TestFolderDeleteConfirmDialog(unittest.TestCase):
    """Test the FolderDeleteConfirmDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_folder_delete_confirm_dialog_creation(self):
        """Test that FolderDeleteConfirmDialog can be created."""
        todo_title = "Test Todo"
        dialog = FolderDeleteConfirmDialog(self.root, todo_title)
        self.assertEqual(dialog.title(), "폴더 삭제 확인")
        self.assertIn(todo_title, dialog.message)
        self.assertEqual(dialog.ok_text, "폴더도 삭제")
        self.assertEqual(dialog.cancel_text, "폴더 유지")
        dialog.destroy()


class TestUtilityFunctions(unittest.TestCase):
    """Test the utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    @patch('gui.dialogs.AddTodoDialog')
    def test_show_add_todo_dialog(self, mock_dialog_class):
        """Test show_add_todo_dialog utility function."""
        mock_dialog = MagicMock()
        mock_dialog.result = "Test Todo"
        mock_dialog_class.return_value = mock_dialog
        
        with patch.object(self.root, 'wait_window'):
            result = show_add_todo_dialog(self.root)
            
        mock_dialog_class.assert_called_once_with(self.root)
        self.assertEqual(result, "Test Todo")
    
    @patch('gui.dialogs.EditTodoDialog')
    def test_show_edit_todo_dialog(self, mock_dialog_class):
        """Test show_edit_todo_dialog utility function."""
        mock_dialog = MagicMock()
        mock_dialog.result = "Updated Todo"
        mock_dialog_class.return_value = mock_dialog
        
        with patch.object(self.root, 'wait_window'):
            result = show_edit_todo_dialog(self.root, "Original Todo")
            
        mock_dialog_class.assert_called_once_with(self.root, "Original Todo")
        self.assertEqual(result, "Updated Todo")
    
    @patch('gui.dialogs.AddSubtaskDialog')
    def test_show_add_subtask_dialog(self, mock_dialog_class):
        """Test show_add_subtask_dialog utility function."""
        mock_dialog = MagicMock()
        mock_dialog.result = "Test Subtask"
        mock_dialog_class.return_value = mock_dialog
        
        with patch.object(self.root, 'wait_window'):
            result = show_add_subtask_dialog(self.root, "Parent Todo")
            
        mock_dialog_class.assert_called_once_with(self.root, "Parent Todo")
        self.assertEqual(result, "Test Subtask")
    
    @patch('gui.dialogs.DeleteConfirmDialog')
    def test_show_delete_confirm_dialog(self, mock_dialog_class):
        """Test show_delete_confirm_dialog utility function."""
        mock_dialog = MagicMock()
        mock_dialog.result = True
        mock_dialog_class.return_value = mock_dialog
        
        with patch.object(self.root, 'wait_window'):
            result = show_delete_confirm_dialog(self.root, "Test Item")
            
        mock_dialog_class.assert_called_once_with(self.root, "Test Item", "할일")
        self.assertTrue(result)
    
    @patch('gui.dialogs.FolderDeleteConfirmDialog')
    def test_show_folder_delete_confirm_dialog(self, mock_dialog_class):
        """Test show_folder_delete_confirm_dialog utility function."""
        mock_dialog = MagicMock()
        mock_dialog.result = True
        mock_dialog_class.return_value = mock_dialog
        
        with patch.object(self.root, 'wait_window'):
            result = show_folder_delete_confirm_dialog(self.root, "Test Todo")
            
        mock_dialog_class.assert_called_once_with(self.root, "Test Todo")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()