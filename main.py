import asyncio
from src.services.data_provider import DataProvider
from src.core.engine import QuizEngine
from src.services.audio_loader import AudioLoader
from src.renderers.moviepy_renderer import MoviePyRenderer
from moviepy.editor import concatenate_audioclips, AudioFileClip

async def main():
    print("=== ЗАПУСК ПОЛНОГО КОНВЕЙЕРА (DATA -> AUDIO -> VIDEO) ===")
    
    words_base = DataProvider.load("data/vocabulary.json")
    blueprint = QuizEngine.create_blueprint(words_base)
    audio_loader = AudioLoader()
    
    print("[1/2] Генерация/Проверка озвучки...")
    for i, item in enumerate(blueprint):
        # Озвучиваем английскую фразу (Голос Guy) и корейское слово (Голос InJoon)
        path_q_en = await audio_loader.get_audio(item["q_phrase_en"], "en-US-GuyNeural")
        path_q_ko = await audio_loader.get_audio(item["korean"], "ko-KR-InJoonNeural")
        
        # Генерируем уникальные имена для сшитых аудиофайлов вопросов
        item["audio_question_path"] = f"temp_q_{i}.mp3"
        concatenate_audioclips([AudioFileClip(path_q_en), AudioFileClip(path_q_ko)]).write_audiofile(item["audio_question_path"])
        
        # Озвучиваем фразу ответа на английском языке (Голос Guy)
        item["audio_answer_path"] = await audio_loader.get_audio(item["a_phrase_en"], "en-US-GuyNeural")
        
        item["duration_en"] = AudioFileClip(item["audio_question_path"]).duration
        item["duration_ko"] = AudioFileClip(item["audio_answer_path"]).duration

    print("[2/2] Сборка финального видео...")
    renderer = MoviePyRenderer("templates/vertical/template.json")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, renderer.render_video, blueprint, "final_output.mp4")
    print("=== КОНВЕЙЕР УСПЕШНО ЗАВЕРШЕН ===")

if __name__ == "__main__":
    asyncio.run(main())