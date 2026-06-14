from PIL import Image, ImageDraw, ImageFont

class AnimationEngine:
    def __init__(self, template):
        self.template = template

    def _get_font(self, size):
        return ImageFont.truetype("assets/fonts/MalgunGothic-Bold.ttf", size)

    def draw_card(self, item, is_answer=False, correct_idx=None):
        t = self.template
        img = Image.new('RGB', (t['width'], t['height']), color=t['colors']['bg'])
        draw = ImageDraw.Draw(img)

        draw.text((t['width']//2, 80), "@KOREANQUIZEN", fill="#aaaaaa", anchor="mm", font=self._get_font(46))
        
        # Отрисовка фразы только в вопросе
        if not is_answer:
            draw.text((t['width']//2, 500), item['q_phrase_en'], fill="#ffffff", anchor="mm", font=self._get_font(60))

        draw.text((t['width']//2, 800), item['korean'], fill="white", anchor="mm", font=self._get_font(180))
        draw.text((t['width']//2, 950), f"[{item['transcription']}]", fill="#c0c0c0", anchor="mm", font=self._get_font(60))

        # ... (таймер и варианты ответов как в прошлой версии) ...
        p = t['coordinates']['progress_bar']
        draw.rectangle([p['x'], 1100, p['x'] + p['w'], 1100 + p['h']], fill="#ffffff59")
        draw.rectangle([p['x'], 1100, p['x'] + int(p['w'] * (1.0 if is_answer else 0.5)), 1100 + p['h']], fill="#38bdf8")

        for i, opt in enumerate(item['options']):
            y = 1300 + (i * 220)
            draw.rectangle([240, y, 840, y + 150], outline="white", width=3, fill="#86efac" if (is_answer and i == correct_idx) else None)
            draw.text((290, y + 40), f"{chr(65+i)}. {opt}", fill="white", font=self._get_font(64))
        return img