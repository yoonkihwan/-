
import tkinter as tk
from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
from ui.todo_frame import TodoFrame
from datetime import datetime

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("업무용 PC 앱")
        self.geometry("800x600")

        # --- Clock Label ---
        self.clock_label = tk.Label(self, font=('Helvetica', 12))
        self.clock_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.update_clock()

        # --- Services ---
        todo_repo = TodoRepository(db_path="todos.db")
        self.todo_service = TodoService(repository=todo_repo)

        # --- Main UI Frame ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TodoFrame을 메인 프레임에 추가
        todo_app_frame = TodoFrame(main_frame, self.todo_service)
        todo_app_frame.pack(fill=tk.BOTH, expand=True)

    def update_clock(self):
        """1초마다 현재 시간을 표시하는 라벨을 업데이트합니다."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock) # 1000ms(1초) 후에 다시 실행

if __name__ == "__main__":
    app = Application()
    app.mainloop()

