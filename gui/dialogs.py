"""
GUI Dialog classes for the Todo Manager application.

This module contains all dialog windows used in the GUI application:
- AddTodoDialog: Dialog for adding new todos
- EditTodoDialog: Dialog for editing existing todos
- AddSubtaskDialog: Dialog for adding subtasks to todos
- ConfirmDialog: Dialog for confirmation prompts
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional


class BaseDialog(tk.Toplevel):
    """Base class for all dialog windows with common functionality."""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 200):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        
        # Configure dialog window
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog on parent window
        self.center_on_parent()
        
        # Setup UI
        self.setup_ui()
        
        # Bind events
        self.bind('<Return>', self.on_ok)
        self.bind('<Escape>', self.on_cancel)
        
        # Focus on first input
        self.focus_first_input()
    
    def center_on_parent(self):
        """Center the dialog window on its parent."""
        self.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = self.winfo_reqwidth()
        dialog_height = self.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI. Override in subclasses."""
        pass
    
    def focus_first_input(self):
        """Focus on the first input field. Override in subclasses."""
        pass
    
    def validate_input(self) -> bool:
        """Validate user input. Override in subclasses."""
        return True
    
    def on_ok(self, event=None):
        """Handle OK button click."""
        if self.validate_input():
            self.result = self.get_result()
            self.destroy()
    
    def on_cancel(self, event=None):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()
    
    def get_result(self):
        """Get the dialog result. Override in subclasses."""
        return None
    
    def show_error(self, message: str, title: str = "오류"):
        """Show error message to user."""
        messagebox.showerror(title, message, parent=self)


class AddTodoDialog(BaseDialog):
    """Dialog for adding new todos."""
    
    def __init__(self, parent):
        self.title_var = tk.StringVar()
        super().__init__(parent, "할일 추가", 450, 180)
    
    def setup_ui(self):
        """Setup the add todo dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title input
        title_label = ttk.Label(main_frame, text="할일 제목:")
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="• 할일 제목을 입력하세요 (1-100자)\n• 특수문자는 자동으로 정리됩니다",
            foreground="gray"
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="추가", command=self.on_ok).pack(side=tk.RIGHT)
    
    def focus_first_input(self):
        """Focus on the title entry."""
        self.title_entry.focus_set()
    
    def validate_input(self) -> bool:
        """Validate the todo title input."""
        title = self.title_var.get().strip()
        
        if not title:
            self.show_error("할일 제목을 입력해주세요.")
            self.title_entry.focus_set()
            return False
        
        if len(title) > 100:
            self.show_error("할일 제목은 100자를 초과할 수 없습니다.")
            self.title_entry.focus_set()
            return False
        
        # Clean up special characters
        cleaned_title = self._clean_title(title)
        if cleaned_title != title:
            self.title_var.set(cleaned_title)
        
        return True
    
    def _clean_title(self, title: str) -> str:
        """Clean up special characters from title."""
        # Remove or replace problematic characters for file system
        forbidden_chars = '<>:"/\\|?*'
        cleaned = title
        for char in forbidden_chars:
            cleaned = cleaned.replace(char, '_')
        
        # Remove multiple spaces and trim
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def get_result(self) -> Optional[str]:
        """Get the cleaned todo title."""
        return self.title_var.get().strip()


class EditTodoDialog(BaseDialog):
    """Dialog for editing existing todos."""
    
    def __init__(self, parent, current_title: str):
        self.current_title = current_title
        self.title_var = tk.StringVar(value=current_title)
        super().__init__(parent, "할일 수정", 450, 180)
    
    def setup_ui(self):
        """Setup the edit todo dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title input
        title_label = ttk.Label(main_frame, text="할일 제목:")
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="• 할일 제목을 수정하세요 (1-100자)\n• 특수문자는 자동으로 정리됩니다",
            foreground="gray"
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="수정", command=self.on_ok).pack(side=tk.RIGHT)
    
    def focus_first_input(self):
        """Focus on the title entry and select all text."""
        self.title_entry.focus_set()
        self.title_entry.select_range(0, tk.END)
    
    def validate_input(self) -> bool:
        """Validate the todo title input."""
        title = self.title_var.get().strip()
        
        if not title:
            self.show_error("할일 제목을 입력해주세요.")
            self.title_entry.focus_set()
            return False
        
        if len(title) > 100:
            self.show_error("할일 제목은 100자를 초과할 수 없습니다.")
            self.title_entry.focus_set()
            return False
        
        # Clean up special characters
        cleaned_title = self._clean_title(title)
        if cleaned_title != title:
            self.title_var.set(cleaned_title)
        
        return True
    
    def _clean_title(self, title: str) -> str:
        """Clean up special characters from title."""
        # Remove or replace problematic characters for file system
        forbidden_chars = '<>:"/\\|?*'
        cleaned = title
        for char in forbidden_chars:
            cleaned = cleaned.replace(char, '_')
        
        # Remove multiple spaces and trim
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def get_result(self) -> Optional[str]:
        """Get the cleaned todo title."""
        new_title = self.title_var.get().strip()
        return new_title if new_title != self.current_title else None


