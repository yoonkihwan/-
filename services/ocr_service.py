
import pytesseract
from PIL import Image

class OCRService:
    """
    Tesseract를 사용하여 이미지에서 텍스트를 추출합니다.
    """
    def __init__(self, tesseract_cmd_path=None):
        """
        OCR 서비스를 초기화합니다.
        :param tesseract_cmd_path: Tesseract 실행 파일의 경로 (선택 사항)
        """
        # Tesseract가 시스템 PATH에 설치되지 않은 경우, 아래 경로를 지정해야 합니다.
        # 예: 'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

    def extract_text_from_image(self, image_path: str) -> str:
        """
        주어진 이미지 파일에서 텍스트를 추출합니다.
        :param image_path: 텍스트를 추출할 이미지의 파일 경로
        :return: 추출된 텍스트
        """
        try:
            img = Image.open(image_path)
            # 한글+영어 인식을 위해 lang='kor+eng' 설정
            text = pytesseract.image_to_string(img, lang='kor+eng')
            return text
        except FileNotFoundError:
            return "오류: 이미지 파일을 찾을 수 없습니다."
        except Exception as e:
            # Tesseract가 설치되지 않았거나 경로가 잘못된 경우 오류가 발생할 수 있습니다.
            error_message = str(e)
            if "Tesseract is not installed" in error_message:
                return "오류: Tesseract가 설치되지 않았거나 경로가 올바르지 않습니다. PATH를 확인해주세요."
            return f"알 수 없는 OCR 오류 발생: {error_message}"
