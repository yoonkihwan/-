
import tkinter as tk
import mss
from PIL import Image
from datetime import datetime
import os
from services.config_service import ConfigService

class ScreenshotService:
    """
    스크린샷 캡처 관련 로직을 처리합니다.
    """
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self._last_region = None  # 마지막으로 선택한 캡처 영역 저장

    def _get_timestamp_path(self, extension=".png"):
        """타임스탬프를 기반으로 한 파일 저장 경로를 반환합니다."""
        save_dir = self.config_service.get("screenshot_save_dir")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(save_dir, f"capture_{timestamp}{extension}")

    def capture_fullscreen(self) -> str:
        """
        전체 화면을 캡처하고 파일로 저장합니다.
        :return: 저장된 파일의 경로
        """
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[0]) # 모든 모니터 포함
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            filepath = self._get_timestamp_path()
            img.save(filepath)
            return filepath

    def capture_region(self) -> str:
        """
        사용자가 선택한 영역을 캡처하고 파일로 저장합니다.
        :return: 저장된 파일의 경로 또는 빈 문자열
        """
        # 영역 선택을 위한 오버레이 창 생성
        overlay = _RegionSelector()
        region = overlay.get_selected_region()

        if not region or region["width"] <= 0 or region["height"] <= 0:
            return "" # 캡처 취소

        with mss.mss() as sct:
            sct_img = sct.grab(region)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            filepath = self._get_timestamp_path()
            img.save(filepath)
            # 마지막 영역 기억
            self._last_region = region
            return filepath

    def capture_last_region(self) -> str:
        """
        직전에 선택한 영역을 다시 캡처한다. 이전 영역이 없으면 빈 문자열 반환.
        :return: 저장된 파일 경로 또는 빈 문자열
        """
        if not self._last_region:
            return ""
        region = self._last_region
        if not region or region.get("width", 0) <= 0 or region.get("height", 0) <= 0:
            return ""
        with mss.mss() as sct:
            sct_img = sct.grab(region)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            filepath = self._get_timestamp_path()
            img.save(filepath)
            return filepath


class _RegionSelector(tk.Toplevel):
    """스크린샷 영역 선택을 위한 투명 오버레이 창 클래스"""
    def __init__(self):
        super().__init__()
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = {}

        # Toplevel 창 설정
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.3) # 투명도
        self.attributes("-topmost", True) # 항상 위에 표시
        self.overrideredirect(True) # 창 테두리 제거

        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # ESC 키로 취소
        self.bind("<Escape>", lambda e: self.destroy())
        
        self.wait_window(self)

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        self.region = {"top": int(top), "left": int(left), "width": int(width), "height": int(height)}
        self.destroy()

    def get_selected_region(self):
        return self.region
