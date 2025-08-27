
import sqlite3
from typing import List, Optional
from models.todo import Todo

class TodoRepository:
    """
    Todo 데이터베이스 CRUD 작업을 처리하는 저장소
    """
    def __init__(self, db_path: str):
        """
        저장소를 초기화하고 데이터베이스 연결을 설정합니다.
        :param db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        """데이터베이스 연결을 반환합니다."""
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """
        'todos' 테이블이 없으면 생성합니다.
        """
        conn = self._get_connection()
        try:
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS todos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        finally:
            conn.close()

    def create(self, content: str) -> Optional[Todo]:
        """
        새로운 할 일을 데이터베이스에 추가합니다.
        :param content: 할 일 내용
        :return: 생성된 할 일 객체 또는 None
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO todos (content, status) VALUES (?, ?)",
                    (content, 'pending')
                )
                new_id = cursor.lastrowid
                
                # 방금 삽입된 행을 다시 조회하여 객체로 반환
                cursor.execute("SELECT id, content, status, created_at FROM todos WHERE id = ?", (new_id,))
                row = cursor.fetchone()
                if row:
                    return Todo(id=row[0], content=row[1], status=row[2], created_at=row[3])
            return None
        finally:
            conn.close()

    def get_all(self) -> List[Todo]:
        """
        모든 할 일 목록을 데이터베이스에서 가져옵니다.
        :return: Todo 객체 리스트
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, status, created_at FROM todos ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [Todo(id=row[0], content=row[1], status=row[2], created_at=row[3]) for row in rows]
        finally:
            conn.close()

    def update_status(self, todo_id: int, status: str) -> bool:
        """
        특정 할 일의 상태를 업데이트합니다.
        :param todo_id: 업데이트할 할 일의 ID
        :param status: 새로운 상태 ('pending' 또는 'completed')
        :return: 성공 여부
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE todos SET status = ? WHERE id = ?",
                    (status, todo_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, todo_id: int) -> bool:
        """
        특정 할 일을 데이터베이스에서 삭제합니다.
        :param todo_id: 삭제할 할 일의 ID
        :return: 성공 여부
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()

