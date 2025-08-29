from typing import Optional, Dict
from googletrans import Translator, LANGUAGES


class TranslateService:
    def __init__(self):
        self.translator = Translator()

    def languages(self) -> Dict[str, str]:
        """Return mapping of language code -> English name."""
        return LANGUAGES

    def detect(self, text: str) -> Optional[str]:
        try:
            if not text or not text.strip():
                return None
            r = self.translator.detect(text)
            return getattr(r, 'lang', None)
        except Exception:
            return None

    def translate(self, text: str, src: Optional[str] = None, dest: str = 'ko') -> str:
        """Translate text. src=None means auto-detect."""
        if not text:
            return ''
        try:
            if not src:
                src = 'auto'
            res = self.translator.translate(text, src=src, dest=dest)
            return res.text
        except Exception as e:
            # Fallback: try line-by-line for robustness
            try:
                parts = []
                for line in (text or '').splitlines():
                    if not line.strip():
                        parts.append('')
                        continue
                    r = self.translator.translate(line, src=src or 'auto', dest=dest)
                    parts.append(r.text)
                return '\n'.join(parts)
            except Exception:
                return f"오류: 번역 실패 - {e}"

