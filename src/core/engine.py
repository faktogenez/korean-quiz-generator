import json
import random

class QuizEngine:
    # Расширенная база шаблонов для максимальной динамики
    TEMPLATES = {
        "question": [
            "What's the meaning of?", 
            "What does this mean?", 
            "What is it in English?",
            "Can you translate this?",
            "Guess the meaning:",
            "Do you know this word?"
        ],
        "answer": [
            "The correct answer is {answer}.", 
            "It's {answer}.", 
            "That means {answer}.",
            "Correct: {answer}!",
            "Perfect! It's {answer}."
        ],
        "cta_last": [
            "Is it {opt1} or {opt2}? Write your answer in the comments!",
            "What do you think, is it {opt1} or {opt2}? Drop your guess below!",
            "Hard choice! Is it {opt1} or {opt2}? Tell me in the comments!",
            "Final round! {opt1} or {opt2}? What's your final answer? comment below!",
            "No hints this time. Is it {opt1} or {opt2}? Let me know in the comments!",
            "Can you solve this? {opt1} or {opt2}? Write inside comments!"
        ]
    }

    @staticmethod
    def create_blueprint(words_base, template_path="templates/vertical/template.json"):
        blueprint = []
        all_trans = [w.translation for w in words_base]
        total_cards = len(words_base)

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            palette = config.get("background_palette", ["#1e1e2e"])
        except Exception:
            palette = ["#1e1e2e"]

        for i, card in enumerate(words_base):
            correct_trans = card.translation
            others = [t for t in all_trans if t != correct_trans]
            distractor = random.choice(others) if others else "Wrong Option"
            
            options = [correct_trans, distractor]
            if random.random() > 0.5:
                options.reverse()
            
            is_last = (i == total_cards - 1)
            
            if is_last:
                a_phrase = random.choice(QuizEngine.TEMPLATES["cta_last"]).format(
                    opt1=options[0].upper(), 
                    opt2=options[1].upper()
                )
            else:
                a_phrase = random.choice(QuizEngine.TEMPLATES["answer"]).format(answer=correct_trans)
            
            card_bg = random.choice(palette)
            
            blueprint.append({
                "progress_text": f"{i+1} / {total_cards}",
                "korean": card.word,
                "transcription": card.transcription,
                "correct_text": correct_trans,
                "q_phrase_en": random.choice(QuizEngine.TEMPLATES["question"]),
                "a_phrase_en": a_phrase,
                "options": options,
                "correct_index": options.index(correct_trans),
                "is_last": is_last,
                "custom_bg": card_bg
            })
        return blueprint