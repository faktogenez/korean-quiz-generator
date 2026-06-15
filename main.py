import os
import glob
import asyncio
import json
from src.services.data_provider import DataProvider
from src.core.engine import QuizEngine
from src.services.audio_loader import AudioLoader
from src.renderers.moviepy_renderer import MoviePyRenderer
from src.renderers.animation_engine import AnimationEngine
from moviepy.editor import concatenate_audioclips, AudioFileClip

# =====================================================================
# РЕЖИМЫ НАСТРОЙКИ И ТЕСТИРОВАНИЯ (Управляй проектом здесь)
# =====================================================================
MODE_LAYOUT_TEST = True
MODE_FAST_VIDEO_TEST = False    
# =====================================================================

def auto_clean():
    """Автоматическое удаление временных файлов озвучки"""
    print("[Очистка] Удаляю временные аудиофайлы вопросов...")
    temp_files = glob.glob("temp_q_*.mp3")
    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass
    print("[Очистка] Проект чист!")

async def main():
    # 1. Загрузка основной базы данных слов
    words_base = DataProvider.load("data/vocabulary.json")
    if not words_base:
        print("[Ошибка] База слов пуста или не найдена!")
        return

    # 2. Применение лайфхака для быстрого теста анимации знака вопроса
    if MODE_FAST_VIDEO_TEST and not MODE_LAYOUT_TEST:
        print("💡 [Лайфхак] Включен быстрый тест видео. Берем только последний слайд квиза...")
        words_base = [words_base[-1]]

    # 3. Генерация плана (blueprint) для карточек
    blueprint = QuizEngine.create_blueprint(words_base, "templates/vertical/template.json")
    
    # 4. РЕЖИМ 1: Тестирование верстки (Генерация картинки-превью)
    if MODE_LAYOUT_TEST:
        print("=== [ТЕСТ] РЕЖИМ ПРОВЕРКИ ВЕРСТКИ ===")
        with open("templates/vertical/template.json", 'r', encoding='utf-8') as f:
            template = json.load(f)
            
        animator = AnimationEngine(template)
        # Всегда берем последнюю карточку, чтобы сразу видеть настроенный знак вопроса "?"
        test_item = blueprint[-1] 
        animator.save_test_preview(test_item, "test_card_preview.png")
        print("=== [ТЕСТ] КАРТИНКА ПРЕВЬЮ УСПЕШНО СОЗДАНА ===")
        return

    # 5. РЕЖИМ 2: Сборка полноценного видео (или быстрого тест-видео)
    print("=== ЗАПУСК КОНВЕЙЕРА СБОРКИ (DATA -> AUDIO -> VIDEO) ===")
    audio_loader = AudioLoader()
    
    print("[1/2] Синтез озвучки с динамическими фразами...")
    for i, item in enumerate(blueprint):
        path_q_en = await audio_loader.get_audio(item["q_phrase_en"], "en-US-GuyNeural")
        path_q_ko = await audio_loader.get_audio(item["korean"], "ko-KR-InJoonNeural")
        
        item["audio_question_path"] = f"temp_q_{i}.mp3"
        concatenate_audioclips([AudioFileClip(path_q_en), AudioFileClip(path_q_ko)]).write_audiofile(item["audio_question_path"])
        item["audio_answer_path"] = await audio_loader.get_audio(item["a_phrase_en"], "en-US-GuyNeural")

    print("[2/2] Рендеринг видео (Добавлен микро-шум против бана + плавные переходы)...")
    renderer = MoviePyRenderer("templates/vertical/template.json")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, renderer.render_video, blueprint, "final_output.mp4")
    
    # Автоматическая чистка мусора за собой после успешного рендеринга
    auto_clean()
    print("=== КОНВЕЙЕР УСПЕШНО ЗАВЕРШЕН! Файл: final_output.mp4 ===")

if __name__ == "__main__":
    asyncio.run(main())