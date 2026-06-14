from abc import ABC, abstractmethod

class BaseRenderer(ABC):
    """
    Абстрактный базовый класс (интерфейс) для всех будущих видео-рендереров.
    Любой класс дизайна на любой ветке Git обязан наследоваться от него
    и реализовывать метод render_video.
    """
    
    @abstractmethod
    def render_video(self, blueprint: list[dict], output_path: str, timer_duration: float) -> None:
        """
        Метод, который превращает текстовый сценарий (blueprint) в готовый MP4 файл.
        
        :param blueprint: Список карточек-вопросов, сгенерированный QuizEngine
        :param output_path: Путь для сохранения готового видео-файла
        :param timer_duration: Длительность отображения таймера на экране
        """
        pass