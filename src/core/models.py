class Word:
    """
    Класс-модель, представляющий одну словарную пару с учетом темы.
    """
    def __init__(self, topic: str, word: str, transcription: str, translation: str):
        self.topic = topic               # Категория (например, "colors")
        self.word = word                 # Слово на корейском
        self.transcription = transcription # Транскрипция
        self.translation = translation   # Перевод на английский

    def __repr__(self):
        return f"<Word: {self.word} ({self.topic})>"