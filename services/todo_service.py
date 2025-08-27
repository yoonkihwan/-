
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

