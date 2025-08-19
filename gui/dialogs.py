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
from datetime import datetime, timedelta
import calendar
from services.date_service import DateService


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
        self.has_due_date_var = tk.BooleanVar(value=False)
        self.due_date = None
        super().__init__(parent, "할일 추가", 500, 320)
    
    def setup_ui(self):
        """Setup the add todo dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title input
        title_label = ttk.Label(main_frame, text="할일 제목:")
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Due date section
        self.setup_due_date_section(main_frame)
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="• 할일 제목을 입력하세요 (1-100자)\n• 특수문자는 자동으로 정리됩니다\n• 목표 날짜는 선택사항입니다",
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
    
    def setup_due_date_section(self, parent):
        """Setup the due date selection section."""
        # Due date frame
        due_date_frame = ttk.LabelFrame(parent, text="목표 날짜", padding="10")
        due_date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Due date checkbox
        self.due_date_checkbox = ttk.Checkbutton(
            due_date_frame,
            text="목표 날짜 설정",
            variable=self.has_due_date_var,
            command=self.on_due_date_toggle
        )
        self.due_date_checkbox.pack(anchor=tk.W, pady=(0, 10))
        
        # Simple date/time inputs
        datetime_frame = ttk.Frame(due_date_frame)
        datetime_frame.pack(fill=tk.X)
        
        # Date input
        date_frame = ttk.Frame(datetime_frame)
        date_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(date_frame, text="날짜:").pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Time input
        time_frame = ttk.Frame(datetime_frame)
        time_frame.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="시간:").pack(side=tk.LEFT)
        self.hour_var = tk.StringVar(value="18")
        self.minute_var = tk.StringVar(value="00")
        
        self.hour_spinbox = ttk.Spinbox(time_frame, textvariable=self.hour_var,
                                       from_=0, to=23, width=3, format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=(5, 2))
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        self.minute_spinbox = ttk.Spinbox(time_frame, textvariable=self.minute_var,
                                         from_=0, to=59, width=3, format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT, padx=(2, 0))
        
        # Store widgets for state management
        self.datetime_widgets = [self.date_entry, self.hour_spinbox, self.minute_spinbox]
        
        # Initially disable the datetime widgets
        self.update_due_date_state()
    
    def on_due_date_toggle(self):
        """Handle due date checkbox toggle."""
        self.update_due_date_state()
    
    def update_due_date_state(self):
        """Update the state of due date widgets."""
        enabled = self.has_due_date_var.get()
        state = "normal" if enabled else "disabled"
        
        # Update datetime widgets state
        for widget in self.datetime_widgets:
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(state=state)
                except tk.TclError:
                    pass
    
    def get_datetime_from_inputs(self):
        """Get datetime from input widgets."""
        try:
            date_str = self.date_var.get()
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.replace(hour=hour, minute=minute)
        except (ValueError, TypeError):
            return None
    
    def get_result(self) -> Optional[dict]:
        """Get the dialog result with title and due date."""
        title = self.title_var.get().strip()
        due_date = None
        
        if self.has_due_date_var.get():
            due_date = self.get_datetime_from_inputs()
        
        return {
            'title': title,
            'due_date': due_date
        }


class EditTodoDialog(BaseDialog):
    """Dialog for editing existing todos."""
    
    def __init__(self, parent, current_title: str, current_due_date: Optional[datetime] = None):
        self.current_title = current_title
        self.current_due_date = current_due_date
        self.title_var = tk.StringVar(value=current_title)
        self.has_due_date_var = tk.BooleanVar(value=current_due_date is not None)
        self.due_date = current_due_date
        super().__init__(parent, "할일 수정", 500, 320)
    
    def setup_ui(self):
        """Setup the edit todo dialog UI."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title input
        title_label = ttk.Label(main_frame, text="할일 제목:")
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Due date section
        self.setup_due_date_section(main_frame)
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="• 할일 제목을 수정하세요 (1-100자)\n• 특수문자는 자동으로 정리됩니다\n• 목표 날짜는 선택사항입니다",
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
    
    def setup_due_date_section(self, parent):
        """Setup the due date selection section."""
        # Due date frame
        due_date_frame = ttk.LabelFrame(parent, text="목표 날짜", padding="10")
        due_date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Due date checkbox
        self.due_date_checkbox = ttk.Checkbutton(
            due_date_frame,
            text="목표 날짜 설정",
            variable=self.has_due_date_var,
            command=self.on_due_date_toggle
        )
        self.due_date_checkbox.pack(anchor=tk.W, pady=(0, 10))
        
        # Date/time widget
        self.datetime_widget = DateTimeWidget(due_date_frame, self.current_due_date)
        self.datetime_widget.pack(fill=tk.X)
        
        # Update initial state
        self.update_due_date_state()
    
    def on_due_date_toggle(self):
        """Handle due date checkbox toggle."""
        self.update_due_date_state()
    
    def update_due_date_state(self):
        """Update the state of due date widgets."""
        enabled = self.has_due_date_var.get()
        state = "normal" if enabled else "disabled"
        
        # Update datetime widget state
        for child in self.datetime_widget.winfo_children():
            if hasattr(child, 'configure'):
                try:
                    child.configure(state=state)
                except tk.TclError:
                    pass
            # Handle nested frames
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if hasattr(grandchild, 'configure'):
                        try:
                            grandchild.configure(state=state)
                        except tk.TclError:
                            pass
    
    def get_result(self) -> Optional[dict]:
        """Get the dialog result with title and due date changes."""
        new_title = self.title_var.get().strip()
        new_due_date = None
        
        if self.has_due_date_var.get():
            new_due_date = self.datetime_widget.get_datetime()
        
        # Check if anything changed
        title_changed = new_title != self.current_title
        due_date_changed = new_due_date != self.current_due_date
        
        if not title_changed and not due_date_changed:
            return None
        
        return {
            'title': new_title if title_changed else None,
            'due_date': new_due_date,
            'due_date_changed': due_date_changed
        }


