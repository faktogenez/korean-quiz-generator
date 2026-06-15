from PIL import Image, ImageDraw, ImageFont

class AnimationEngine:
    def __init__(self, template):
        self.template = template

    def _get_font(self, size):
        return ImageFont.truetype("assets/fonts/MalgunGothic-Bold.ttf", size)

    def draw_card(self, item, is_answer=False, correct_idx=None, timer_progress=0.0):
        t = self.template
        width, height = t['width'], t['height']
        img = Image.new('RGB', (width, height), color=t['colors']['bg'])
        draw = ImageDraw.Draw(img)

        # 1. Заголовок и Счетчик карточек
        draw.text((width // 2, 80), "@KOREANQUIZEN", fill="#aaaaaa", anchor="mm", font=self._get_font(46))
        draw.text((width // 2, 200), item['progress_text'], fill="#a0a0a0", anchor="mm", font=self._get_font(70))

        # 2. Фраза вопроса
        draw.text((width // 2, 500), item['q_phrase_en'], fill="#ffffff", anchor="mm", font=self._get_font(60))

        # 3. Слово на корейском и транскрипция
        draw.text((width // 2, 800), item['korean'], fill="white", anchor="mm", font=self._get_font(180))
        draw.text((width // 2, 950), f"[{item['transcription']}]", fill="#c0c0c0", anchor="mm", font=self._get_font(60))

        # 4. Прогресс-бар таймера
        p = t['coordinates']['progress_bar']
        start_x = (width - 700) // 2
        draw.rectangle([start_x, 1100, start_x + 700, 1100 + p['h']], fill="#ffffff59")
        fill_width = 700 * (1.0 if is_answer else timer_progress)
        draw.rectangle([start_x, 1100, start_x + fill_width, 1100 + p['h']], fill="#38bdf8")

        # 5. Варианты ответов
        for i, opt in enumerate(item['options']):
            y = 1300 + (i * 220)
            is_correct = is_answer and (i == correct_idx) and not item.get('is_last', False)
            fill_color = "#86efac" if is_correct else None
            
            draw.rectangle([240, y, 840, y + 150], outline="white", width=3, fill=fill_color)
            draw.text((290, y + 40), f"{chr(65+i)}. {opt}", fill="white", font=self._get_font(64))
            
        return img