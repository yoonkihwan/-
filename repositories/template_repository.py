import sqlite3

class TemplateRepository:
    def __init__(self, db_path='config.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_template(self, title, content):
        try:
            self.cursor.execute("INSERT INTO templates (title, content) VALUES (?, ?)", (title, content))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None # Title already exists

    def get_all_templates(self):
        self.cursor.execute("SELECT id, title, content FROM templates ORDER BY title")
        return self.cursor.fetchall()

    def get_template(self, template_id):
        self.cursor.execute("SELECT id, title, content FROM templates WHERE id = ?", (template_id,))
        return self.cursor.fetchone()

    def update_template(self, template_id, title, content):
        try:
            self.cursor.execute("UPDATE templates SET title = ?, content = ? WHERE id = ?", (title, content, template_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # New title already exists

    def delete_template(self, template_id):
        self.cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