class AddSubtaskDialog(BaseDialog):
    """Dialog for adding subtasks to todos."""
    
    def __init__(self, parent, todo_title: str, parent_due_date: Optional[datetime] = None):
        self.todo_title = todo_title
        self.parent_due_date = parent_due_date
        self.subtask_var = tk.StringVar()
        self.has_due_date_var = tk.BooleanVar(value=False)
        self.due_date = None
        super().__init__(parent, "하위작업 추가", 500, 380)
    
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
        todo_title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Parent due date display if exists
        if self.parent_due_date:
            parent_due_label = ttk.Label(
                main_frame,
                text=f"상위 할일 목표 날짜: {DateService.format_due_date(self.parent_due_date, 'absolute')}",
                foreground="gray",
                font=("TkDefaultFont", 8)
            )
            parent_due_label.pack(anchor=tk.W, pady=(0, 15))
        else:
            # Add some spacing
            ttk.Label(main_frame, text="").pack(pady=(0, 5))
        
        # Subtask input
        subtask_label = ttk.Label(main_frame, text="하위작업 내용:")
        subtask_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.subtask_entry = ttk.Entry(main_frame, textvariable=self.subtask_var, width=50)
        self.subtask_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Due date section
        self.setup_due_date_section(main_frame)
        
        # Warning label for due date validation
        self.warning_label = ttk.Label(main_frame, text="", foreground="red")
        self.warning_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="• 하위작업 내용을 입력하세요 (1-200자)\n• 체크박스로 완료 상태를 관리할 수 있습니다\n• 하위작업 목표 날짜는 상위 할일보다 늦을 수 없습니다",
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
    
    def setup_due_date_section(self, parent):
        """Setup the due date selection section."""
        # Due date frame
        due_date_frame = ttk.LabelFrame(parent, text="목표 날짜", padding="10")
        due_date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Due date checkbox
        self.due_date_checkbox = ttk.Checkbutton(
            due_date_frame,
            text="목표 날짜 설정",
            variable=self.has_due_date_var,
            command=self.on_due_date_toggle
        )
        self.due_date_checkbox.pack(anchor=tk.W, pady=(0, 10))
        
        # Date/time widget
        self.datetime_widget = DateTimeWidget(due_date_frame)
        self.datetime_widget.pack(fill=tk.X)
        
        # Initially disable the datetime widget
        self.update_due_date_state()
    
    def on_due_date_toggle(self):
        """Handle due date checkbox toggle."""
        self.update_due_date_state()
        self.validate_due_date()
    
    def update_due_date_state(self):
        """Update the state of due date widgets."""
        enabled = self.has_due_date_var.get()
        state = "normal" if enabled else "disabled"
        
        # Update datetime widget state
        for child in self.datetime_widget.winfo_children():
            if hasattr(child, 'configure'):
                try:
                    child.configure(state=state)
                except tk.TclError:
                    pass
            # Handle nested frames
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if hasattr(grandchild, 'configure'):
                        try:
                            grandchild.configure(state=state)
                        except tk.TclError:
                            pass
    
    def validate_due_date(self):
        """Validate subtask due date against parent due date."""
        self.warning_label.config(text="")
        
        if not self.has_due_date_var.get() or not self.parent_due_date:
            return True
        
        subtask_due_date = self.datetime_widget.get_datetime()
        if subtask_due_date and subtask_due_date > self.parent_due_date:
            warning_text = f"경고: 하위작업 목표 날짜가 상위 할일 목표 날짜({DateService.format_due_date(self.parent_due_date, 'absolute')})보다 늦습니다."
            self.warning_label.config(text=warning_text)
            return False
        
        return True
    
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
        
        # Validate due date if set
        if self.has_due_date_var.get() and self.parent_due_date:
            subtask_due_date = self.datetime_widget.get_datetime()
            if subtask_due_date and subtask_due_date > self.parent_due_date:
                self.show_error("하위작업의 목표 날짜는 상위 할일의 목표 날짜보다 늦을 수 없습니다.")
                return False
        
        return True
    
    def get_result(self) -> Optional[dict]:
        """Get the dialog result with subtask title and due date."""
        title = self.subtask_var.get().strip()
        due_date = None
        
        if self.has_due_date_var.get():
            due_date = self.datetime_widget.get_datetime()
        
        return {
            'title': title,
            'due_date': due_date
        }


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


