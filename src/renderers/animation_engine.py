from PIL import Image, ImageDraw, ImageFont

class AnimationEngine:
    def __init__(self, template):
        self.template = template

    def _get_font(self, size):
        # Используем путь к шрифту, который точно есть в твоем проекте
        return ImageFont.truetype("assets/fonts/MalgunGothic-Bold.ttf", size)

    def draw_card(self, item, is_answer=False, correct_idx=None, timer_progress=0.0):
        t = self.template
        width, height = t['width'], t['height']
        img = Image.new('RGB', (width, height), color=t['colors']['bg'])
        draw = ImageDraw.Draw(img)

        # 1. Заголовок
        draw.text((width//2, 80), "@KOREANQUIZEN", fill="#aaaaaa", anchor="mm", font=self._get_font(46))
        
        # 2. Фраза вопроса (рисуем всегда, если не ответ)
        if not is_answer:
            draw.text((width//2, 500), item['q_phrase_en'], fill="#ffffff", anchor="mm", font=self._get_font(60))

        # 3. Слово и транскрипция
        draw.text((width//2, 800), item['korean'], fill="white", anchor="mm", font=self._get_font(180))
        draw.text((width//2, 950), f"[{item['transcription']}]", fill="#c0c0c0", anchor="mm", font=self._get_font(60))

        # 4. Таймер (Укоротили ширину: было 880, ставим 700)
        p = t['coordinates']['progress_bar']
        start_x = (width - 700) // 2
        draw.rectangle([start_x, 1100, start_x + 700, 1100 + p['h']], fill="#ffffff59")
        # Анимация роста
        fill_width = 700 * (1.0 if is_answer else timer_progress)
        draw.rectangle([start_x, 1100, start_x + fill_width, 1100 + p['h']], fill="#38bdf8")

        # 5. Ответы
        for i, opt in enumerate(item['options']):
            y = 1300 + (i * 220)
            draw.rectangle([240, y, 840, y + 150], outline="white", width=3, 
                           fill="#86efac" if (is_answer and i == correct_idx) else None)
            draw.text((290, y + 40), f"{chr(65+i)}. {opt}", fill="white", font=self._get_font(64))
        return img