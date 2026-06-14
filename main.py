from src.services.data_provider import DataProvider
from src.core.engine import QuizEngine
from src.services.audio_loader import AudioLoader

# --- ГЛАВНЫЙ ПУЛЬТ УПРАВЛЕНИЯ КОНВЕЙЕРОМ ---
SETTINGS = {
    "variant": 1,                       # 1 - Классический тест, 2 или 3 - Карточка запоминания
    "data_file": "data/vocabulary.json",# Путь к базе слов
    "timer_duration": 3.0,              # Сколько секунд длится таймер
    "output_name": "tiktok_output.mp4"  # Имя финального видео
}

def main():
    print("=== ЗАПУСК ВИДЕО-КОНВЕЙЕРА (ВЕТКА MAIN) ===")
    
    # Шаг 1: Загружаем корейско-английскую базу данных
    print(f"[1/4] Загрузка слов из файла {SETTINGS['data_file']}...")
    words_base = DataProvider.load(SETTINGS["data_file"])
    print(f"Успешно загружено слов: {len(words_base)}")
    
    if not words_base:
        print("Ошибка: База данных пуста. Завершение работы.")
        return

    # Шаг 2: Движок генерирует чертеж теста длительностью более 60 секунд
    print("[2/4] Генерация умного сценария для TikTok (>60 секунд)...")
    blueprint = QuizEngine.create_blueprint(
        words=words_base, 
        variant=SETTINGS["variant"], 
        timer_duration=SETTINGS["timer_duration"]
    )
    print(f"Сценарий успешно создан! Всего карточек в видео: {len(blueprint)}")

    # Шаг 3: Сервис озвучки проверяет кэш и скачивает недостающие .mp3
    print("[3/4] Проверка кэша аудио и автоматическая генерация озвучки через gTTS...")
    audio_service = AudioLoader()
    
    for index, item in enumerate(blueprint, start=1):
        print(f"  Озвучка карточки {item['progress_text']}: '{item['english']}' и '{item['korean']}'...")
        # Скачиваем/проверяем английскую озвучку для вопроса
        item["audio_question_path"] = audio_service.get_audio(item["english"], "en")
        # Скачиваем/проверяем корейскую озвучку для правильного ответа
        item["audio_answer_path"] = audio_service.get_audio(item["korean"], "ko")

    # Шаг 4: Имитация рендеринга (На ветке main мы просто проверяем логику сборки пакета)
    print("[4/4] Сборка пакета данных завершена.")
    print("\n=== ГОТОВЫЙ ЧЕРТЕЖ ДЛЯ ВИДЕОРЕНДЕРА (BLUEPRINT) ===")
    for item in blueprint:
        print(f"\nКарточка: {item['progress_text']}")
        print(f"  Вопрос (EN): {item['english']} -> Аудио: {item['audio_question_path']}")
        print(f"  Ответ (KO): {item['korean']} {item['transcription']} -> Аудио: {item['audio_answer_path']}")
        if item['options']:
            print(f"  Варианты ответов: {item['options']} (Индекс правильного: {item['correct_index']})")
    
    print("\nЛогическое ядро отработало штатно. Пакет готов к передаче в MoviePy на дизайн-ветках.")

if __name__ == "__main__":
    main()