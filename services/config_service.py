
import json
import os

class ConfigService:
    """
    JSON 설정 파일을 관리합니다.
    """
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        if not os.path.exists(self.config_path):
            # 기본 설정으로 파일 생성
            self._save_config({"screenshot_save_dir": "screenshots"})
        
        self.config = self._load_config()

    def _load_config(self):
        """설정 파일에서 데이터를 로드합니다."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_config(self, data):
        """설정 파일에 데이터를 저장합니다."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get(self, key):
        """
        설정에서 키에 해당하는 값을 가져옵니다.
        :param key: 가져올 값의 키
        :return: 키에 해당하는 값 또는 None
        """
        return self.config.get(key)

    def set(self, key, value):
        """
        설정 값을 지정하고 파일에 저장합니다.
        :param key: 설정할 값의 키
        :param value: 설정할 값
        """
        self.config[key] = value
        self._save_config(self.config)
