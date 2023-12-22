import re
class SenitizePath():
    def senitize_path(self, path):
        input_path = re.sub(r'[^\w\s./-]', '', path).strip()
        sanitized_input_gif = re.sub(r'[-\s]+', '_', input_path)
        return sanitized_input_gif