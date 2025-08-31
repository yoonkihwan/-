import tkinter as tk
from tkinter import ttk


class ScreenshotFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self):
        lf = tk.LabelFrame(self, text="스크린샷 & OCR")
        lf.pack(fill=tk.X, padx=5, pady=10)

        tk.Button(lf, text="전체 화면 캡처", command=self.app.capture_fullscreen).pack(fill=tk.X, padx=6, pady=6)
        tk.Button(lf, text="영역 선택 캡처", command=self.app.capture_region).pack(fill=tk.X, padx=6, pady=6)
        tk.Button(lf, text="영역 캡처 + OCR", command=self.app.capture_and_ocr).pack(fill=tk.X, padx=6, pady=6)

        # 자동 후처리
        auto = tk.LabelFrame(self, text="OCR 자동 처리")
        auto.pack(fill=tk.X, padx=5, pady=10)
        tk.Button(auto, text="영역 캡처 → OCR → 복사", command=self._region_ocr_copy).pack(fill=tk.X, padx=6, pady=4)
        tk.Button(auto, text="영역 캡처 → OCR → Todo 추가", command=self._region_ocr_todo).pack(fill=tk.X, padx=6, pady=4)
        tk.Button(auto, text="영역 캡처 → OCR → 번역(→ 복사)", command=self._region_ocr_translate).pack(fill=tk.X, padx=6, pady=4)

        # 번역 자동 처리 버튼 제거(요구 사항에 따라 숨김)
        try:
            for w in auto.winfo_children():
                try:
                    if isinstance(w, tk.Button) and ('번역' in str(w.cget('text'))):
                        w.destroy()
                except Exception:
                    pass
        except Exception:
            pass

    # --- helpers ---
    def _region_ocr_copy(self):
        try:
            # 최소화 후 약간 지연하여 영역 캡처 → OCR → 복사
            self.app.wm_state('iconic')
        except Exception:
            pass
        def task():
            try:
                path = self.app.screenshot_service.capture_region()
                if not path:
                    self.app.update_status("캡처가 취소되었습니다")
                    return
                text = self._ocr_extract(path)
                if text is None:
                    return
                self.app.clipboard_clear()
                self.app.clipboard_append(text)
                self.app.update_status("OCR 결과를 클립보드에 복사했습니다")
            finally:
                try:
                    self.app.wm_state('normal')
                except Exception:
                    pass
        self.after(200, task)

    def _region_ocr_todo(self):
        try:
            self.app.wm_state('iconic')
        except Exception:
            pass
        def task():
            try:
                path = self.app.screenshot_service.capture_region()
                if not path:
                    self.app.update_status("캡처가 취소되었습니다")
                    return
                text = self._ocr_extract(path)
                if text is None or not text.strip():
                    return
                if hasattr(self.app.todo_service, 'add_from_text'):
                    count = self.app.todo_service.add_from_text(text)
                    self.app.update_status(f"TODO {count}개 추가")
                else:
                    self.app.todo_service.add_todo(text.strip())
                    self.app.update_status("TODO 1개 추가")
                if hasattr(self.app, 'todo_frame'):
                    self.app.todo_frame.refresh_todos()
            finally:
                try:
                    self.app.wm_state('normal')
                except Exception:
                    pass
        self.after(200, task)

    def _region_ocr_translate(self, dest: str = 'ko'):
        try:
            self.app.wm_state('iconic')
        except Exception:
            pass
        def task():
            try:
                path = self.app.screenshot_service.capture_region()
                if not path:
                    self.app.update_status("캡처가 취소되었습니다")
                    return
                text = self._ocr_extract(path)
                if text is None:
                    return
                translated = self.app.translate_service.translate(text, src=None, dest=dest)
                self.app.clipboard_clear()
                self.app.clipboard_append(translated)
                self.app.update_status("번역 결과를 클립보드에 복사했습니다")
            finally:
                try:
                    self.app.wm_state('normal')
                except Exception:
                    pass
        self.after(200, task)

    def _ocr_extract(self, path: str):
        try:
            svc = self.app.ocr_service or None
        except Exception:
            svc = None
        try:
            if svc is None:
                from services.ocr_service import OCRService  # lazy import
                svc = OCRService(tesseract_cmd_path=self.app.config_service.get('tesseract_cmd_path'))
                self.app.ocr_service = svc
            text = svc.extract_text_from_image(path)
            # 오류 포맷 방지(문구 시작이 오류: 인 경우)
            if isinstance(text, str) and text.strip().lower().startswith("오류:"):
                from tkinter import messagebox
                messagebox.showerror("OCR 오류", text)
                return None
            return text or ''
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("OCR 오류", f"처리 실패: {e}")
            return None
