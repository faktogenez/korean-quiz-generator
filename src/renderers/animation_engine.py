import numpy as np
from PIL import Image, ImageDraw, ImageFont

class AnimationEngine:
    def __init__(self, template):
        self.template = template

    def _get_font(self, size):
        return ImageFont.truetype(self.template['meta']['font_path'], int(size))

    def draw_card(self, item, is_answer=False, correct_idx=None, timer_progress=0.0, pulse_font_size=None, anti_ban_noise=False):
        t = self.template
        width, height = t['dimensions']['width'], t['dimensions']['height']
        bg_color = item.get('custom_bg', "#1e1e2e")
        
        img = Image.new('RGB', (width, height), color=bg_color)
        
        if anti_ban_noise:
            arr = np.array(img, dtype=np.int16)
            noise = np.random.randint(-2, 3, arr.shape, dtype=np.int16)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)

        draw = ImageDraw.Draw(img)
        layout = t['layout']
        typo = t['typography']
        colors = t['colors']

        # 1. Вотермарка и Прогресс
        draw.text((width // 2, layout['y_watermark']), t['meta']['channel_name'], 
                  fill=colors['text_watermark'], anchor="mm", font=self._get_font(typo['size_watermark']))
        
        draw.text((width // 2, layout['y_progress']), item['progress_text'], 
                  fill=colors['text_progress'], anchor="mm", font=self._get_font(typo['size_progress']))

        # 2. Фраза вопроса
        draw.text((width // 2, layout['y_phrase']), item['q_phrase_en'], 
                  fill=colors['text_phrase'], anchor="mm", font=self._get_font(typo['size_phrase']))

        # 3. Корейский текст с обводкой
        draw.text(
            (width // 2, layout['y_korean']), 
            item['korean'], 
            fill=colors['text_korean'], 
            anchor="mm", 
            font=self._get_font(typo['size_korean']),
            stroke_width=layout.get('korean_stroke_width', 0),
            stroke_fill=colors.get('text_korean_stroke', "#000000")
        )
        
        draw.text((width // 2, layout['y_transcription']), f"[{item['transcription']}]", 
                  fill=colors['text_transcription'], anchor="mm", font=self._get_font(typo['size_transcription']))

        # 4. Таймер
        tm = layout['timer']
        start_x = (width - tm['width']) // 2
        draw.rectangle([start_x, tm['y'], start_x + tm['width'], tm['y'] + tm['height']], 
                       fill=colors['timer_background'])
        
        fill_width = tm['width'] * (1.0 if is_answer else timer_progress)
        draw.rectangle([start_x, tm['y'], start_x + fill_width, tm['y'] + tm['height']], 
                       fill=colors['timer_fill'])

        # 5. Варианты ответов
        opt_cfg = layout['options']
        box_start_x = (width - opt_cfg['width']) // 2
        
        for i, opt in enumerate(item['options']):
            y = opt_cfg['y_start'] + (i * opt_cfg['y_space'])
            is_correct = is_answer and (i == correct_idx) and not item.get('is_last', False)
            fill_color = colors['option_correct_bg'] if is_correct else None
            
            draw.rectangle(
                [box_start_x, y, box_start_x + opt_cfg['width'], y + opt_cfg['height']], 
                outline=colors['option_border'], 
                width=opt_cfg['border_width'], 
                fill=fill_color
            )
            text_x = box_start_x + opt_cfg['text_offset_x']
            text_y = y + opt_cfg['text_offset_y']
            draw.text((text_x, text_y), f"{chr(65+i)}. {opt}", 
                      fill=colors['text_option'], font=self._get_font(typo['size_option']))
            
        # 6. Отрисовка пульсирующего знака вопроса (Настройки из JSON)
        if item.get('is_last', False) and is_answer:
            final_font_size = pulse_font_size if pulse_font_size is not None else typo['size_pulse_question_base']
            draw.text(
                (width // 2, layout.get('pulse_question_y', 1450)), 
                "?", 
                fill=colors.get('pulse_question_mark', colors['timer_fill']), 
                anchor="mm", 
                font=self._get_font(final_font_size)
            )
            
        return img

    def save_test_preview(self, item, filename="test_card_preview.png"):
        # Превью генерирует точную статичную копию кадра интерактива
        img = self.draw_card(item, is_answer=True, correct_idx=item['correct_index'], timer_progress=1.0)
        img.save(filename)
        print(f"[Успех] Финальный тестовый кадр с интерактивом '?' сохранен: {filename}")