class AddSubtaskDialog(BaseDialog):
    """Dialog for adding subtasks to todos."""
    
    def __init__(self, parent, todo_title: str):
        self.todo_title = todo_title
        self.subtask_var = tk.StringVar()
        super().__init__(parent, "하위작업 추가", 450, 220)
    
    def setup_ui(self):
        """Setup the add subtask dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Todo title display
        todo_label = ttk.Label(main_frame, text="할일:")
        todo_label.pack(anchor=tk.W, pady=(0, 2))
        
        todo_title_label = ttk.Label(
            main_frame, 
            text=self.todo_title, 
            foreground="blue",
            font=("TkDefaultFont", 9, "bold")
        )
        todo_title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Subtask input
        subtask_label = ttk.Label(main_frame, text="하위작업 내용:")
        subtask_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.subtask_entry = ttk.Entry(main_frame, textvariable=self.subtask_var, width=50)
        self.subtask_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="• 하위작업 내용을 입력하세요 (1-200자)\n• 체크박스로 완료 상태를 관리할 수 있습니다",
            foreground="gray"
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="추가", command=self.on_ok).pack(side=tk.RIGHT)
    
    def focus_first_input(self):
        """Focus on the subtask entry."""
        self.subtask_entry.focus_set()
    
    def validate_input(self) -> bool:
        """Validate the subtask input."""
        subtask_title = self.subtask_var.get().strip()
        
        if not subtask_title:
            self.show_error("하위작업 내용을 입력해주세요.")
            self.subtask_entry.focus_set()
            return False
        
        if len(subtask_title) > 200:
            self.show_error("하위작업 내용은 200자를 초과할 수 없습니다.")
            self.subtask_entry.focus_set()
            return False
        
        return True
    
    def get_result(self) -> Optional[str]:
        """Get the subtask title."""
        return self.subtask_var.get().strip()


class ConfirmDialog(BaseDialog):
    """Dialog for confirmation prompts."""
    
    def __init__(self, parent, message: str, title: str = "확인", 
                 ok_text: str = "확인", cancel_text: str = "취소"):
        self.message = message
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        super().__init__(parent, title, 400, 150)
    
    def setup_ui(self):
        """Setup the confirmation dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        message_label = ttk.Label(
            main_frame, 
            text=self.message, 
            wraplength=350,
            justify=tk.CENTER
        )
        message_label.pack(expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text=self.cancel_text, 
            command=self.on_cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text=self.ok_text, 
            command=self.on_ok
        ).pack(side=tk.RIGHT)
    
    def focus_first_input(self):
        """Focus on the OK button."""
        # Find the OK button and focus on it
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for button in child.winfo_children():
                    if isinstance(button, ttk.Button) and button.cget('text') == self.ok_text:
                        button.focus_set()
                        break
    
    def get_result(self) -> bool:
        """Get the confirmation result."""
        return True  # Only returns True if OK was clicked


class DeleteConfirmDialog(ConfirmDialog):
    """Specialized confirmation dialog for delete operations."""
    
    def __init__(self, parent, item_name: str, item_type: str = "할일"):
        message = f"'{item_name}' {item_type}을(를) 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다."
        super().__init__(
            parent, 
            message, 
            title="삭제 확인", 
            ok_text="삭제", 
            cancel_text="취소"
        )


class FolderDeleteConfirmDialog(ConfirmDialog):
    """Specialized confirmation dialog for folder delete operations."""
    
    def __init__(self, parent, todo_title: str):
        message = (f"'{todo_title}' 할일을 삭제합니다.\n\n"
                  f"관련 폴더도 함께 삭제하시겠습니까?\n"
                  f"폴더 안의 모든 파일이 삭제됩니다.")
        super().__init__(
            parent, 
            message, 
            title="폴더 삭제 확인", 
            ok_text="폴더도 삭제", 
            cancel_text="폴더 유지"
        )


