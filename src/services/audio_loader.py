import os
import re
from gtts import gTTS

class AudioLoader:
    """
    Сервис автоматической озвучки текста с поддержкой локального кэширования.
    Предотвращает повторные запросы к API Google для уже озвученных слов.
    """
    def __init__(self, cache_dir: str = "assets/cache"):
        self.cache_dir = cache_dir
        # Автоматически создаем папку для кэша аудиофайлов, если её нет
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _sanitize_filename(self, text: str) -> str:
        """Очищает текст от спецсимволов, чтобы имя файла было корректным"""
        # Оставляем только буквы, цифры и пробелы, заменяя остальное на пустоту
        clean_text = re.sub(r'[^\w\s-]', '', text)
        # Заменяем пробелы на нижнее подчеркивание и переводим в нижний регистр
        return clean_text.strip().replace(" ", "_").lower()

    def get_audio(self, text: str, lang: str) -> str:
        """
        Принимает текст и код языка ('en' или 'ko').
        Проверяет кэш. Если файла нет — скачивает его через gTTS.
        Возвращает относительный путь к готовому .mp3 файлу.
        """
        # Формируем имя файла, например: assets/cache/en_hello.mp3
        safe_name = self._sanitize_filename(text)
        file_name = f"{lang}_{safe_name}.mp3"
        file_path = os.path.join(self.cache_dir, file_name)

        # Шаг 1: Проверяем, существует ли файл в кэше
        if os.path.exists(file_path):
            # Файл найден, возвращаем путь без повторного скачивания
            return file_path

        # Шаг 2: Если файла нет в кэше, генерируем его через Google TTS
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(file_path)
            return file_path
        except Exception as e:
            print(f"Ошибка при генерации аудио для '{text}' ({lang}): {e}")
            # Возвращаем пустую строку, чтобы рендерер знал, что звука нет, но код не падал
            return ""