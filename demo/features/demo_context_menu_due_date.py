"""
Context Menu Due Date Demo

Demonstrates the context menu functionality for setting and removing due dates
on both todos and subtasks.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.todo_tree import TodoTree
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from models.todo import Todo
from models.subtask import SubTask


class ContextMenuDueDateDemo:
    """Demo application for context menu due date functionality"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Context Menu Due Date Demo")
        self.root.geometry("800x600")
        
        # Initialize services
        storage_service = StorageService("demo_data/context_menu_demo.json")
        file_service = FileService()
        self.todo_service = TodoService(storage_service, file_service)
        
        # Setup UI
        self.setup_ui()
        
        # Create sample data
        self.create_sample_data()
        
        # Show instructions
        self.show_instructions()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions label
        self.instructions_label = ttk.Label(
            main_frame,
            text="Right-click on todos or subtasks to see context menu with due date options",
            font=('TkDefaultFont', 10, 'bold')
        )
        self.instructions_label.pack(pady=(0, 10))
        
        # TodoTree
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.todo_tree = TodoTree(tree_frame, self.todo_service)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Refresh Tree",
            command=self.refresh_tree
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Add Sample Todo",
            command=self.add_sample_todo
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        ).pack(side=tk.RIGHT)
    
    def create_sample_data(self):
        """Create sample todos and subtasks for demonstration"""
        try:
            # Clear existing data
            self.clear_all()
            
            # Create sample todos
            todo1 = self.todo_service.add_todo("Project Planning Meeting")
            todo2 = self.todo_service.add_todo("Website Development")
            todo3 = self.todo_service.add_todo("Code Review Session")
            
            if todo1:
                # Add subtasks to first todo
                self.todo_service.add_subtask(todo1.id, "Prepare agenda")
                self.todo_service.add_subtask(todo1.id, "Book meeting room")
                self.todo_service.add_subtask(todo1.id, "Send invitations")
                
                # Set due date for the todo
                due_date = datetime.now() + timedelta(days=2)
                self.todo_service.set_todo_due_date(todo1.id, due_date)
            
            if todo2:
                # Add subtasks to second todo
                self.todo_service.add_subtask(todo2.id, "Design mockups")
                self.todo_service.add_subtask(todo2.id, "Frontend development")
                self.todo_service.add_subtask(todo2.id, "Backend API")
                self.todo_service.add_subtask(todo2.id, "Testing")
                
                # Set due date for some subtasks
                subtasks = self.todo_service.get_subtasks(todo2.id)
                if subtasks:
                    # Set due date for first subtask
                    due_date = datetime.now() + timedelta(days=1)
                    self.todo_service.set_subtask_due_date(todo2.id, subtasks[0].id, due_date)
                    
                    # Set due date for second subtask
                    due_date = datetime.now() + timedelta(days=5)
                    self.todo_service.set_subtask_due_date(todo2.id, subtasks[1].id, due_date)
            
            if todo3:
                # Set urgent date for demonstration (1 hour from now)
                urgent_date = datetime.now() + timedelta(hours=1)
                self.todo_service.set_todo_due_date(todo3.id, urgent_date)
            
            # Refresh the tree to show the data
            self.refresh_tree()
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
    
    def add_sample_todo(self):
        """Add a new sample todo"""
        try:
            todo = self.todo_service.add_todo(
                f"New Todo {datetime.now().strftime('%H:%M:%S')}"
            )
            
            if todo:
                # Add a subtask
                self.todo_service.add_subtask(todo.id, "Sample subtask")
                
                # Refresh tree
                self.refresh_tree()
                
        except Exception as e:
            print(f"Error adding sample todo: {e}")
    
    def refresh_tree(self):
        """Refresh the todo tree"""
        try:
            self.todo_tree.refresh_tree()
        except Exception as e:
            print(f"Error refreshing tree: {e}")
    
    def clear_all(self):
        """Clear all todos"""
        try:
            todos = self.todo_service.get_all_todos()
            for todo in todos:
                self.todo_service.delete_todo(todo.id)
            self.refresh_tree()
        except Exception as e:
            print(f"Error clearing todos: {e}")
    
    def show_instructions(self):
        """Show detailed instructions in a popup"""
        instructions = """
Context Menu Due Date Demo Instructions:

1. RIGHT-CLICK on any todo or subtask to open the context menu

2. For TODOS, you'll see:
   - "목표 날짜 설정" (Set Due Date) - Opens date picker dialog
   - "목표 날짜 제거" (Remove Due Date) - Removes existing due date

3. For SUBTASKS, you'll see:
   - "목표 날짜 설정" (Set Due Date) - Opens date picker dialog
   - "목표 날짜 제거" (Remove Due Date) - Removes existing due date

4. Due dates are displayed in the "목표 날짜" column with:
   - Color coding based on urgency (red for overdue, yellow for urgent, etc.)
   - Relative time display (e.g., "2일 후", "1시간 전")
   - Time remaining text

5. Items with due dates show urgency-based styling:
   - Overdue items: Red text, bold font
   - Urgent items: Orange text, bold font
   - Warning items: Yellow text
   - Normal items: Default styling

Try right-clicking on different items to test the functionality!
        """
        
        # Create instruction window
        instruction_window = tk.Toplevel(self.root)
        instruction_window.title("Instructions")
        instruction_window.geometry("600x400")
        instruction_window.transient(self.root)
        
        # Add text widget with scrollbar
        text_frame = ttk.Frame(instruction_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('TkDefaultFont', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, instructions)
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            instruction_window,
            text="Close",
            command=instruction_window.destroy
        ).pack(pady=10)
    
    def run(self):
        """Run the demo application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        except Exception as e:
            print(f"Demo error: {e}")
        finally:
            try:
                self.root.destroy()
            except:
                pass


def main():
    """Main function to run the demo"""
    print("Starting Context Menu Due Date Demo...")
    print("This demo shows the context menu functionality for due dates.")
    print("Right-click on todos and subtasks to see the due date options.")
    print()
    
    try:
        demo = ContextMenuDueDateDemo()
        demo.run()
    except Exception as e:
        print(f"Failed to start demo: {e}")
        return 1
    
    print("Demo completed.")
    return 0


if __name__ == "__main__":
    exit(main())