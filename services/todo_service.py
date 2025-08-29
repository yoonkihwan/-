
from typing import List, Optional
from models.todo import Todo
from repositories.todo_repository import TodoRepository

class TodoService:
    """
    투두리스트 관련 비즈니스 로직을 처리합니다.
    """
    def __init__(self, repository: TodoRepository):
        """
        서비스를 초기화합니다.
        :param repository: TodoRepository의 인스턴스
        """
        self.repository = repository

    def add_todo(self, content: str) -> Optional[Todo]:
        """
        새로운 할 일을 추가합니다.
        :param content: 할 일 내용
        :return: 생성된 Todo 객체
        """
        if not content.strip():
            # 내용은 비어 있을 수 없습니다 (간단한 유효성 검사).
            return None
        return self.repository.create(content)

    def get_all_todos(self) -> List[Todo]:
        """
        모든 할 일 목록을 가져옵니다.
        :return: Todo 객체 리스트
        """
        return self.repository.get_all()

    def update_todo_status(self, todo_id: int, status: str) -> bool:
        """
        할 일의 상태를 업데이트합니다.
        :param todo_id: 할 일 ID
        :param status: 새로운 상태 ('pending' 또는 'completed')
        :return: 성공 여부
        """
        if status not in ['pending', 'completed']:
            return False
        return self.repository.update_status(todo_id, status)

    def delete_todo(self, todo_id: int) -> bool:
        """
        할 일을 삭제합니다.
        :param todo_id: 삭제할 할 일의 ID
        :return: 성공 여부
        """
        return self.repository.delete(todo_id)

    # ---- Advanced helpers (non-breaking additions) ----
    def add_todo_adv(self, content: str, parent_id: Optional[int] = None) -> Optional[Todo]:
        if not content.strip():
            return None
        if hasattr(self.repository, 'create_advanced'):
            return self.repository.create_advanced(content, parent_id)
        return self.repository.create(content)

    def get_all_todos_adv(self, status_filter: Optional[str] = None, show_archived: bool = False) -> List[Todo]:
        if hasattr(self.repository, 'get_all_advanced'):
            return self.repository.get_all_advanced(status_filter, show_archived)
        return self.repository.get_all()

    def update_todos_status_bulk(self, todo_ids: List[int], status: str) -> int:
        if status not in ['pending', 'completed']:
            return 0
        if hasattr(self.repository, 'update_status_bulk'):
            return self.repository.update_status_bulk(todo_ids, status)
        count = 0
        for tid in todo_ids:
            if self.repository.update_status(tid, status):
                count += 1
        return count

    def delete_many(self, todo_ids: List[int]) -> int:
        if hasattr(self.repository, 'delete_many'):
            return self.repository.delete_many(todo_ids)
        count = 0
        for tid in todo_ids:
            if self.repository.delete(tid):
                count += 1
        return count

    def update_sort_orders(self, parent_id: Optional[int], ordered_ids: List[int]) -> None:
        if hasattr(self.repository, 'update_sort_orders'):
            self.repository.update_sort_orders(parent_id, ordered_ids)

    def archive_completed_older_than_days(self, days: int) -> int:
        if hasattr(self.repository, 'archive_completed_older_than_days'):
            return self.repository.archive_completed_older_than_days(days)
        return 0

    def add_from_text(self, text: str, parent_id: Optional[int] = None) -> int:
        lines = [ln.strip() for ln in (text or '').splitlines()]
        items = [ln for ln in lines if ln]
        count = 0
        for ln in items:
            t = self.add_todo_adv(ln, parent_id)
            if t:
                count += 1
        return count
