#!/usr/bin/env python3
"""
Test script for dialog integration with due date functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from datetime import datetime, timedelta
from gui.dialogs import AddTodoDialog


def test_add_todo_dialog_simple():
    """Test the add todo dialog with due date functionality - simple version."""
    print("Testing Add Todo Dialog with Due Date...")
    
    root = tk.Tk()
    root.title("Test Root Window")
    
    # Create a simple test button
    def show_dialog():
        dialog = AddTodoDialog(root)
        root.wait_window(dialog)
        
        result = dialog.result
        if result:
            print(f"Result: {result}")
            print(f"Title: {result.get('title')}")
            print(f"Due Date: {result.get('due_date')}")
        else:
            print("Dialog was cancelled")
        
        root.quit()  # Exit the mainloop
    
    test_button = tk.Button(root, text="Show Add Todo Dialog", command=show_dialog)
    test_button.pack(pady=20)
    
    # Start the GUI event loop
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    print("Dialog Integration Test - Simple Version")
    print("=" * 50)
    
    try:
        test_add_todo_dialog_simple()
        print("\nTest completed!")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()