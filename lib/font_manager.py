import os
from typing import Dict, Optional


class FontManager:

    def __init__(self, folder: str):
        self.fonts_by_name: Dict[str, str] = {}
        for dir_path, dir_names, file_names in os.walk(folder):
            for file_name in file_names:
                base_name, extension = os.path.splitext(file_name)
                if extension.lower() in ['.otf', '.ttf']:
                    file_path = os.path.join(dir_path, file_name)
                    self.fonts_by_name[base_name.lower()] = file_path

    def get_font(self, name: str) -> Optional[str]:
        return self.fonts_by_name.get(name.lower())
