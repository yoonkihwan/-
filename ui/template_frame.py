import tkinter as tk
from tkinter import ttk, messagebox
from ui.scroll_util import bind_mousewheel


class TemplateFrame(tk.Frame):
    def __init__(self, parent, template_service, app):
        super().__init__(parent)
        self.template_service = template_service
        self.app = app

        self.create_widgets()
        self.load_templates()

    def create_widgets(self):
        # 레이아웃: 왼쪽 목록, 오른쪽 내용/버튼
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # 왼쪽: 템플릿 목록
        list_frame = ttk.Frame(pane, padding=5)
        self.template_list = tk.Listbox(list_frame)
        self.template_list.pack(fill=tk.BOTH, expand=True)
        self.template_list.bind("<<ListboxSelect>>", self.on_template_select)
        # 마우스 휠 스크롤
        bind_mousewheel(self.template_list)
        pane.add(list_frame, weight=1)

        # 오른쪽: 템플릿 내용 + 컨트롤
        content_frame = ttk.Frame(pane, padding=5)
        pane.add(content_frame, weight=3)

        self.title_var = tk.StringVar()
        tk.Entry(content_frame, textvariable=self.title_var, font=('Helvetica', 12, 'bold')).pack(fill=tk.X, pady=(0, 5))

        self.content_text = tk.Text(content_frame, wrap=tk.WORD, height=10)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        bind_mousewheel(self.content_text)

        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="새 템플릿", command=self.new_template).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="저장", command=self.save_template).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="삭제", command=self.delete_template).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="클립보드 복사", command=self.copy_to_clipboard).pack(side=tk.RIGHT, padx=5)

    def load_templates(self):
        self.template_list.delete(0, tk.END)
        self.templates = self.template_service.get_all_templates()
        for template in self.templates:
            self.template_list.insert(tk.END, template.title)
        self.clear_form()

    def on_template_select(self, event):
        selected_indices = self.template_list.curselection()
        if not selected_indices:
            return
        selected_index = selected_indices[0]
        template = self.templates[selected_index]
        self.current_template_id = template.id
        self.title_var.set(template.title)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, template.content)

    def clear_form(self):
        self.current_template_id = None
        self.title_var.set("")
        self.content_text.delete("1.0", tk.END)
        self.template_list.selection_clear(0, tk.END)

    def new_template(self):
        self.clear_form()
        self.title_var.set("새 템플릿 제목")

    def save_template(self):
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("입력 오류", "제목과 내용을 모두 입력하세요.")
            return

        if self.current_template_id:
            # 업데이트
            success = self.template_service.update_template(self.current_template_id, title, content)
            if not success:
                messagebox.showerror("저장 실패", "같은 이름의 다른 템플릿이 이미 존재합니다.")
                return
        else:
            # 신규 추가
            new_id = self.template_service.add_template(title, content)
            if not new_id:
                messagebox.showerror("추가 실패", "같은 이름의 템플릿이 이미 존재합니다.")
                return
            self.current_template_id = new_id

        self.load_templates()
        self.app.update_status("템플릿이 저장되었습니다.")

    def delete_template(self):
        if not self.current_template_id:
            messagebox.showwarning("선택 오류", "삭제할 템플릿을 목록에서 선택하세요.")
            return
        if messagebox.askyesno("삭제 확인", "정말 이 템플릿을 삭제하시겠습니까?"):
            self.template_service.delete_template(self.current_template_id)
            self.load_templates()
            self.app.update_status("템플릿이 삭제되었습니다.")

    def copy_to_clipboard(self):
        content = self.content_text.get("1.0", tk.END).strip()
        if content:
            self.app.clipboard_clear()
            self.app.clipboard_append(content)
            self.app.update_status("템플릿 내용이 클립보드로 복사되었습니다")

