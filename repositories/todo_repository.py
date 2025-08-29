
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
        # Ensure new columns exist for advanced features
        self._migrate()

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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sort_order INTEGER DEFAULT 0,
                        parent_id INTEGER NULL,
                        archived_at TIMESTAMP NULL
                    )
                ''')
        finally:
            conn.close()

    def _migrate(self):
        """Add missing columns for older databases (SQLite ALTER TABLE ADD COLUMN is idempotent)."""
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                for sql in (
                    "ALTER TABLE todos ADD COLUMN sort_order INTEGER DEFAULT 0",
                    "ALTER TABLE todos ADD COLUMN parent_id INTEGER NULL",
                    "ALTER TABLE todos ADD COLUMN archived_at TIMESTAMP NULL",
                ):
                    try:
                        cur.execute(sql)
                    except Exception:
                        # Ignore if column already exists
                        pass
        finally:
            conn.close()

    # --- Advanced CRUD helpers ---
    def create_advanced(self, content: str, parent_id: Optional[int] = None):
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                # next sort order within same parent
                if parent_id is None:
                    cur.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM todos WHERE parent_id IS NULL AND archived_at IS NULL")
                else:
                    cur.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM todos WHERE parent_id = ? AND archived_at IS NULL", (parent_id,))
                next_order = cur.fetchone()[0] or 1

                cur.execute(
                    "INSERT INTO todos (content, status, sort_order, parent_id) VALUES (?, 'pending', ?, ?)",
                    (content, next_order, parent_id)
                )
                new_id = cur.lastrowid
                cur.execute("SELECT id, content, status, created_at, sort_order, parent_id, archived_at FROM todos WHERE id = ?", (new_id,))
                row = cur.fetchone()
                if row:
                    return Todo(id=row[0], content=row[1], status=row[2], created_at=row[3], sort_order=row[4], parent_id=row[5], archived_at=row[6])
                return None
        finally:
            conn.close()

    def get_all_advanced(self, status_filter: Optional[str] = None, show_archived: bool = False) -> List[Todo]:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                q = "SELECT id, content, status, created_at, sort_order, parent_id, archived_at FROM todos"
                clauses = []
                params = []
                if not show_archived:
                    clauses.append("archived_at IS NULL")
                if status_filter in ('pending','completed'):
                    clauses.append("status = ?")
                    params.append(status_filter)
                if clauses:
                    q += " WHERE " + " AND ".join(clauses)
                q += " ORDER BY COALESCE(parent_id, id) ASC, sort_order ASC, created_at ASC"
                cur.execute(q, params)
                rows = cur.fetchall()
                return [Todo(id=r[0], content=r[1], status=r[2], created_at=r[3], sort_order=r[4], parent_id=r[5], archived_at=r[6]) for r in rows]
        finally:
            conn.close()

    def update_status_bulk(self, todo_ids: List[int], status: str) -> int:
        if not todo_ids:
            return 0
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                qmarks = ",".join(["?"]*len(todo_ids))
                cur.execute(f"UPDATE todos SET status = ? WHERE id IN ({qmarks})", [status, *todo_ids])
                return cur.rowcount
        finally:
            conn.close()

    def delete_many(self, todo_ids: List[int]) -> int:
        if not todo_ids:
            return 0
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                qmarks = ",".join(["?"]*len(todo_ids))
                cur.execute(f"DELETE FROM todos WHERE id IN ({qmarks})", todo_ids)
                return cur.rowcount
        finally:
            conn.close()

    def update_sort_orders(self, parent_id: Optional[int], ordered_ids: List[int]) -> None:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                for idx, tid in enumerate(ordered_ids, start=1):
                    cur.execute("UPDATE todos SET sort_order = ? WHERE id = ?", (idx, tid))
        finally:
            conn.close()

    def archive_completed_older_than_days(self, days: int) -> int:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE todos SET archived_at = CURRENT_TIMESTAMP WHERE archived_at IS NULL AND status = 'completed' AND created_at < datetime('now', ?)",
                    (f'-{int(days)} days',)
                )
                return cur.rowcount
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
