
from dataclasses import dataclass
from typing import Optional

@dataclass
class Todo:
    """
    Todo 항목을 위한 데이터 클래스
    """
    id: int
    content: str
    status: str  # 'pending', 'completed'
    created_at: str
    sort_order: int = 0
    parent_id: Optional[int] = None
    archived_at: Optional[str] = None
