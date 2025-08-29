
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
from services.screenshot_service import ScreenshotService
from services.config_service import ConfigService
from services.ocr_service import OCRService
from services.clipboard_service import ClipboardService
from services.launcher_service import LauncherService
from services.formatter_service import FormatterService
from services.template_service import TemplateService # 추가
from ui.todo_frame import TodoFrame
from ui.clipboard_frame import ClipboardFrame
from ui.launcher_frame import LauncherFrame
from ui.formatter_frame import FormatterFrame
from ui.template_frame import TemplateFrame # 추가
from datetime import datetime

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("업무용 PC 앱")
        self.geometry("800x600")

        # --- Services ---
        self.config_service = ConfigService()
        self.todo_service = TodoService(repository=TodoRepository(db_path="todos.db"))
        self.screenshot_service = ScreenshotService(config_service=self.config_service)
        self.ocr_service = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
        self.clipboard_service = ClipboardService(root=self, on_change_callback=None)
        self.launcher_service = LauncherService()
        self.formatter_service = FormatterService()
        self.template_service = TemplateService() # 추가

        # --- Main Layout ---
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.clock_label = tk.Label(top_frame, font=('Helvetica', 12))
        self.clock_label.pack(side=tk.LEFT)
        self.update_clock()

        self.status_label = tk.Label(top_frame, text="", font=('Helvetica', 10), fg="blue")
        self.status_label.pack(side=tk.RIGHT)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = tk.Frame(bottom_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False) # 왼쪽 프레임 크기 고정

        right_frame = tk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Widgets ---
        # Left Frame Widgets
        screenshot_frame = tk.LabelFrame(left_frame, text="스크린샷 & OCR")
        screenshot_frame.pack(fill=tk.X, pady=(0, 10))
        fs_button = tk.Button(screenshot_frame, text="전체 화면 캡처", command=self.capture_fullscreen)
        fs_button.pack(fill=tk.X, padx=5, pady=5)
        sr_button = tk.Button(screenshot_frame, text="영역 선택 캡처", command=self.capture_region)
        sr_button.pack(fill=tk.X, padx=5, pady=5)
        ocr_button = tk.Button(screenshot_frame, text="영역 캡처 후 OCR", command=self.capture_and_ocr)
        ocr_button.pack(fill=tk.X, padx=5, pady=5)

        settings_frame = tk.LabelFrame(left_frame, text="설정")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # 설정 프레임 내부를 그리드로 재구성
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)

        change_dir_button = tk.Button(settings_frame, text="저장 폴더 변경", command=self.change_screenshot_directory)
        change_dir_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        open_dir_button = tk.Button(settings_frame, text="저장 폴더 열기", command=self.open_screenshot_directory)
        open_dir_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        tesseract_path_button = tk.Button(settings_frame, text="Tesseract 경로 설정", command=self.set_tesseract_path)
        tesseract_path_button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        clipboard_history_frame = ClipboardFrame(left_frame, app=self, clipboard_service=self.clipboard_service)
        clipboard_history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Right Frame Widgets (이제 Notebook으로 관리)
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        todo_app_frame = TodoFrame(notebook, self.todo_service)
        self.todo_frame = todo_app_frame
        launcher_app_frame = LauncherFrame(notebook, self.launcher_service, self)
        formatter_app_frame = FormatterFrame(notebook, self.formatter_service, self)
        template_app_frame = TemplateFrame(notebook, self.template_service, self)

        notebook.add(todo_app_frame, text="투두리스트")
        notebook.add(launcher_app_frame, text="작업 공간") # 이름 변경
        notebook.add(formatter_app_frame, text="텍스트 변환기")
        notebook.add(template_app_frame, text="이메일 템플릿")

        # Start background services
        self.clipboard_service.start_monitoring()

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.after(5000, lambda: self.status_label.config(text=""))

    def capture_fullscreen(self):
        try:
            filepath = self.screenshot_service.capture_fullscreen()
            self.update_status(f"저장 완료: {filepath}")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")

    def capture_region(self):
        self.update_status("화면을 최소화하고 영역을 선택하세요...")
        self.wm_state('iconic')
        self.after(200, lambda: self._execute_region_capture(ocr_after=False))

    def capture_and_ocr(self):
        self.update_status("OCR 할 영역을 선택하세요...")
        self.wm_state('iconic')
        self.after(200, lambda: self._execute_region_capture(ocr_after=True))

    def _execute_region_capture(self, ocr_after=False):
        try:
            filepath = self.screenshot_service.capture_region()
            if filepath:
                self.update_status(f"저장 완료: {filepath}")
                if ocr_after:
                    self.run_ocr(filepath)
            else:
                self.update_status("캡처가 취소되었습니다.")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")
        finally:
            self.wm_state('normal')

    def run_ocr(self, filepath):
        self.update_status("텍스트 인식 중...")
        self.ocr_service = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
        extracted_text = self.ocr_service.extract_text_from_image(filepath)
        if "오류:" in extracted_text:
            messagebox.showerror("OCR 실패", extracted_text)
        else:
            self.show_ocr_result(extracted_text)
        self.update_status("OCR 완료")

    def show_ocr_result(self, text):
        result_window = tk.Toplevel(self)
        result_window.title("OCR 결과")
        result_window.geometry("400x300")

        text_widget = tk.Text(result_window, wrap=tk.WORD, font=('Malgun Gothic', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, text)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update_status("클립보드에 복사되었습니다.")

        copy_button = tk.Button(result_window, text="클립보드에 복사", command=copy_to_clipboard)
        copy_button.pack(pady=5)

    def show_ocr_result(self, text):
        result_window = tk.Toplevel(self)
        result_window.title("OCR 결과")
        result_window.geometry("400x360")

        text_widget = tk.Text(result_window, wrap=tk.WORD, font=('Malgun Gothic', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, text)

        btns = tk.Frame(result_window)
        btns.pack(fill=tk.X, pady=5)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(text_widget.get("1.0", tk.END))
            self.update_status("클립보드에 복사했습니다")

        def add_to_todo():
            content = text_widget.get("1.0", tk.END)
            if not content.strip():
                messagebox.showwarning("추가 실패", "추가할 내용이 없습니다.")
                return
            if hasattr(self.todo_service, 'add_from_text'):
                count = self.todo_service.add_from_text(content)
                messagebox.showinfo("할 일 추가", f"{count}개 항목을 추가했습니다.")
            else:
                self.todo_service.add_todo(content.strip())
                messagebox.showinfo("할 일 추가", "1개 항목을 추가했습니다.")
            if hasattr(self, 'todo_frame'):
                self.todo_frame.refresh_todos()

        copy_button = tk.Button(btns, text="클립보드 복사", command=copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=5)
        add_button = tk.Button(btns, text="할 일로 추가", command=add_to_todo)
        add_button.pack(side=tk.LEFT, padx=5)

    def change_screenshot_directory(self):
        new_dir = filedialog.askdirectory(
            title="스크린샷 저장 폴더 선택",
            initialdir=self.config_service.get("screenshot_save_dir")
        )
        if new_dir:
            self.config_service.set("screenshot_save_dir", new_dir)
            self.update_status(f"스크린샷 저장 폴더가 변경되었습니다.")

    def open_screenshot_directory(self):
        path = self.config_service.get("screenshot_save_dir")
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", path], check=True)
        except Exception as e:
            messagebox.showerror("폴더 열기 실패", f"폴더를 열 수 없습니다: {e}")

    def set_tesseract_path(self):
        filepath = filedialog.askopenfilename(
            title="tesseract.exe 파일을 선택하세요",
            filetypes=[("Executable files", "*.exe")]
        )
        if filepath:
            self.config_service.set('tesseract_cmd_path', filepath)
            self.update_status("Tesseract 경로가 설정되었습니다. 다시 시도해주세요.")
            messagebox.showinfo("설정 완료", "Tesseract 경로가 설정되었습니다. OCR 기능을 다시 시도해주세요.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
