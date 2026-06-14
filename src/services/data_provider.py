import json
from src.core.models import Word

class DataProvider:
    @staticmethod
    def load(file_path: str, topic_filter: str = None) -> list[Word]:
        words = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for item in data:
                    # Используем .get(), чтобы избежать KeyError
                    topic = item.get('topic', 'general') 
                    word = item.get('word')
                    transcription = item.get('transcription', '')
                    translation = item.get('translation')

                    # Пропускаем, если нет обязательных данных
                    if not word or not translation:
                        continue
                        
                    if topic_filter and topic != topic_filter:
                        continue
                        
                    words.append(Word(topic, word, transcription, translation))
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            
        return words