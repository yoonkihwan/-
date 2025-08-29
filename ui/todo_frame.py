import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from services.todo_service import TodoService

class TodoFrame(tk.Frame):
    def __init__(self, master, todo_service: TodoService, **kwargs):
        super().__init__(master, **kwargs)
        self.todo_service = todo_service

        self._configure_styles()
        self._create_widgets()
        self.refresh_todos()

    def _configure_styles(self):
        # Treeview 항목 폰트 설정 (기본/취소선)
        self.normal_font = tkfont.Font(family="Malgun Gothic", size=10)
        self.strikethrough_font = tkfont.Font(family="Malgun Gothic", size=10)
        self.strikethrough_font.configure(overstrike=1)

    def _create_widgets(self):
        self.config(padx=10, pady=10)
        
        input_frame = tk.Frame(self)
        input_frame.pack(fill=tk.X, pady=5)

        self.todo_entry = tk.Entry(input_frame, width=50)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", self.add_todo)

        add_button = tk.Button(input_frame, text="추가", command=self.add_todo)
        add_button.pack(side=tk.LEFT)

        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview로 리스트 구현
        self.todo_tree = ttk.Treeview(list_frame, columns=("content",), show="tree headings")
        self.todo_tree.heading("#0", text="✓")
        self.todo_tree.heading("content", text="할 일")
        self.todo_tree.column("#0", width=40, anchor="center")
        self.todo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.todo_tree.bind("<Double-1>", self.toggle_todo_status)

        # 완료/미완료 상태에 따른 스타일 태그 설정
        self.todo_tree.tag_configure('completed', font=self.strikethrough_font, foreground="#888888")
        self.todo_tree.tag_configure('pending', font=self.normal_font, foreground="#000000")

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.todo_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_tree.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)

        delete_button = tk.Button(button_frame, text="삭제", command=self.delete_todo)
        delete_button.pack(side=tk.RIGHT)

    def refresh_todos(self):
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        
        self.todos = self.todo_service.get_all_todos()
        for todo in self.todos:
            checkbox = "☑" if todo.status == 'completed' else "☐"
            tags = ('completed',) if todo.status == 'completed' else ('pending',)
            self.todo_tree.insert("", tk.END, iid=todo.id, text=checkbox, values=(todo.content,), tags=tags)

    def add_todo(self, event=None):
        content = self.todo_entry.get()
        if not content.strip():
            messagebox.showwarning("입력 오류", "할 일의 내용을 입력해주세요.")
            return
        
        if self.todo_service.add_todo(content):
            self.todo_entry.delete(0, tk.END)
            self.refresh_todos()
        else:
            messagebox.showerror("추가 실패", "알 수 없는 오류로 할 일을 추가하지 못했습니다.")

    def get_selected_todo_id(self):
        selected_items = self.todo_tree.selection()
        if not selected_items:
            messagebox.showwarning("선택 오류", "목록에서 항목을 먼저 선택해주세요.")
            return None
        return selected_items[0]

    def toggle_todo_status(self, event):
        item_id = self.todo_tree.identify_row(event.y)
        if not item_id:
            return

        # 현재 상태 확인
        current_todo = next((t for t in self.todos if str(t.id) == item_id), None)
        if not current_todo:
            return

        new_status = 'pending' if current_todo.status == 'completed' else 'completed'
        
        if self.todo_service.update_todo_status(current_todo.id, new_status):
            self.refresh_todos()
        else:
            messagebox.showerror("업데이트 실패", "상태를 업데이트하지 못했습니다.")

    def delete_todo(self):
        todo_id = self.get_selected_todo_id()
        if todo_id is not None:
            if self.todo_service.delete_todo(todo_id):
                self.refresh_todos()
            else:
                messagebox.showerror("삭제 실패", "할 일을 삭제하지 못했습니다.")
