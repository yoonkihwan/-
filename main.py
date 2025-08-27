
import tkinter as tk
from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
from ui.todo_frame import TodoFrame

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("업무용 PC 앱")
        self.geometry("800x600")

        # 데이터베이스 및 서비스 초기화
        todo_repo = TodoRepository(db_path="todos.db")
        self.todo_service = TodoService(repository=todo_repo)

        # UI 구성
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TodoFrame을 메인 프레임에 추가
        todo_app_frame = TodoFrame(main_frame, self.todo_service)
        todo_app_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = Application()
    app.mainloop()

