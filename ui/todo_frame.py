
import tkinter as tk
from tkinter import messagebox
from services.todo_service import TodoService

class TodoFrame(tk.Frame):
    """
    투두리스트 UI를 구성하는 프레임
    """
    def __init__(self, master, todo_service: TodoService, **kwargs):
        super().__init__(master, **kwargs)
        self.todo_service = todo_service

        self._create_widgets()
        self.refresh_todos()

    def _create_widgets(self):
        """UI 위젯들을 생성하고 배치합니다."""
        # 프레임 설정
        self.config(padx=10, pady=10)
        
        # 입력 프레임
        input_frame = tk.Frame(self)
        input_frame.pack(fill=tk.X, pady=5)

        self.todo_entry = tk.Entry(input_frame, width=50)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        add_button = tk.Button(input_frame, text="추가", command=self.add_todo)
        add_button.pack(side=tk.LEFT)

        # 목록 프레임
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.todo_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.todo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.todo_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_listbox.config(yscrollcommand=scrollbar.set)

        # 버튼 프레임
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)

        complete_button = tk.Button(button_frame, text="완료 처리", command=self.mark_as_completed)
        complete_button.pack(side=tk.LEFT)

        delete_button = tk.Button(button_frame, text="삭제", command=self.delete_todo)
        delete_button.pack(side=tk.RIGHT)

    def refresh_todos(self):
        """목록을 새로고침하여 모든 할 일을 표시합니다."""
        self.todo_listbox.delete(0, tk.END)
        self.todos = self.todo_service.get_all_todos()
        for todo in self.todos:
            display_text = f"[{todo.status}] {todo.content}"
            self.todo_listbox.insert(tk.END, display_text)

    def add_todo(self):
        """새로운 할 일을 추가합니다."""
        content = self.todo_entry.get()
        if not content.strip():
            messagebox.showwarning("입력 오류", "할 일의 내용을 입력해주세요.")
            return
        
        new_todo = self.todo_service.add_todo(content)
        if new_todo:
            self.todo_entry.delete(0, tk.END)
            self.refresh_todos()
        else:
            messagebox.showerror("추가 실패", "알 수 없는 오류로 할 일을 추가하지 못했습니다.")

    def get_selected_todo_id(self):
        """리스트박스에서 선택된 항목의 ID를 반환합니다."""
        selected_indices = self.todo_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("선택 오류", "목록에서 항목을 먼저 선택해주세요.")
            return None
        return self.todos[selected_indices[0]].id

    def mark_as_completed(self):
        """선택된 할 일을 '완료' 상태로 변경합니다."""
        todo_id = self.get_selected_todo_id()
        if todo_id is not None:
            if self.todo_service.update_todo_status(todo_id, 'completed'):
                self.refresh_todos()
            else:
                messagebox.showerror("업데이트 실패", "상태를 업데이트하지 못했습니다.")

    def delete_todo(self):
        """선택된 할 일을 삭제합니다."""
        todo_id = self.get_selected_todo_id()
        if todo_id is not None:
            if self.todo_service.delete(todo_id):
                self.refresh_todos()
            else:
                messagebox.showerror("삭제 실패", "할 일을 삭제하지 못했습니다.")
