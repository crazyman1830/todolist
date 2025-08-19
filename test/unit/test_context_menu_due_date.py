"""
Context Menu Due Date Integration Tests

Tests for verifying that the context menu due date options work correctly
for both todos and subtasks.
"""

import unittest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.todo_tree import TodoTree
from services.todo_service import TodoService
from models.todo import Todo
from models.subtask import SubTask


class TestContextMenuDueDate(unittest.TestCase):
    """Context menu due date functionality tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Mock TodoService
        self.mock_todo_service = Mock(spec=TodoService)
        # Mock get_all_todos to return empty list initially
        self.mock_todo_service.get_all_todos.return_value = []
        
        # Create test data
        self.test_todo = Todo(
            id=1,
            title="Test Todo",
            created_at=datetime.now(),
            folder_path="test_folder"
        )
        
        self.test_subtask = SubTask(
            id=1,
            todo_id=1,
            title="Test Subtask",
            created_at=datetime.now()
        )
        
        # Create TodoTree
        self.todo_tree = TodoTree(self.root, self.mock_todo_service)
        
    def tearDown(self):
        """Clean up test environment"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_context_menu_has_due_date_options(self):
        """Test that context menus have due date options"""
        # Check todo context menu
        todo_menu_labels = []
        for i in range(self.todo_tree.todo_context_menu.index('end') + 1):
            try:
                label = self.todo_tree.todo_context_menu.entrycget(i, 'label')
                todo_menu_labels.append(label)
            except:
                pass  # Skip separators
        
        self.assertIn("목표 날짜 설정", todo_menu_labels)
        self.assertIn("목표 날짜 제거", todo_menu_labels)
        
        # Check subtask context menu
        subtask_menu_labels = []
        for i in range(self.todo_tree.subtask_context_menu.index('end') + 1):
            try:
                label = self.todo_tree.subtask_context_menu.entrycget(i, 'label')
                subtask_menu_labels.append(label)
            except:
                pass  # Skip separators
        
        self.assertIn("목표 날짜 설정", subtask_menu_labels)
        self.assertIn("목표 날짜 제거", subtask_menu_labels)
    
    @patch('gui.dialogs.DueDateDialog')
    def test_on_set_due_date_for_todo(self, mock_dialog_class):
        """Test setting due date for todo via context menu"""
        # Setup mock dialog
        mock_dialog = Mock()
        mock_dialog.result = datetime.now() + timedelta(days=3)
        mock_dialog_class.return_value = mock_dialog
        
        # Setup mock service responses
        self.mock_todo_service.set_todo_due_date.return_value = True
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        
        # Add todo to tree
        self.todo_tree.node_data['test_item'] = {
            'type': 'todo',
            'todo_id': 1,
            'data': self.test_todo
        }
        
        # Mock selection
        with patch.object(self.todo_tree, 'selection', return_value=['test_item']):
            # Call the handler
            self.todo_tree.on_set_due_date()
        
        # Verify dialog was created with correct parameters
        mock_dialog_class.assert_called_once()
        call_args = mock_dialog_class.call_args
        self.assertEqual(call_args[1]['current_due_date'], self.test_todo.due_date)
        self.assertEqual(call_args[1]['item_type'], "할일")
        
        # Verify service was called
        self.mock_todo_service.set_todo_due_date.assert_called_once_with(1, mock_dialog.result)
    
    @patch('gui.dialogs.DueDateDialog')
    def test_on_set_due_date_for_subtask(self, mock_dialog_class):
        """Test setting due date for subtask via context menu"""
        # Setup mock dialog
        mock_dialog = Mock()
        mock_dialog.result = datetime.now() + timedelta(days=2)
        mock_dialog_class.return_value = mock_dialog
        
        # Setup mock service responses
        self.mock_todo_service.set_subtask_due_date.return_value = True
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        self.mock_todo_service.get_subtasks.return_value = [self.test_subtask]
        
        # Add subtask to tree
        self.todo_tree.node_data['test_subtask_item'] = {
            'type': 'subtask',
            'subtask_id': 1,
            'data': self.test_subtask
        }
        
        # Mock selection
        with patch.object(self.todo_tree, 'selection', return_value=['test_subtask_item']):
            # Call the handler
            self.todo_tree.on_set_subtask_due_date()
        
        # Verify dialog was created with correct parameters
        mock_dialog_class.assert_called_once()
        call_args = mock_dialog_class.call_args
        self.assertEqual(call_args[1]['current_due_date'], self.test_subtask.due_date)
        self.assertEqual(call_args[1]['parent_due_date'], self.test_todo.due_date)
        self.assertEqual(call_args[1]['item_type'], "하위작업")
        
        # Verify service was called
        self.mock_todo_service.set_subtask_due_date.assert_called_once_with(1, 1, mock_dialog.result)
    
    def test_on_remove_due_date_for_todo(self):
        """Test removing due date for todo via context menu"""
        # Set up todo with due date
        self.test_todo.due_date = datetime.now() + timedelta(days=5)
        
        # Setup mock service responses
        self.mock_todo_service.set_todo_due_date.return_value = True
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        
        # Add todo to tree
        self.todo_tree.node_data['test_item'] = {
            'type': 'todo',
            'todo_id': 1,
            'data': self.test_todo
        }
        
        # Mock selection
        with patch.object(self.todo_tree, 'selection', return_value=['test_item']):
            # Call the handler
            self.todo_tree.on_remove_due_date()
        
        # Verify service was called to remove due date (set to None)
        self.mock_todo_service.set_todo_due_date.assert_called_once_with(1, None)
    
    def test_on_remove_due_date_for_subtask(self):
        """Test removing due date for subtask via context menu"""
        # Set up subtask with due date
        self.test_subtask.due_date = datetime.now() + timedelta(days=3)
        
        # Setup mock service responses
        self.mock_todo_service.set_subtask_due_date.return_value = True
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        self.mock_todo_service.get_subtasks.return_value = [self.test_subtask]
        
        # Add subtask to tree
        self.todo_tree.node_data['test_subtask_item'] = {
            'type': 'subtask',
            'subtask_id': 1,
            'data': self.test_subtask
        }
        
        # Mock selection
        with patch.object(self.todo_tree, 'selection', return_value=['test_subtask_item']):
            # Call the handler
            self.todo_tree.on_remove_subtask_due_date()
        
        # Verify service was called to remove due date (set to None)
        self.mock_todo_service.set_subtask_due_date.assert_called_once_with(1, 1, None)
    
    def test_context_menu_handlers_with_no_selection(self):
        """Test that handlers handle no selection gracefully"""
        # Mock empty selection
        with patch.object(self.todo_tree, 'selection', return_value=[]):
            # These should not raise exceptions
            self.todo_tree.on_set_due_date()
            self.todo_tree.on_remove_due_date()
            self.todo_tree.on_set_subtask_due_date()
            self.todo_tree.on_remove_subtask_due_date()
        
        # Verify no service calls were made
        self.mock_todo_service.set_todo_due_date.assert_not_called()
        self.mock_todo_service.set_subtask_due_date.assert_not_called()
    
    def test_context_menu_handlers_with_wrong_item_type(self):
        """Test that handlers handle wrong item types gracefully"""
        # Add todo to tree but try subtask handler
        self.todo_tree.node_data['test_item'] = {
            'type': 'todo',
            'todo_id': 1,
            'data': self.test_todo
        }
        
        with patch.object(self.todo_tree, 'selection', return_value=['test_item']):
            # These should not raise exceptions or make service calls
            self.todo_tree.on_set_subtask_due_date()
            self.todo_tree.on_remove_subtask_due_date()
        
        # Verify no service calls were made
        self.mock_todo_service.set_subtask_due_date.assert_not_called()
    
    @patch('gui.dialogs.DueDateDialog')
    def test_dialog_error_handling(self, mock_dialog_class):
        """Test error handling when dialog creation fails"""
        # Setup mock dialog to raise exception
        mock_dialog_class.side_effect = Exception("Dialog creation failed")
        
        # Add todo to tree
        self.todo_tree.node_data['test_item'] = {
            'type': 'todo',
            'todo_id': 1,
            'data': self.test_todo
        }
        
        # Mock selection
        with patch.object(self.todo_tree, 'selection', return_value=['test_item']):
            # This should not raise exception (should be caught and logged)
            self.todo_tree.on_set_due_date()
        
        # Verify no service calls were made due to dialog error
        self.mock_todo_service.set_todo_due_date.assert_not_called()
    
    def test_status_update_event_generation(self):
        """Test that status update events are generated after due date changes"""
        # Set up todo with due date
        self.test_todo.due_date = datetime.now() + timedelta(days=5)
        
        # Setup mock service responses
        self.mock_todo_service.set_todo_due_date.return_value = True
        self.mock_todo_service.get_todo_by_id.return_value = self.test_todo
        
        # Add todo to tree
        self.todo_tree.node_data['test_item'] = {
            'type': 'todo',
            'todo_id': 1,
            'data': self.test_todo
        }
        
        # Mock event generation
        with patch.object(self.todo_tree, 'event_generate') as mock_event_gen:
            with patch.object(self.todo_tree, 'selection', return_value=['test_item']):
                # Call the handler
                self.todo_tree.on_remove_due_date()
        
        # Verify status update event was generated
        mock_event_gen.assert_called_with('<<StatusUpdate>>')


if __name__ == '__main__':
    unittest.main()