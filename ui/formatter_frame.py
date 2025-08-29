import tkinter as tk
from tkinter import ttk


class FormatterFrame(tk.Frame):
    def __init__(self, parent, formatter_service, app):
        super().__init__(parent)
        self.formatter_service = formatter_service
        self.app = app  # 상태 메시지/클립보드 사용

        self.create_widgets()

    def create_widgets(self):
        # 전체 레이아웃
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # 입력 패널
        input_frame = ttk.Frame(main_pane, padding=5)
        tk.Label(input_frame, text="입력", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)
        self.input_text = tk.Text(input_frame, wrap=tk.WORD, height=10, width=40)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        main_pane.add(input_frame, weight=1)

        # 출력 패널
        output_frame = ttk.Frame(main_pane, padding=5)
        tk.Label(output_frame, text="결과", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=10, width=40)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        main_pane.add(output_frame, weight=1)

        # 컨트롤 패널
        control_frame = tk.Frame(self, pady=5)
        control_frame.pack(fill=tk.X)

        tk.Button(control_frame, text="Tab → CSV", command=self.format_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Tab → Markdown 표", command=self.format_to_md_table).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="목록으로 (-)", command=self.format_to_list).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="공백→줄바꿈(Excel)", command=self.format_space_to_newline).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="결과 복사", command=self.copy_output).pack(side=tk.RIGHT, padx=5)

    def get_input_text(self):
        return self.input_text.get("1.0", tk.END)

    def set_output_text(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)

    def format_to_csv(self):
        result = self.formatter_service.to_csv(self.get_input_text())
        self.set_output_text(result)

    def format_to_md_table(self):
        result = self.formatter_service.to_markdown_table(self.get_input_text())
        self.set_output_text(result)

    def format_to_list(self):
        result = self.formatter_service.to_list(self.get_input_text())
        self.set_output_text(result)

    def format_space_to_newline(self):
        result = self.formatter_service.space_to_newline(self.get_input_text())
        self.set_output_text(result)

    def copy_output(self):
        output = self.output_text.get("1.0", tk.END).strip()
        if output:
            self.app.clipboard_clear()
            self.app.clipboard_append(output)
            self.app.update_status("결과가 클립보드로 복사되었습니다")

