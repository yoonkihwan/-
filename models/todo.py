
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Todo:
    """
    Todo 항목을 위한 데이터 클래스
    """
    id: int
    content: str
    status: str  # 'pending', 'completed'
    created_at: str

