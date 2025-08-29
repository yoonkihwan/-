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
        # Controls (input + actions)
        input_frame = tk.Frame(self)
        input_frame.pack(fill=tk.X, pady=5)

        self.todo_entry = tk.Entry(input_frame, width=50)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", self.add_todo)

        add_button = tk.Button(input_frame, text="추가", command=self.add_todo)
        add_button.pack(side=tk.LEFT)
        add_sub_button = tk.Button(input_frame, text="하위 추가", command=self.add_subtask)
        add_sub_button.pack(side=tk.LEFT, padx=(5,0))

        # Filter bar
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0,5))
        tk.Label(filter_frame, text="필터:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value='all')
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, state='readonly', values=['all','pending','completed'])
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_todos())
        self.show_archived_var = tk.BooleanVar(value=False)
        show_archived_cb = ttk.Checkbutton(filter_frame, text='보관 보기', variable=self.show_archived_var, command=self.refresh_todos)
        show_archived_cb.pack(side=tk.LEFT, padx=10)

        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview로 리스트 구현 (확장 선택 + 트리모드)
        self.todo_tree = ttk.Treeview(list_frame, columns=("content",), show="tree headings", selectmode='extended')
        self.todo_tree.heading("#0", text="✓")
        self.todo_tree.heading("content", text="할 일")
        self.todo_tree.column("#0", width=40, anchor="center")
        self.todo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.todo_tree.bind("<Double-1>", self.toggle_todo_status)
        # keyboard shortcuts
        self.todo_tree.bind('<Delete>', lambda e: self.delete_selected())
        self.todo_tree.bind('<space>', lambda e: self.toggle_selected_status())

        # Drag-and-drop reordering within same parent
        self._drag_item = None
        self._drag_parent = None
        self.todo_tree.bind('<ButtonPress-1>', self._on_tree_button_press)
        self.todo_tree.bind('<B1-Motion>', self._on_tree_motion)
        self.todo_tree.bind('<ButtonRelease-1>', self._on_tree_button_release)

        # 완료/미완료 상태에 따른 스타일 태그 설정
        self.todo_tree.tag_configure('completed', font=self.strikethrough_font, foreground="#888888")
        self.todo_tree.tag_configure('pending', font=self.normal_font, foreground="#000000")

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.todo_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_tree.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)

        delete_button = tk.Button(button_frame, text="삭제", command=self.delete_selected)
        delete_button.pack(side=tk.RIGHT)

    def refresh_todos(self):
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        
        # Auto-archive old completed
        try:
            self.todo_service.archive_completed_older_than_days(7)
        except Exception:
            pass

        status_filter = None if self.filter_var.get() == 'all' else self.filter_var.get()
        show_archived = bool(self.show_archived_var.get())
        # Advanced fetch for hierarchy/ordering
        if hasattr(self.todo_service, 'get_all_todos_adv'):
            self.todos = self.todo_service.get_all_todos_adv(status_filter=status_filter, show_archived=show_archived)
        else:
            self.todos = self.todo_service.get_all_todos()

        # Build a lookup and children mapping
        by_id = {str(t.id): t for t in self.todos}
        children_map = {}
        for t in self.todos:
            pid = '' if (t.parent_id is None) else str(t.parent_id)
            children_map.setdefault(pid, []).append(t)
        # Insert recursively
        def insert_branch(parent_key: str, parent_tree_iid: str):
            items = children_map.get(parent_key, [])
            # Order by sort_order then created_at implicitly from query
            for t in items:
                iid = str(t.id)
                checkbox = "☑" if t.status == 'completed' else "☐"
                tags = ('completed',) if t.status == 'completed' else ('pending',)
                self.todo_tree.insert(parent_tree_iid, tk.END, iid=iid, text=checkbox, values=(t.content,), tags=tags, open=True)
                insert_branch(iid, iid)
        insert_branch('', '')

    def add_todo(self, event=None):
        content = self.todo_entry.get()
        if not content.strip():
            messagebox.showwarning("입력 오류", "할 일의 내용을 입력해주세요.")
            return
        parent_id = None
        sel = self.todo_tree.selection()
        if sel:
            # If a parent is selected and user clicked '추가', make it a root unless using '하위 추가'
            parent_id = None
        # Prefer advanced add to set order/parent
        add_method = getattr(self.todo_service, 'add_todo_adv', self.todo_service.add_todo)
        if add_method(content, parent_id):
            self.todo_entry.delete(0, tk.END)
            self.refresh_todos()
        else:
            messagebox.showerror("추가 실패", "알 수 없는 오류로 할 일을 추가하지 못했습니다.")

    def add_subtask(self):
        content = self.todo_entry.get()
        if not content.strip():
            messagebox.showwarning("입력 오류", "할 일의 내용을 입력해주세요.")
            return
        sel = self.todo_tree.selection()
        if not sel:
            messagebox.showwarning("선택 오류", "하위 작업을 추가할 상위 항목을 선택해주세요.")
            return
        parent_id = int(sel[0])
        add_method = getattr(self.todo_service, 'add_todo_adv', self.todo_service.add_todo)
        if add_method(content, parent_id):
            self.todo_entry.delete(0, tk.END)
            self.refresh_todos()
        else:
            messagebox.showerror("추가 실패", "알 수 없는 오류로 하위 작업을 추가하지 못했습니다.")

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

    def toggle_selected_status(self):
        selected = self.todo_tree.selection()
        if not selected:
            return
        # Determine target status: if all completed -> pending, else completed
        selected_todos = [t for t in self.todos if str(t.id) in selected]
        all_completed = all(t.status == 'completed' for t in selected_todos)
        target = 'pending' if all_completed else 'completed'
        ids = [int(i) for i in selected]
        if hasattr(self.todo_service, 'update_todos_status_bulk'):
            self.todo_service.update_todos_status_bulk(ids, target)
        else:
            for tid in ids:
                self.todo_service.update_todo_status(tid, target)
        self.refresh_todos()

    def delete_selected(self):
        selected = self.todo_tree.selection()
        if not selected:
            messagebox.showwarning("선택 오류", "삭제할 항목을 선택하세요.")
            return
        if not messagebox.askyesno("삭제 확인", f"선택한 {len(selected)}개 항목을 삭제할까요?"):
            return
        ids = [int(i) for i in selected]
        if hasattr(self.todo_service, 'delete_many'):
            self.todo_service.delete_many(ids)
        else:
            for tid in ids:
                self.todo_service.delete_todo(tid)
        self.refresh_todos()

    # Drag-and-drop helpers
    def _on_tree_button_press(self, event):
        iid = self.todo_tree.identify_row(event.y)
        if iid:
            self._drag_item = iid
            parent = self.todo_tree.parent(iid)
            self._drag_parent = parent
        else:
            self._drag_item = None
            self._drag_parent = None

    def _on_tree_motion(self, event):
        if not self._drag_item:
            return
        target_iid = self.todo_tree.identify_row(event.y)
        if not target_iid or target_iid == self._drag_item:
            return
        # Only move within same parent to keep hierarchy simple
        if self.todo_tree.parent(target_iid) != self._drag_parent:
            return
        index = self.todo_tree.index(target_iid)
        self.todo_tree.move(self._drag_item, self._drag_parent, index)

    def _on_tree_button_release(self, event):
        if not self._drag_item:
            return
        parent = self._drag_parent
        # Read new order under this parent and persist
        children = self.todo_tree.get_children(parent)
        ordered_ids = [int(i) for i in children]
        self.todo_service.update_sort_orders(int(parent) if parent else None, ordered_ids)
        self._drag_item = None
        self._drag_parent = None