class DueDateDialog(BaseDialog):
    """목표 날짜 설정을 위한 다이얼로그"""
    
    def __init__(self, parent, current_due_date: Optional[datetime] = None,
                 parent_due_date: Optional[datetime] = None,
                 item_type: str = "할일"):
        self.current_due_date = current_due_date
        self.parent_due_date = parent_due_date
        self.item_type = item_type
        
        # 날짜/시간 변수들
        self.has_due_date_var = tk.BooleanVar(value=current_due_date is not None)
        self.selected_date = current_due_date or datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        
        # UI 컴포넌트 참조
        self.calendar_frame = None
        self.time_frame = None
        self.hour_spinbox = None
        self.minute_spinbox = None
        self.warning_label = None
        
        super().__init__(parent, f"{item_type} 목표 날짜 설정", 600, 500)
        
        # 스타일 설정
        self.setup_styles()
    
    def setup_styles(self):
        """달력 버튼 스타일 설정"""
        style = ttk.Style()
        
        # 선택된 날짜 스타일
        style.configure("Selected.TButton", 
                       background="blue", 
                       foreground="white",
                       font=("TkDefaultFont", 9, "bold"))
        
        # 오늘 날짜 스타일
        style.configure("Today.TButton", 
                       background="lightblue", 
                       foreground="black",
                       font=("TkDefaultFont", 9, "bold"))
        
        # 과거 날짜 스타일
        style.configure("Past.TButton", 
                       foreground="gray")
    
    def setup_ui(self):
        """목표 날짜 설정 UI 구성"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 목표 날짜 사용 여부 체크박스
        self.setup_due_date_checkbox(main_frame)
        
        # 빠른 선택 버튼들
        self.setup_quick_buttons(main_frame)
        
        # 달력과 시간 선택 프레임
        datetime_frame = ttk.Frame(main_frame)
        datetime_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 달력 위젯
        self.setup_calendar(datetime_frame)
        
        # 시간 선택 위젯
        self.setup_time_selection(datetime_frame)
        
        # 현재 설정 표시
        self.setup_current_setting_display(main_frame)
        
        # 경고 메시지 레이블
        self.setup_warning_label(main_frame)
        
        # 버튼들
        self.setup_buttons(main_frame)
        
        # 초기 상태 업데이트
        self.update_ui_state()
    
    def setup_due_date_checkbox(self, parent):
        """목표 날짜 사용 여부 체크박스 설정"""
        checkbox_frame = ttk.Frame(parent)
        checkbox_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.due_date_checkbox = ttk.Checkbutton(
            checkbox_frame,
            text=f"{self.item_type}에 목표 날짜 설정",
            variable=self.has_due_date_var,
            command=self.on_due_date_toggle
        )
        self.due_date_checkbox.pack(anchor=tk.W)
    
    def setup_quick_buttons(self, parent):
        """빠른 날짜 선택 버튼들 설정"""
        quick_frame = ttk.LabelFrame(parent, text="빠른 선택", padding="10")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 버튼들을 2행으로 배치
        button_frame1 = ttk.Frame(quick_frame)
        button_frame1.pack(fill=tk.X, pady=(0, 5))
        
        button_frame2 = ttk.Frame(quick_frame)
        button_frame2.pack(fill=tk.X)
        
        quick_options = DateService.get_quick_date_options()
        
        # 첫 번째 행 버튼들
        first_row = ["오늘", "내일", "모레", "이번 주말"]
        for option in first_row:
            if option in quick_options:
                btn = ttk.Button(
                    button_frame1,
                    text=option,
                    command=lambda opt=option: self.set_quick_date(opt)
                )
                btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 두 번째 행 버튼들
        second_row = ["다음 주", "1주일 후", "2주일 후", "1개월 후"]
        for option in second_row:
            if option in quick_options:
                btn = ttk.Button(
                    button_frame2,
                    text=option,
                    command=lambda opt=option: self.set_quick_date(opt)
                )
                btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 목표 날짜 제거 버튼
        remove_btn = ttk.Button(
            button_frame2,
            text="목표 날짜 제거",
            command=self.remove_due_date
        )
        remove_btn.pack(side=tk.RIGHT)
    
    def setup_calendar(self, parent):
        """달력 위젯 설정"""
        self.calendar_frame = ttk.LabelFrame(parent, text="날짜 선택", padding="10")
        self.calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 월/년 선택
        nav_frame = ttk.Frame(self.calendar_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 이전 달 버튼
        ttk.Button(nav_frame, text="◀", width=3, command=self.prev_month).pack(side=tk.LEFT)
        
        # 월/년 표시
        self.month_year_var = tk.StringVar()
        self.month_year_label = ttk.Label(nav_frame, textvariable=self.month_year_var, font=("TkDefaultFont", 10, "bold"))
        self.month_year_label.pack(side=tk.LEFT, expand=True)
        
        # 다음 달 버튼
        ttk.Button(nav_frame, text="▶", width=3, command=self.next_month).pack(side=tk.RIGHT)
        
        # 달력 그리드
        self.calendar_grid_frame = ttk.Frame(self.calendar_frame)
        self.calendar_grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # 요일 헤더
        days = ['월', '화', '수', '목', '금', '토', '일']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_grid_frame, text=day, font=("TkDefaultFont", 9, "bold"))
            label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
        
        # 달력 버튼들을 저장할 리스트
        self.calendar_buttons = []
        
        # 그리드 가중치 설정
        for i in range(7):
            self.calendar_grid_frame.columnconfigure(i, weight=1)
        for i in range(7):  # 헤더 + 최대 6주
            self.calendar_grid_frame.rowconfigure(i, weight=1)
        
        self.current_calendar_date = self.selected_date.replace(day=1)
        self.update_calendar()
    
    def setup_time_selection(self, parent):
        """시간 선택 위젯 설정"""
        self.time_frame = ttk.LabelFrame(parent, text="시간 선택", padding="10")
        self.time_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 시간 선택
        hour_frame = ttk.Frame(self.time_frame)
        hour_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(hour_frame, text="시:").pack(side=tk.LEFT)
        self.hour_spinbox = ttk.Spinbox(
            hour_frame,
            from_=0, to=23,
            width=5,
            format="%02.0f",
            command=self.on_time_change
        )
        self.hour_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        self.hour_spinbox.set(f"{self.selected_date.hour:02d}")
        
        # 분 선택
        minute_frame = ttk.Frame(self.time_frame)
        minute_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(minute_frame, text="분:").pack(side=tk.LEFT)
        self.minute_spinbox = ttk.Spinbox(
            minute_frame,
            from_=0, to=59,
            width=5,
            format="%02.0f",
            command=self.on_time_change
        )
        self.minute_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        self.minute_spinbox.set(f"{self.selected_date.minute:02d}")
        
        # 시간 바인딩
        self.hour_spinbox.bind('<KeyRelease>', lambda e: self.on_time_change())
        self.minute_spinbox.bind('<KeyRelease>', lambda e: self.on_time_change())
        
        # 빠른 시간 선택 버튼들
        quick_time_frame = ttk.Frame(self.time_frame)
        quick_time_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quick_time_frame, text="빠른 시간:").pack(anchor=tk.W, pady=(0, 5))
        
        time_buttons = [
            ("09:00", 9, 0),
            ("12:00", 12, 0),
            ("18:00", 18, 0),
            ("21:00", 21, 0)
        ]
        
        for text, hour, minute in time_buttons:
            btn = ttk.Button(
                quick_time_frame,
                text=text,
                width=8,
                command=lambda h=hour, m=minute: self.set_time(h, m)
            )
            btn.pack(fill=tk.X, pady=1)
    
    def setup_current_setting_display(self, parent):
        """현재 설정된 날짜 표시"""
        current_frame = ttk.LabelFrame(parent, text="현재 설정", padding="10")
        current_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.current_setting_var = tk.StringVar()
        self.current_setting_label = ttk.Label(
            current_frame,
            textvariable=self.current_setting_var,
            font=("TkDefaultFont", 10, "bold"),
            foreground="blue"
        )
        self.current_setting_label.pack()
        
        self.update_current_setting_display()
    
    def setup_warning_label(self, parent):
        """경고 메시지 레이블 설정"""
        self.warning_label = ttk.Label(
            parent,
            text="",
            foreground="red",
            font=("TkDefaultFont", 9)
        )
        self.warning_label.pack(fill=tk.X, pady=(5, 0))
    
    def setup_buttons(self, parent):
        """버튼들 설정"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="취소", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="확인", command=self.on_ok).pack(side=tk.RIGHT)
    
    def update_calendar(self):
        """달력 표시 업데이트"""
        # 기존 버튼들 제거
        for btn in self.calendar_buttons:
            btn.destroy()
        self.calendar_buttons.clear()
        
        # 월/년 표시 업데이트
        self.month_year_var.set(f"{self.current_calendar_date.year}년 {self.current_calendar_date.month}월")
        
        # 달력 데이터 생성
        cal = calendar.monthcalendar(self.current_calendar_date.year, self.current_calendar_date.month)
        
        # 달력 버튼들 생성
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # 빈 날짜
                    label = ttk.Label(self.calendar_grid_frame, text="")
                    label.grid(row=week_num + 1, column=day_num, padx=1, pady=1, sticky="nsew")
                    self.calendar_buttons.append(label)
                else:
                    # 날짜 버튼
                    date_obj = datetime(self.current_calendar_date.year, self.current_calendar_date.month, day)
                    
                    # 오늘 날짜인지 확인
                    is_today = date_obj.date() == datetime.now().date()
                    
                    # 선택된 날짜인지 확인
                    is_selected = (date_obj.date() == self.selected_date.date() and 
                                 self.has_due_date_var.get())
                    
                    # 과거 날짜인지 확인
                    is_past = date_obj.date() < datetime.now().date()
                    
                    btn = ttk.Button(
                        self.calendar_grid_frame,
                        text=str(day),
                        width=4,
                        command=lambda d=day: self.select_date(d)
                    )
                    
                    # 스타일 적용
                    if is_selected:
                        btn.configure(style="Selected.TButton")
                    elif is_today:
                        btn.configure(style="Today.TButton")
                    elif is_past:
                        btn.configure(style="Past.TButton")
                    
                    btn.grid(row=week_num + 1, column=day_num, padx=1, pady=1, sticky="nsew")
                    self.calendar_buttons.append(btn)
    
    def prev_month(self):
        """이전 달로 이동"""
        if self.current_calendar_date.month == 1:
            self.current_calendar_date = self.current_calendar_date.replace(year=self.current_calendar_date.year - 1, month=12)
        else:
            self.current_calendar_date = self.current_calendar_date.replace(month=self.current_calendar_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """다음 달로 이동"""
        if self.current_calendar_date.month == 12:
            self.current_calendar_date = self.current_calendar_date.replace(year=self.current_calendar_date.year + 1, month=1)
        else:
            self.current_calendar_date = self.current_calendar_date.replace(month=self.current_calendar_date.month + 1)
        self.update_calendar()
    
    def select_date(self, day):
        """날짜 선택"""
        if not self.has_due_date_var.get():
            self.has_due_date_var.set(True)
            self.update_ui_state()
        
        # 선택된 날짜 업데이트 (시간은 유지)
        self.selected_date = self.selected_date.replace(
            year=self.current_calendar_date.year,
            month=self.current_calendar_date.month,
            day=day
        )
        
        self.update_calendar()
        self.update_current_setting_display()
        self.validate_and_show_warnings()
    
    def set_time(self, hour, minute):
        """시간 설정"""
        self.hour_spinbox.set(f"{hour:02d}")
        self.minute_spinbox.set(f"{minute:02d}")
        self.on_time_change()
    
    def on_time_change(self):
        """시간 변경 이벤트"""
        try:
            hour = int(self.hour_spinbox.get())
            minute = int(self.minute_spinbox.get())
            
            # 유효한 시간인지 확인
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                self.selected_date = self.selected_date.replace(hour=hour, minute=minute)
                self.update_current_setting_display()
                self.validate_and_show_warnings()
        except ValueError:
            pass  # 잘못된 입력은 무시
    
    def set_quick_date(self, option):
        """빠른 날짜 선택"""
        quick_options = DateService.get_quick_date_options()
        if option in quick_options:
            self.has_due_date_var.set(True)
            self.selected_date = quick_options[option]
            
            # 달력을 해당 월로 이동
            self.current_calendar_date = self.selected_date.replace(day=1)
            
            # UI 업데이트
            self.update_ui_state()
            self.update_calendar()
            self.hour_spinbox.set(f"{self.selected_date.hour:02d}")
            self.minute_spinbox.set(f"{self.selected_date.minute:02d}")
            self.update_current_setting_display()
            self.validate_and_show_warnings()
    
    def remove_due_date(self):
        """목표 날짜 제거"""
        self.has_due_date_var.set(False)
        self.update_ui_state()
        self.update_current_setting_display()
        self.clear_warnings()
    
    def on_due_date_toggle(self):
        """목표 날짜 사용 여부 토글"""
        self.update_ui_state()
        self.update_current_setting_display()
        if self.has_due_date_var.get():
            self.validate_and_show_warnings()
        else:
            self.clear_warnings()
    
    def update_ui_state(self):
        """UI 상태 업데이트"""
        enabled = self.has_due_date_var.get()
        
        # 달력과 시간 선택 위젯 활성화/비활성화
        state = "normal" if enabled else "disabled"
        
        if self.calendar_frame:
            for child in self.calendar_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if hasattr(grandchild, 'configure'):
                            try:
                                grandchild.configure(state=state)
                            except tk.TclError:
                                pass
        
        if self.time_frame:
            for child in self.time_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if hasattr(grandchild, 'configure'):
                            try:
                                grandchild.configure(state=state)
                            except tk.TclError:
                                pass
        
        # 달력 버튼들 상태 변경
        for btn in self.calendar_buttons:
            if isinstance(btn, ttk.Button):
                try:
                    btn.configure(state=state)
                except tk.TclError:
                    pass
        
        self.update_calendar()
    
    def update_current_setting_display(self):
        """현재 설정 표시 업데이트"""
        if not self.has_due_date_var.get():
            self.current_setting_var.set("목표 날짜 없음")
        else:
            formatted_date = DateService.format_due_date(self.selected_date, 'relative')
            urgency_text = DateService.get_time_remaining_text(self.selected_date)
            if urgency_text:
                self.current_setting_var.set(f"{formatted_date} ({urgency_text})")
            else:
                self.current_setting_var.set(formatted_date)
    
    def validate_and_show_warnings(self):
        """유효성 검사 및 경고 메시지 표시"""
        if not self.has_due_date_var.get():
            self.clear_warnings()
            return
        
        is_valid, error_message = DateService.validate_due_date(self.selected_date, self.parent_due_date)
        
        if not is_valid:
            self.warning_label.configure(text=f"⚠️ {error_message}")
        else:
            # 과거 날짜 경고 (1시간 이내는 허용하지만 경고)
            now = datetime.now()
            if self.selected_date < now:
                time_diff = now - self.selected_date
                if time_diff.total_seconds() < 3600:  # 1시간 이내
                    self.warning_label.configure(text="⚠️ 목표 날짜가 현재 시간보다 이전입니다.")
                else:
                    self.warning_label.configure(text="")
            else:
                self.warning_label.configure(text="")
    
    def clear_warnings(self):
        """경고 메시지 제거"""
        self.warning_label.configure(text="")
    
    def focus_first_input(self):
        """첫 번째 입력 필드에 포커스"""
        self.due_date_checkbox.focus_set()
    
    def validate_input(self) -> bool:
        """입력 유효성 검사
        
        Requirements: 오류 메시지 및 사용자 가이드 개선
        """
        if not self.has_due_date_var.get():
            return True  # 목표 날짜 없음은 유효
        
        # 선택된 날짜가 유효한지 확인
        if self.selected_date is None:
            self.show_error(
                "올바른 날짜를 선택해주세요.\n\n" +
                "도움말:\n" +
                "• 달력에서 날짜를 클릭하거나\n" +
                "• 빠른 선택 버튼을 사용하거나\n" +
                "• 직접 날짜를 입력하세요"
            )
            return False
        
        is_valid, error_message = DateService.validate_due_date(self.selected_date, self.parent_due_date)
        
        if not is_valid:
            # 더 자세한 오류 메시지 제공
            enhanced_message = error_message
            if self.parent_due_date:
                enhanced_message += f"\n\n상위 할일 목표 날짜: {DateService.format_due_date(self.parent_due_date, 'absolute')}"
                enhanced_message += f"\n선택한 날짜: {DateService.format_due_date(self.selected_date, 'absolute')}"
                enhanced_message += "\n\n하위작업의 목표 날짜는 상위 할일보다 이르거나 같아야 합니다."
            
            self.show_error(enhanced_message)
            return False
        
        # 과거 날짜에 대한 확인 (1시간 이전까지는 허용)
        now = datetime.now()
        if self.selected_date < now - timedelta(hours=1):
            from tkinter import messagebox
            
            time_diff = now - self.selected_date
            if time_diff.days > 0:
                time_desc = f"{time_diff.days}일 전"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_desc = f"{hours}시간 전"
            else:
                minutes = time_diff.seconds // 60
                time_desc = f"{minutes}분 전"
            
            result = messagebox.askyesno(
                "과거 날짜 확인",
                f"목표 날짜가 과거입니다 ({time_desc}).\n\n"
                f"설정하려는 날짜: {DateService.format_due_date(self.selected_date, 'absolute')}\n"
                f"현재 시간: {DateService.format_due_date(now, 'absolute')}\n\n"
                f"과거 날짜로 설정하면 즉시 '지연됨' 상태가 됩니다.\n"
                f"그래도 설정하시겠습니까?\n\n"
                f"권장: 미래 날짜를 선택하세요.",
                parent=self
            )
            if not result:
                return False
        
        # 너무 먼 미래 날짜 경고 (1년 이후)
        elif self.selected_date > now + timedelta(days=365):
            from tkinter import messagebox
            result = messagebox.askyesno(
                "먼 미래 날짜 확인",
                f"목표 날짜가 1년 이후입니다.\n\n"
                f"설정하려는 날짜: {DateService.format_due_date(self.selected_date, 'absolute')}\n\n"
                f"정말로 이 날짜로 설정하시겠습니까?",
                parent=self
            )
            if not result:
                return False
        
        return True
    
    def get_result(self) -> Optional[datetime]:
        """선택된 목표 날짜 반환"""
        if self.has_due_date_var.get():
            return self.selected_date
        else:
            return None


class StartupNotificationDialog(BaseDialog):
    """시작 시 알림 다이얼로그"""
    
    def __init__(self, parent, overdue_count: int, due_today_count: int):
        self.overdue_count = overdue_count
        self.due_today_count = due_today_count
        self.dont_show_again_var = tk.BooleanVar()
        super().__init__(parent, "할일 알림", 400, 250)
    
    def setup_ui(self):
        """알림 다이얼로그 UI 구성"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 알림 아이콘과 제목
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 아이콘 (이모지 사용)
        icon_label = ttk.Label(header_frame, text="⏰", font=("TkDefaultFont", 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 제목
        title_label = ttk.Label(
            header_frame, 
            text="할일 알림", 
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # 알림 내용
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        if self.overdue_count > 0:
            overdue_label = ttk.Label(
                content_frame,
                text=f"🔴 지연된 할일: {self.overdue_count}개",
                font=("TkDefaultFont", 11),
                foreground="red"
            )
            overdue_label.pack(anchor=tk.W, pady=(0, 5))
        
        if self.due_today_count > 0:
            today_label = ttk.Label(
                content_frame,
                text=f"🟡 오늘 마감 할일: {self.due_today_count}개",
                font=("TkDefaultFont", 11),
                foreground="orange"
            )
            today_label.pack(anchor=tk.W, pady=(0, 5))
        
        if self.overdue_count == 0 and self.due_today_count == 0:
            no_urgent_label = ttk.Label(
                content_frame,
                text="🟢 긴급한 할일이 없습니다.",
                font=("TkDefaultFont", 11),
                foreground="green"
            )
            no_urgent_label.pack(anchor=tk.W)
        
        # "다시 보지 않기" 체크박스
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.pack(fill=tk.X, pady=(10, 0))
        
        dont_show_checkbox = ttk.Checkbutton(
            checkbox_frame,
            text="다시 보지 않기",
            variable=self.dont_show_again_var
        )
        dont_show_checkbox.pack(anchor=tk.W)
        
        # 확인 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="확인", command=self.on_ok).pack(side=tk.RIGHT)
    
    def focus_first_input(self):
        """확인 버튼에 포커스"""
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for frame in child.winfo_children():
                    if isinstance(frame, ttk.Frame):
                        for button in frame.winfo_children():
                            if isinstance(button, ttk.Button) and button.cget('text') == "확인":
                                button.focus_set()
                                return
    
    def get_result(self) -> dict:
        """알림 결과 반환"""
        return {
            'confirmed': True,
            'dont_show_again': self.dont_show_again_var.get()
        }


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
    result = dialog.result
    if result and isinstance(result, dict):
        return result.get('title')
    return result


def show_add_todo_dialog_with_due_date(parent) -> Optional[dict]:
    """Show add todo dialog and return the full result with title and due date."""
    dialog = AddTodoDialog(parent)
    parent.wait_window(dialog)
    return dialog.result


def show_edit_todo_dialog(parent, current_title: str) -> Optional[str]:
    """Show edit todo dialog and return the new title if changed."""
    dialog = EditTodoDialog(parent, current_title)
    parent.wait_window(dialog)
    result = dialog.result
    if result and isinstance(result, dict):
        return result.get('title')
    return result


def show_edit_todo_dialog_with_due_date(parent, current_title: str, current_due_date: Optional[datetime] = None) -> Optional[dict]:
    """Show edit todo dialog and return the full result with title and due date changes."""
    dialog = EditTodoDialog(parent, current_title, current_due_date)
    parent.wait_window(dialog)
    return dialog.result


def show_add_subtask_dialog(parent, todo_title: str) -> Optional[str]:
    """Show add subtask dialog and return the subtask title if confirmed."""
    dialog = AddSubtaskDialog(parent, todo_title)
    parent.wait_window(dialog)
    result = dialog.result
    if result and isinstance(result, dict):
        return result.get('title')
    return result


def show_add_subtask_dialog_with_due_date(parent, todo_title: str, parent_due_date: Optional[datetime] = None) -> Optional[dict]:
    """Show add subtask dialog and return the full result with title and due date."""
    dialog = AddSubtaskDialog(parent, todo_title, parent_due_date)
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
    """Show error message dialog with enhanced user guidance.
    
    Requirements: 오류 메시지 및 사용자 가이드 개선
    """
    # 일반적인 오류에 대한 도움말 추가
    enhanced_message = message
    
    # 파일 관련 오류
    if "파일" in message or "폴더" in message:
        enhanced_message += "\n\n도움말:\n• 파일이 다른 프로그램에서 사용 중인지 확인하세요\n• 충분한 디스크 공간이 있는지 확인하세요\n• 관리자 권한이 필요할 수 있습니다"
    
    # 날짜 관련 오류
    elif "날짜" in message or "시간" in message:
        enhanced_message += "\n\n도움말:\n• 올바른 날짜 형식을 사용하세요 (YYYY-MM-DD)\n• 유효한 날짜인지 확인하세요\n• 빠른 선택 버튼을 사용해보세요"
    
    # 네트워크 관련 오류
    elif "연결" in message or "네트워크" in message:
        enhanced_message += "\n\n도움말:\n• 인터넷 연결을 확인하세요\n• 방화벽 설정을 확인하세요\n• 잠시 후 다시 시도해보세요"
    
    # 일반적인 해결 방법 제안
    if "예상치 못한" in message or "알 수 없는" in message:
        enhanced_message += "\n\n해결 방법:\n• 프로그램을 다시 시작해보세요\n• 데이터를 백업하고 복원해보세요\n• F1 키를 눌러 도움말을 확인하세요"
    
    messagebox.showerror(title, enhanced_message, parent=parent)


def show_info_dialog(parent, message: str, title: str = "정보"):
    """Show information message dialog with enhanced formatting.
    
    Requirements: 사용자 가이드 개선
    """
    messagebox.showinfo(title, message, parent=parent)


def show_warning_dialog(parent, message: str, title: str = "경고"):
    """Show warning message dialog with enhanced user guidance.
    
    Requirements: 오류 메시지 및 사용자 가이드 개선
    """
    # 경고에 대한 추가 안내 제공
    enhanced_message = message
    
    if "삭제" in message:
        enhanced_message += "\n\n주의: 이 작업은 되돌릴 수 없습니다."
    elif "저장" in message:
        enhanced_message += "\n\n권장: 중요한 데이터는 미리 백업하세요."
    
    messagebox.showwarning(title, enhanced_message, parent=parent)


def show_folder_error_dialog(parent, error_message: str, error_type: str = "폴더 오류", show_help: bool = True):
    """Show enhanced folder error dialog with helpful guidance."""
    dialog = FolderErrorDialog(parent, error_message, error_type, show_help)
    parent.wait_window(dialog)
    return dialog.result


def show_due_date_dialog(parent, current_due_date: Optional[datetime] = None,
                        parent_due_date: Optional[datetime] = None,
                        item_type: str = "할일") -> Optional[datetime]:
    """Show due date setting dialog and return the selected date if confirmed."""
    dialog = DueDateDialog(parent, current_due_date, parent_due_date, item_type)
    parent.wait_window(dialog)
    return dialog.result


def show_startup_notification_dialog(parent, overdue_count: int, due_today_count: int) -> dict:
    """Show startup notification dialog and return the result."""
    dialog = StartupNotificationDialog(parent, overdue_count, due_today_count)
    parent.wait_window(dialog)
    return dialog.result or {'confirmed': False, 'dont_show_again': False}