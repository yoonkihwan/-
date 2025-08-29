import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os

class LauncherFrame(tk.Frame):
    def __init__(self, parent, launcher_service, app):
        super().__init__(parent)
        self.launcher_service = launcher_service
        self.app = app
        self.workspaces = []
        self.current_workspace_id = None
        self.selected_item_widget = None
        self.item_widgets = {}

        self.create_widgets()
        self.load_workspaces()

    def create_widgets(self):
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # 왼쪽: 작업 공간 목록
        ws_frame = ttk.Frame(pane, padding=5)
        ws_list_frame = tk.LabelFrame(ws_frame, text="작업 공간")
        ws_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.workspace_list = tk.Listbox(ws_list_frame)
        self.workspace_list.pack(fill=tk.BOTH, expand=True)
        self.workspace_list.bind("<<ListboxSelect>>", self.on_workspace_select)
        
        ws_btn_frame = tk.Frame(ws_frame)
        ws_btn_frame.pack(fill=tk.X)
        tk.Button(ws_btn_frame, text="추가", command=self.add_workspace).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(ws_btn_frame, text="삭제", command=self.delete_workspace).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(ws_frame, text="▶ 작업 공간 실행", command=self.launch_workspace, background="#28a745", foreground="white").pack(fill=tk.X, pady=(5,0))
        pane.add(ws_frame, weight=1)

        # 오른쪽: 아이템 목록
        items_frame = ttk.Frame(pane, padding=5)
        items_main_frame = tk.LabelFrame(items_frame, text="항목 (파일, 폴더, URL)")
        items_main_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.canvas = tk.Canvas(items_main_frame, borderwidth=0)
        self.item_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(items_main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.item_frame, anchor="nw")
        self.item_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        item_btn_frame = tk.Frame(items_frame)
        item_btn_frame.pack(fill=tk.X)
        tk.Button(item_btn_frame, text="파일 추가", command=self.add_file).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(item_btn_frame, text="폴더 추가", command=self.add_folder).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(item_btn_frame, text="URL 추가", command=self.add_url).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(item_btn_frame, text="항목 삭제", command=self.delete_item).pack(side=tk.LEFT, expand=True, fill=tk.X)
        pane.add(items_frame, weight=3)

    def load_workspaces(self):
        self.workspace_list.delete(0, tk.END)
        self.workspaces = self.launcher_service.get_all_workspaces()
        for ws in self.workspaces:
            self.workspace_list.insert(tk.END, ws.name)
        if self.workspaces:
            self.workspace_list.selection_set(0)
            self.on_workspace_select(None)
        else:
            self.clear_items()

    def on_workspace_select(self, event):
        selected_indices = self.workspace_list.curselection()
        if not selected_indices:
            self.clear_items()
            return
        selected_index = selected_indices[0]
        self.current_workspace_id = self.workspaces[selected_index].id
        self.load_items_for_workspace()

    def load_items_for_workspace(self):
        self.clear_items()
        if not self.current_workspace_id:
            return
        items = self.launcher_service.get_items_by_workspace(self.current_workspace_id)
        cols = 4
        for i, item in enumerate(items):
            row, col = divmod(i, cols)
            item_widget = tk.Frame(self.item_frame, borderwidth=1, relief="flat", padx=5, pady=5)
            item_widget.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            icon = "📁" if item.item_type == 'folder' else ("🌐" if item.item_type == 'url' else "📄")
            icon_label = tk.Label(item_widget, text=icon, font=('Helvetica', 24))
            icon_label.pack()
            name_label = tk.Label(item_widget, text=item.name, wraplength=90, justify="center")
            name_label.pack()
            
            self.item_widgets[item_widget] = item
            # 컨테이너와 자식 위젯 모두에 이벤트 바인딩
            for widget in [item_widget, icon_label, name_label]:
                widget.bind("<Button-1>", self.on_select_item)
                widget.bind("<Double-1>", self.on_double_click)

    def clear_items(self):
        for widget in self.item_frame.winfo_children():
            widget.destroy()
        self.item_widgets.clear()
        self.selected_item_widget = None

    def add_workspace(self):
        name = simpledialog.askstring("작업 공간 추가", "새 작업 공간의 이름을 입력하세요:")
        if name:
            if self.launcher_service.add_workspace(name):
                self.load_workspaces()
            else:
                messagebox.showerror("오류", "이미 존재하는 이름입니다.")

    def delete_workspace(self):
        if not self.current_workspace_id:
            messagebox.showwarning("경고", "삭제할 작업 공간을 선택하세요.")
            return
        if messagebox.askyesno("확인", "정말 이 작업 공간을 삭제하시겠습니까?\n(내부의 모든 항목도 함께 삭제됩니다)"):
            self.launcher_service.delete_workspace(self.current_workspace_id)
            self.current_workspace_id = None
            self.load_workspaces()

    def launch_workspace(self):
        if not self.current_workspace_id:
            messagebox.showwarning("경고", "실행할 작업 공간을 선택하세요.")
            return
        self.launcher_service.launch_workspace(self.current_workspace_id)
        self.app.update_status("작업 공간 실행 완료")

    def _add_item(self, name, path, item_type):
        if not self.current_workspace_id:
            messagebox.showwarning("경고", "항목을 추가할 작업 공간을 먼저 선택하세요.")
            return
        self.launcher_service.add_item(name, path, item_type, self.current_workspace_id)
        self.load_items_for_workspace()

    def add_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self._add_item(os.path.basename(filepath), filepath, 'file')

    def add_folder(self):
        folderpath = filedialog.askdirectory()
        if folderpath:
            self._add_item(os.path.basename(folderpath), folderpath, 'folder')

    def add_url(self):
        url = simpledialog.askstring("URL 추가", "연결할 웹사이트 주소를 입력하세요:")
        if url:
            name = simpledialog.askstring("이름 설정", "해당 URL의 이름을 입력하세요:", initialvalue=url.split('//')[-1].split('/')[0])
            if name:
                self._add_item(name, url, 'url')

    def delete_item(self):
        if not self.selected_item_widget:
            messagebox.showwarning("경고", "삭제할 항목을 선택하세요.")
            return
        if messagebox.askyesno("확인", "선택한 항목을 정말 삭제하시겠습니까?"):
            item_to_delete = self.item_widgets.get(self.selected_item_widget)
            if item_to_delete:
                self.launcher_service.delete_item(item_to_delete.id)
                self.load_items_for_workspace()

    def on_select_item(self, event):
        if self.selected_item_widget:
            try:
                self.selected_item_widget.config(relief="flat", bg=self.cget('bg'))
            except tk.TclError:
                pass # 위젯이 이미 삭제된 경우
        
        widget = event.widget
        while widget not in self.item_widgets:
            widget = widget.master
            if widget is None: return

        self.selected_item_widget = widget
        self.selected_item_widget.config(relief="solid", bg="lightblue")

    def on_double_click(self, event):
        widget = event.widget
        while widget not in self.item_widgets:
            widget = widget.master
            if widget is None: return
        
        item_to_launch = self.item_widgets.get(widget)
        if item_to_launch:
            self.launcher_service.launch_item(item_to_launch.path, item_to_launch.item_type)