class FolderErrorDialog(BaseDialog):
    """Enhanced dialog for folder-related errors with helpful guidance."""
    
    def __init__(self, parent, error_message: str, error_type: str = "폴더 오류", 
                 show_help: bool = True):
        self.error_message = error_message
        self.error_type = error_type
        self.show_help = show_help
        super().__init__(parent, error_type, 500, 300 if show_help else 200)
    
    def setup_ui(self):
        """Setup the folder error dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and message
        error_frame = ttk.Frame(main_frame)
        error_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Error message
        message_label = ttk.Label(
            error_frame, 
            text=self.error_message, 
            wraplength=450,
            justify=tk.LEFT,
            foreground="red"
        )
        message_label.pack(anchor=tk.W)
        
        if self.show_help:
            # Separator
            separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
            separator.pack(fill=tk.X, pady=(10, 15))
            
            # Help section
            help_label = ttk.Label(
                main_frame, 
                text="💡 해결 방법:",
                font=("TkDefaultFont", 9, "bold")
            )
            help_label.pack(anchor=tk.W, pady=(0, 5))
            
            help_text = self._get_help_text()
            help_content = ttk.Label(
                main_frame, 
                text=help_text, 
                wraplength=450,
                justify=tk.LEFT,
                foreground="blue"
            )
            help_content.pack(anchor=tk.W, pady=(0, 15))
        
        # OK button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="확인", 
            command=self.on_ok
        ).pack(side=tk.RIGHT)
    
    def _get_help_text(self) -> str:
        """Get context-specific help text based on error type."""
        if "권한" in self.error_message or "Permission" in self.error_message:
            return ("• 프로그램을 관리자 권한으로 실행해보세요\n"
                   "• 폴더 위치의 권한 설정을 확인해보세요\n"
                   "• 바이러스 백신 프로그램이 차단하고 있는지 확인해보세요")
        elif "공간" in self.error_message or "space" in self.error_message:
            return ("• 디스크 정리를 실행하여 공간을 확보하세요\n"
                   "• 불필요한 파일들을 삭제해보세요\n"
                   "• 다른 드라이브에 프로그램을 설치해보세요")
        elif "경로" in self.error_message or "path" in self.error_message:
            return ("• 할일 제목을 더 짧게 만들어보세요\n"
                   "• 특수문자를 제거해보세요\n"
                   "• 프로그램을 더 짧은 경로에 설치해보세요")
        elif "존재하지 않" in self.error_message:
            return ("• 폴더가 삭제되었을 수 있습니다\n"
                   "• 새로고침을 시도해보세요\n"
                   "• 할일을 다시 생성해보세요")
        elif "xdg-open" in self.error_message:
            return ("• Linux: sudo apt-get install xdg-utils\n"
                   "• 또는 해당 배포판의 패키지 관리자를 사용하세요\n"
                   "• 수동으로 파일 관리자에서 폴더를 열어보세요")
        else:
            return ("• 프로그램을 재시작해보세요\n"
                   "• 시스템을 재부팅해보세요\n"
                   "• 문제가 지속되면 시스템 관리자에게 문의하세요")
    
    def focus_first_input(self):
        """Focus on the OK button."""
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for button in child.winfo_children():
                    if isinstance(button, ttk.Button):
                        button.focus_set()
                        break
    
    def get_result(self) -> bool:
        """Get the dialog result."""
        return True


# Utility functions for showing dialogs
def show_add_todo_dialog(parent) -> Optional[str]:
    """Show add todo dialog and return the title if confirmed."""
    dialog = AddTodoDialog(parent)
    parent.wait_window(dialog)
    return dialog.result


def show_edit_todo_dialog(parent, current_title: str) -> Optional[str]:
    """Show edit todo dialog and return the new title if changed."""
    dialog = EditTodoDialog(parent, current_title)
    parent.wait_window(dialog)
    return dialog.result


def show_add_subtask_dialog(parent, todo_title: str) -> Optional[str]:
    """Show add subtask dialog and return the subtask title if confirmed."""
    dialog = AddSubtaskDialog(parent, todo_title)
    parent.wait_window(dialog)
    return dialog.result


def show_delete_confirm_dialog(parent, item_name: str, item_type: str = "할일") -> bool:
    """Show delete confirmation dialog and return True if confirmed."""
    dialog = DeleteConfirmDialog(parent, item_name, item_type)
    parent.wait_window(dialog)
    return dialog.result is True


def show_folder_delete_confirm_dialog(parent, todo_title: str) -> bool:
    """Show folder delete confirmation dialog and return True if confirmed."""
    dialog = FolderDeleteConfirmDialog(parent, todo_title)
    parent.wait_window(dialog)
    return dialog.result is True


def show_error_dialog(parent, message: str, title: str = "오류"):
    """Show error message dialog."""
    messagebox.showerror(title, message, parent=parent)


def show_info_dialog(parent, message: str, title: str = "정보"):
    """Show information message dialog."""
    messagebox.showinfo(title, message, parent=parent)


def show_warning_dialog(parent, message: str, title: str = "경고"):
    """Show warning message dialog."""
    messagebox.showwarning(title, message, parent=parent)


def show_folder_error_dialog(parent, error_message: str, error_type: str = "폴더 오류", show_help: bool = True):
    """Show enhanced folder error dialog with helpful guidance."""
    dialog = FolderErrorDialog(parent, error_message, error_type, show_help)
    parent.wait_window(dialog)
    return dialog.result