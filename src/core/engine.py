import random

class QuizEngine:
    TEMPLATES = {
        "question": ["What's the meaning of?", "What does this mean?", "What is it in English?"],
        "answer": ["The correct answer is {answer}.", "It's {answer}.", "That means {answer}."]
    }

    @staticmethod
    def create_blueprint(words_base):
        blueprint = []
        all_trans = [w.translation for w in words_base]

        for i, card in enumerate(words_base):
            correct_trans = card.translation
            options = [correct_trans, random.choice([t for t in all_trans if t != correct_trans] or ["Wrong"])]
            correct_index = 0
            if random.random() > 0.5:
                options.reverse()
                correct_index = 1
            
            blueprint.append({
                "progress_text": f"{i+1} / {len(words_base)}",
                "korean": card.word,
                "transcription": card.transcription,
                "q_phrase": random.choice(QuizEngine.TEMPLATES["question"]),
                "a_phrase": random.choice(QuizEngine.TEMPLATES["answer"]).format(answer=correct_trans),
                "options": options,
                "correct_index": correct_index
            })
        return blueprint