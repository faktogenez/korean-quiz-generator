import asyncio
import json
from src.services.data_provider import DataProvider
from src.core.engine import QuizEngine
from src.services.audio_loader import AudioLoader
from src.renderers.moviepy_renderer import MoviePyRenderer
from src.renderers.animation_engine import AnimationEngine
from moviepy.editor import concatenate_audioclips, AudioFileClip

# ==========================================
# РЕЖИМ ПРОВЕРКИ КАРТИНКИ (ВЕРСТКИ)
# True — только картинка-превью с подсвеченным правильным ответом.
# False — сборка полноценного видео.
TEST_MODE = True 
# ==========================================

async def main():
    words_base = DataProvider.load("data/vocabulary.json")
# Измени эту строчку в файле main.py (она находится в районе 16-й строки)
    blueprint = QuizEngine.create_blueprint(words_base, "templates/vertical/template.json")    
    if TEST_MODE:
        print("=== РЕЖИМ ТЕСТИРОВАНИЯ ВЕРСТКИ ===")
        with open("templates/vertical/template.json", 'r', encoding='utf-8') as f:
            template = json.load(f)
            
        animator = AnimationEngine(template)
        # Для теста берем первую карточку (она гарантированно подсветит верный ответ)
        test_item = blueprint[0]
        animator.save_test_preview(test_item, "test_card_preview.png")
        print("=== ТЕСТ ЗАВЕРШЕН, ВИДЕО НЕ СБИРАЛОСЬ ===")
        return

    print("=== ЗАПУСК ПОЛНОГО КОНВЕЙЕРА (DATA -> AUDIO -> VIDEO) ===")
    audio_loader = AudioLoader()
    
    print("[1/2] Генерация/Проверка озвучки...")
    for i, item in enumerate(blueprint):
        path_q_en = await audio_loader.get_audio(item["q_phrase_en"], "en-US-GuyNeural")
        path_q_ko = await audio_loader.get_audio(item["korean"], "ko-KR-InJoonNeural")
        
        item["audio_question_path"] = f"temp_q_{i}.mp3"
        concatenate_audioclips([AudioFileClip(path_q_en), AudioFileClip(path_q_ko)]).write_audiofile(item["audio_question_path"])
        item["audio_answer_path"] = await audio_loader.get_audio(item["a_phrase_en"], "en-US-GuyNeural")

    print("[2/2] Сборка финального видео...")
    renderer = MoviePyRenderer("templates/vertical/template.json")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, renderer.render_video, blueprint, "final_output.mp4")
    print("=== КОНВЕЙЕР УСПЕШНО ЗАВЕРШЕН ===")

if __name__ == "__main__":
    asyncio.run(main())