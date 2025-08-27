
import tkinter as tk
from tkinter import messagebox
from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
from services.screenshot_service import ScreenshotService
from ui.todo_frame import TodoFrame
from datetime import datetime

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("업무용 PC 앱")
        self.geometry("800x600")

        # --- Services ---
        self.todo_service = TodoService(repository=TodoRepository(db_path="todos.db"))
        self.screenshot_service = ScreenshotService()

        # --- Main Layout ---
        # Top frame for clock and status
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.clock_label = tk.Label(top_frame, font=('Helvetica', 12))
        self.clock_label.pack(side=tk.LEFT)
        self.update_clock()

        self.status_label = tk.Label(top_frame, text="", font=('Helvetica', 10), fg="blue")
        self.status_label.pack(side=tk.RIGHT)

        # Bottom frame for main content
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left frame for controls
        left_frame = tk.Frame(bottom_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right frame for content (like Todo list)
        right_frame = tk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Widgets ---
        # Screenshot controls in left frame
        screenshot_frame = tk.LabelFrame(left_frame, text="스크린샷")
        screenshot_frame.pack(fill=tk.X, pady=10)

        fs_button = tk.Button(screenshot_frame, text="전체 화면 캡처", command=self.capture_fullscreen)
        fs_button.pack(fill=tk.X, padx=5, pady=5)

        sr_button = tk.Button(screenshot_frame, text="영역 선택 캡처", command=self.capture_region)
        sr_button.pack(fill=tk.X, padx=5, pady=5)

        # Todo list in right frame
        todo_app_frame = TodoFrame(right_frame, self.todo_service)
        todo_app_frame.pack(fill=tk.BOTH, expand=True)

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.after(5000, lambda: self.status_label.config(text="")) # 5초 후 메시지 지움

    def capture_fullscreen(self):
        try:
            filepath = self.screenshot_service.capture_fullscreen()
            self.update_status(f"저장 완료: {filepath}")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")

    def capture_region(self):
        self.update_status("화면을 최소화하고 영역을 선택하세요...")
        self.wm_state('iconic') # 메인 창 최소화
        self.after(200, self._execute_region_capture) # 잠시 후 캡처 실행

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
            self.wm_state('normal') # 메인 창 다시 표시

if __name__ == "__main__":
    app = Application()
    app.mainloop()

