
import pyperclip
from tkinter import Tk

class ClipboardService:
    """
    클립보드 히스토리를 관리하고, 클립보드 변경을 감지합니다.
    """
    def __init__(self, root: Tk, on_change_callback=None):
        """
        서비스를 초기화합니다.
        :param root: Tkinter의 루트 창 (after 메서드 사용을 위해)
        :param on_change_callback: 클립보드 히스토리가 변경될 때 호출될 콜백 함수
        """
        self.root = root
        self.on_change_callback = on_change_callback
        self.history = []
        self.max_history_size = 50
        self._last_clipboard_content = ""
        self._is_monitoring = False

    def start_monitoring(self):
        """클립보드 모니터링을 시작합니다."""
        if not self._is_monitoring:
            self._is_monitoring = True
            self._last_clipboard_content = self._get_clipboard_content()
            self._check_clipboard()

    def stop_monitoring(self):
        """클립보드 모니터링을 중지합니다."""
        self._is_monitoring = False

    def _get_clipboard_content(self):
        """현재 클립보드 내용을 가져옵니다."""
        try:
            return self.root.clipboard_get()
        except Exception:
            try:
                return pyperclip.paste()
            except pyperclip.PyperclipException:
                return ""

    def _check_clipboard(self):
        """주기적으로 클립보드를 확인하고 변경 사항을 처리합니다."""
        if not self._is_monitoring:
            return

        try:
            current_content = self._get_clipboard_content()
            if current_content and current_content != self._last_clipboard_content:
                self._last_clipboard_content = current_content
                
                # 중복 항목이 맨 위에 있는 경우 추가하지 않음
                if not self.history or self.history[0] != current_content:
                    self.history.insert(0, current_content)
                    
                    # 최대 히스토리 크기 유지
                    if len(self.history) > self.max_history_size:
                        self.history.pop()

                    if self.on_change_callback:
                        self.on_change_callback()
        except Exception as e:
            print(f"클립보드 확인 중 오류 발생: {e}") # 로깅으로 대체하는 것이 좋음
        finally:
            self.root.after(1000, self._check_clipboard) # 1초마다 확인

    def get_history(self) -> list:
        """현재 클립보드 히스토리를 반환합니다."""
        return self.history

    def copy_to_clipboard(self, text: str):
        """주어진 텍스트를 클립보드에 복사합니다."""
        pyperclip.copy(text)
        # 사용자가 히스토리에서 항목을 복사할 때, 그게 다시 히토리에 추가되는 것을 방지
        self._last_clipboard_content = text
