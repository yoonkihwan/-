from typing import Optional, Dict


class TranslateService:
    def __init__(self):
        # Prefer deep-translator (works well on Python 3.13), fallback to googletrans if available
        self.provider = None  # 'deep' | 'googletrans' | None
        self._error: Optional[str] = None
        self.available = False
        self._langs: Dict[str, str] = {
            'auto': 'Auto Detect',
            'ko': 'Korean',
            'en': 'English',
            'ja': 'Japanese',
            'zh-cn': 'Chinese (Simplified)'
        }
        self._deep_cls = None
        self._google = None
        # Try deep-translator first
        try:
            from deep_translator import GoogleTranslator  # type: ignore
            self._deep_cls = GoogleTranslator
            # Load supported languages
            try:
                langs = GoogleTranslator.get_supported_languages(as_dict=True)
                if isinstance(langs, dict) and langs:
                    # deep-translator maps name->code; invert
                    self._langs = {v: k for k, v in langs.items()}
            except Exception:
                pass
            self.provider = 'deep'
            self.available = True
            return
        except Exception as e:
            self._error = str(e)
        # Fallback: googletrans
        try:
            from googletrans import Translator, LANGUAGES  # type: ignore
            self._google = Translator()
            self._langs = LANGUAGES  # type: ignore
            self.provider = 'googletrans'
            self.available = True
        except Exception as e:
            # Keep working app; allow UI to run without translator
            self._error = (self._error or "") + f" | googletrans: {e}"
            self.available = False

    def languages(self) -> Dict[str, str]:
        """Return mapping of language code -> English name (fallback minimal set if unavailable)."""
        return self._langs

    def detect(self, text: str) -> Optional[str]:
        if not self.available:
            return None
        if not text or not text.strip():
            return None
        try:
            if self.provider == 'deep' and self._deep_cls:
                # deep-translator has no detect API; heuristic: return None
                return None
            if self.provider == 'googletrans' and self._google:
                r = self._google.detect(text)
                return getattr(r, 'lang', None)
        except Exception:
            return None

    def translate(self, text: str, src: Optional[str] = None, dest: str = 'ko') -> str:
        """Translate text. src=None means auto-detect. Returns error message if translator unavailable."""
        if not text:
            return ''
        if not self.available:
            msg = "오류: 번역 엔진을 사용할 수 없습니다. 'pip install -r requirements.txt' 후 다시 시도하세요."
            if self._error:
                msg += f"\n세부: {self._error}"
            return msg
        try:
            if not src:
                src = 'auto'
            if self.provider == 'deep' and self._deep_cls:
                # deep-translator requires source/target codes
                translator = self._deep_cls(source=src, target=dest)
                return translator.translate(text)
            if self.provider == 'googletrans' and self._google:
                res = self._google.translate(text, src=src, dest=dest)
                return res.text
            return "오류: 사용 가능한 번역기가 없습니다."
        except Exception as e:
            # Fallback: try line-by-line for robustness
            try:
                parts = []
                for line in (text or '').splitlines():
                    if not line.strip():
                        parts.append('')
                        continue
                    if self.provider == 'deep' and self._deep_cls:
                        translator = self._deep_cls(source=src or 'auto', target=dest)
                        parts.append(translator.translate(line))
                    elif self.provider == 'googletrans' and self._google:
                        r = self._google.translate(line, src=src or 'auto', dest=dest)
                        parts.append(r.text)
                    else:
                        parts.append(line)
                return '\n'.join(parts)
            except Exception:
                return f"오류: 번역 실패 - {e}"
