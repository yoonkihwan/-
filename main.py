
import tkinter as tk
from tkinter import messagebox, filedialog
from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
from services.screenshot_service import ScreenshotService
from services.config_service import ConfigService
from ui.todo_frame import TodoFrame
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

        left_frame = tk.Frame(bottom_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = tk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Widgets ---
        # Screenshot controls
        screenshot_frame = tk.LabelFrame(left_frame, text="스크린샷")
        screenshot_frame.pack(fill=tk.X, pady=10)
        fs_button = tk.Button(screenshot_frame, text="전체 화면 캡처", command=self.capture_fullscreen)
        fs_button.pack(fill=tk.X, padx=5, pady=5)
        sr_button = tk.Button(screenshot_frame, text="영역 선택 캡처", command=self.capture_region)
        sr_button.pack(fill=tk.X, padx=5, pady=5)

        # Settings controls
        settings_frame = tk.LabelFrame(left_frame, text="설정")
        settings_frame.pack(fill=tk.X, pady=10)
        change_dir_button = tk.Button(settings_frame, text="저장 폴더 변경", command=self.change_screenshot_directory)
        change_dir_button.pack(fill=tk.X, padx=5, pady=5)

        # Todo list
        todo_app_frame = TodoFrame(right_frame, self.todo_service)
        todo_app_frame.pack(fill=tk.BOTH, expand=True)

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
        self.after(200, self._execute_region_capture)

    def _execute_region_capture(self):
        try:
            filepath = self.screenshot_service.capture_region()
            if filepath:
                self.update_status(f"저장 완료: {filepath}")
            else:
                self.update_status("캡처가 취소되었습니다.")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")
        finally:
            self.wm_state('normal')

    def change_screenshot_directory(self):
        new_dir = filedialog.askdirectory(
            title="스크린샷 저장 폴더 선택",
            initialdir=self.config_service.get("screenshot_save_dir")
        )
        if new_dir:
            self.config_service.set("screenshot_save_dir", new_dir)
            self.update_status(f"스크린샷 저장 폴더가 변경되었습니다.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()

