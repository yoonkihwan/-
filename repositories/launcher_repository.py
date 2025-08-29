import sqlite3

class LauncherRepository:
    def __init__(self, db_path='config.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.upgrade_schema()
        self.create_tables()

    def upgrade_schema(self):
        # launcher_items 테이블의 스키마를 확인하여 'url' 타입이 없는 구버전인지 확인
        self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='launcher_items'")
        result = self.cursor.fetchone()
        if result and "CHECK(item_type IN ('file', 'folder'))" in result[0]:
            print("Upgrading launcher_items table schema...")
            # 1. 기존 테이블 이름 변경
            self.cursor.execute("ALTER TABLE launcher_items RENAME TO launcher_items_old")
            
            # 2. 새로운 스키마로 테이블 재생성
            self.create_tables()

            # 3. 데이터 복사 (workspace_id가 없을 수 있으므로 예외 처리)
            self.cursor.execute("PRAGMA table_info(launcher_items_old)")
            cols = [info[1] for info in self.cursor.fetchall()]
            col_names = ", ".join(cols)
            q_marks = ", ".join(["?"] * len(cols))

            self.cursor.execute(f"SELECT {col_names} FROM launcher_items_old")
            old_data = self.cursor.fetchall()

            for row in old_data:
                self.cursor.execute(f"INSERT INTO launcher_items ({col_names}) VALUES ({q_marks})", row)

            # 4. 기존 테이블 삭제
            self.cursor.execute("DROP TABLE launcher_items_old")
            self.conn.commit()
            print("Schema upgrade complete.")

    def create_tables(self):
        # 작업 공간 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        # 실행 항목 테이블 (URL 타입 추가)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS launcher_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                item_type TEXT NOT NULL CHECK(item_type IN ('file', 'folder', 'url')),
                workspace_id INTEGER,
                FOREIGN KEY (workspace_id) REFERENCES workspaces (id)
            )
        ''')
        self.conn.commit()

    # --- Workspace Methods ---
    def add_workspace(self, name):
        try:
            self.cursor.execute("INSERT INTO workspaces (name) VALUES (?)", (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_all_workspaces(self):
        self.cursor.execute("SELECT id, name FROM workspaces ORDER BY name")
        return self.cursor.fetchall()

    def delete_workspace(self, workspace_id):
        self.cursor.execute("DELETE FROM launcher_items WHERE workspace_id = ?", (workspace_id,))
        self.cursor.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
        self.conn.commit()

    # --- Item Methods ---
    def add_item(self, name, path, item_type, workspace_id):
        self.cursor.execute(
            "INSERT INTO launcher_items (name, path, item_type, workspace_id) VALUES (?, ?, ?, ?)",
            (name, path, item_type, workspace_id)
        )
        self.conn.commit()

    def get_items_by_workspace(self, workspace_id):
        self.cursor.execute(
            "SELECT id, name, path, item_type FROM launcher_items WHERE workspace_id = ? ORDER BY name",
            (workspace_id,)
        )
        return self.cursor.fetchall()

    def delete_item(self, item_id):
        self.cursor.execute("DELETE FROM launcher_items WHERE id = ?", (item_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
