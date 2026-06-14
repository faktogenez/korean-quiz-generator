import random
from src.core.models import Word

class QuizEngine:
    """
    Ядро и мозг системы. Отвечает за логику формирования тестов,
    подбор ложных вариантов и расчет хронометража для видео (более 60 секунд).
    """

    @staticmethod
    def create_blueprint(words: list[Word], variant: int = 1, timer_duration: float = 3.0) -> list[dict]:
        """
        Создает текстовый сценарий (Blueprint) видео на основе выбранного варианта тестов.
        Гарантирует, что общая длительность видео будет больше 60 секунд.
        """
        if len(words) < 2:
            print("Ошибка: В базе данных должно быть минимум 2 слова для генерации ложных вариантов.")
            return []

        selected_cards = []
        total_duration = 0.0
        
        # Константы примерной длительности аудио (пока у нас нет реальных файлов)
        # Мы закладываем их с небольшим запасом, чтобы гарантировать прохождение порога в 60 сек
        APPROX_AUDIO_QUESTION = 1.5
        APPROX_AUDIO_ANSWER = 1.5
        PAUSE_BETWEEN_CARDS = 0.5
        
        # Длительность одной карточки: Вопрос + Таймер + Ответ + Пауза
        card_estimated_time = APPROX_AUDIO_QUESTION + timer_duration + APPROX_AUDIO_ANSWER + PAUSE_BETWEEN_CARDS

        # Цикл умного хронометража: набираем карточки, пока не перешагнем за 62 секунды
        # Это гарантирует монетизацию в TikTok/Reels
        while total_duration < 62.0:
            # Выбираем случайное слово, которое будет главным вопросом карточки
            main_word = random.choice(words)
            
            # Базовая структура карточки сценария
            card_data = {
                "word": main_word,
                "options": [],
                "correct_index": -1
            }

            # Логика Варианта 1: Классический тест с двумя вариантами ответов
            if variant == 1:
                # Ищем ложный ответ (дистрактор) - любое слово из базы, кроме правильного
                wrong_words = [w for w in words if w.korean != main_word.korean]
                wrong_word = random.choice(wrong_words)
                
                # Собираем варианты (английский вопрос -> корейские ответы)
                options = [main_word.korean, wrong_word.korean]
                random.shuffle(options) # Перемешиваем, чтобы правильный ответ не всегда был первым
                
                card_data["options"] = options
                card_data["correct_index"] = options.index(main_word.korean)

            # Логика Варианта 2 и 3 (Карточки запоминания без выбора вариантов)
            # Для них список options останется пустым, рендерер поймет, что нужно рисовать знак "?"
            elif variant in [2, 3]:
                card_data["options"] = []
                card_data["correct_index"] = 0

            # Добавляем карточку в наш набор и увеличиваем общий счетчик времени
            selected_cards.append(card_data)
            total_duration += card_estimated_time

        # Финальный шаг: Добавляем нумерацию (например, "1/10", "2/10") для каждой карточки
        total_cards_count = len(selected_cards)
        final_blueprint = []
        
        for index, card in enumerate(selected_cards, start=1):
            blueprint_item = {
                "progress_text": f"{index}/{total_cards_count}", # Строка вида "4/9"
                "english": card["word"].english,
                "korean": card["word"].korean,
                "transcription": card["word"].transcription,
                "options": card["options"],
                "correct_index": card["correct_index"]
            }
            final_blueprint.append(blueprint_item)

        return final_blueprint