import json
import random
import colorsys
import os
import urllib.request
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip

class PreviewEngine:
    def __init__(self, template_path=None):
        if template_path is None:
            base_dir = os.path.dirname(__file__)
            template_path = os.path.join(base_dir, 'preview_template.json')
            
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)
            
        self.width = self.template['dimensions']['width']
        self.height = self.template['dimensions']['height']
        
        # Счетчик для циклического перебора пастельных цветов фона
        self.color_cycle_index = 0
        
        self._ensure_audio_files()
        self._ensure_flag_file()
        
    def _get_phrase_audio_path(self, phrase):
        clean_hash = hashlib.md5(phrase.encode('utf-8')).hexdigest()[:12]
        return os.path.join("assets/audio", f"phrase_{clean_hash}.mp3")

    def _ensure_audio_files(self):
        audio_dir = "assets/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        korean_words = {"count_1.mp3": "하나", "count_2.mp3": "둘", "count_3.mp3": "셋"}
        missing_kor = [f for f in korean_words.keys() if not os.path.exists(os.path.join(audio_dir, f))]
        
        toggles = self.template.get('features_toggles', {})
        missing_eng_phrases = []
        if toggles.get('play_phrase_voiceover', True):
            for phrase in self.template['catchy_phrases']:
                p_path = self._get_phrase_audio_path(phrase)
                if not os.path.exists(p_path):
                    missing_eng_phrases.append((phrase, p_path))
                    
        if missing_kor or missing_eng_phrases:
            try:
                from gtts import gTTS
            except ImportError:
                import subprocess, sys
                print("📦 Установка библиотеки gTTS для генерации озвучки...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "gtts"])
                from gtts import gTTS
                
            for filename in missing_kor:
                text = korean_words[filename]
                path = os.path.join(audio_dir, filename)
                gTTS(text=text, lang='ko').save(path)
                
            for phrase, path in missing_eng_phrases:
                gTTS(text=phrase, lang='en', tld='com').save(path)

    def _ensure_flag_file(self):
        img_dir = "assets/images"
        os.makedirs(img_dir, exist_ok=True)
        flag_path = self.template['assets'].get('flag_path', "assets/images/korea.png")
        if not os.path.exists(flag_path):
            print("🇰🇷 Загрузка официального флага Южной Кореи...")
            url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/640px-Flag_of_South_Korea.svg.png"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(flag_path, 'wb') as out_file:
                    out_file.write(response.read())
            except Exception as e:
                print(f"[Внимание] Не удалось загрузить дефолтный флаг: {e}")

    def _load_custom_font(self, font_path, size):
        try:
            return ImageFont.truetype(font_path, max(1, int(size)))
        except IOError:
            return ImageFont.load_default()

    def _generate_pastel_color(self):
        h = random.random()            
        s = random.uniform(0.2, 0.35)  
        l = random.uniform(0.88, 0.94)  
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))

    def _draw_wrapped_text(self, draw, text, font_path, base_size, max_width, center_x, center_y, fill_color):
        font = self._load_custom_font(font_path, base_size)
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word]) if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                current_line.append(word)
            else:
                if current_line: lines.append(" ".join(current_line))
                current_line = [word]
        if current_line: lines.append(" ".join(current_line))
            
        line_data = []
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            h = bbox[3] - bbox[1]
            line_data.append((line, h))
            total_height += h
            
        spacing = 20  
        total_height += spacing * (len(lines) - 1)
        current_y = center_y - total_height / 2
        
        for line, h in line_data:
            draw.text((center_x, current_y + h / 2), line, font=font, fill=fill_color, anchor="mm")
            current_y += h + spacing

    def generate_static_thumbnail(self, display_word, selected_phrase=None, bg_color=None, draw_badge=True):
        colors = self.template.get('colors', {})
        toggles = self.template.get('features_toggles', {})
        typography = self.template.get('typography', {})
        layout = self.template['layout']
        quiz_cfg = self.template.get('quiz_layout', {})
        
        if bg_color is None:
            mode = colors.get('bg_mode', 'fixed')
            if mode == 'cycle':
                palette = colors.get('pastel_colors', ['#EBF5EE'])
                bg_color = palette[self.color_cycle_index % len(palette)]
                if draw_badge:
                    self.color_cycle_index += 1
            elif mode == 'fixed':
                bg_color = colors.get('fixed_bg_hex', '#EBF5EE')
            else:
                bg_color = self._generate_pastel_color()
        
        base_image = Image.new('RGB', (self.width, self.height), color=bg_color)
        draw = ImageDraw.Draw(base_image)

        if quiz_cfg.get('show_ui_frame', True):
            pad = quiz_cfg.get('frame_padding', 45)
            draw.rounded_rectangle(
                [pad, pad, self.width - pad, self.height - pad],
                radius=quiz_cfg.get('frame_radius', 40),
                outline=quiz_cfg.get('frame_color_hex', '#2B2D42'),
                width=quiz_cfg.get('frame_thickness', 5)
            )
        
        flag_path = self.template['assets'].get('flag_path', "assets/images/korea.png")
        if toggles.get('show_flag', True) and os.path.exists(flag_path):
            flag_img = Image.open(flag_path).convert("RGBA")
            flag_cfg = self.template.get('flag_settings', {})
            orig_w, orig_h = flag_img.size
            aspect_ratio = orig_w / orig_h
            
            max_w = flag_cfg.get('max_width', 180)
            scale_factor = flag_cfg.get('scale', 1.0)
            f_w = int(max_w * scale_factor)
            f_h = int(f_w / aspect_ratio)
            
            flag_img = flag_img.resize((f_w, f_h), Image.Resampling.LANCZOS)
            
            x_frac = flag_cfg.get('x_fraction', 0.5)
            y_frac = flag_cfg.get('y_fraction', 0.10)
            flag_x = int(self.width * x_frac - f_w / 2)
            flag_y = int(self.height * y_frac - f_h / 2)
            
            base_image.paste(flag_img, (flag_x, flag_y), flag_img)
            
        font_eng_path = self.template['assets']['font_eng_path']
        
        if not selected_phrase:
            selected_phrase = random.choice(self.template['catchy_phrases'])
            
        if quiz_cfg.get('show_quiz_header', True):
            h1 = quiz_cfg.get('header_line1', {})
            h2 = quiz_cfg.get('header_line2', {})
            font_h1 = self._load_custom_font(self.template['assets'].get(h1.get('font_key', 'font_roboto_path')), h1.get('font_size', 40))
            font_h2 = self._load_custom_font(self.template['assets'].get(h2.get('font_key', 'font_eng_path')), h2.get('font_size', 50))
            draw.text((self.width / 2, self.height * h1.get('y_fraction', 0.155)), h1.get('text', 'KOREAN'), font=font_h1, fill=h1.get('color_hex', '#2B2D42'), anchor="mm")
            draw.text((self.width / 2, self.height * h2.get('y_fraction', 0.18)), h2.get('text', 'TESTS'), font=font_h2, fill=h2.get('color_hex', '#2B2D42'), anchor="mm")
            
        if quiz_cfg.get('channel_footer', {}).get('show', True):
            footer = quiz_cfg.get('channel_footer', {})
            font_f = self._load_custom_font(self.template['assets'].get(footer.get('font_key', 'font_roboto_path')), footer.get('font_size', 42))
            draw.text((self.width / 2, self.height * footer.get('y_fraction', 0.90)), footer.get('text', '@YOUR_CHANNEL'), font=font_f, fill=footer.get('color_hex', '#2B2D42'), anchor="mm")
        
        # ⚡ УМНОЕ РАЗДЕЛЕНИЕ ТЕКСТА: На экран выводим ТОЛЬКО первую часть фразы
        screen_phrase = selected_phrase
        idx_excl = selected_phrase.find('!')
        idx_quest = selected_phrase.find('?')
        valid_indices = [i for i in [idx_excl, idx_quest] if i != -1]
        if valid_indices:
            # Обрезаем строку ровно после первого знака ! или ?
            screen_phrase = selected_phrase[:min(valid_indices) + 1].strip()

        phrase_size = typography.get('phrase_font_size', 75)
        phrase_color = colors.get('phrase_text_hex', '#2B2D42')
        self._draw_wrapped_text(
            draw=draw, text=screen_phrase, font_path=font_eng_path, 
            base_size=phrase_size, max_width=900, 
            center_x=self.width / 2, center_y=self.height * layout['phrase_y_fraction'], 
            fill_color=phrase_color
        )
                  
        prefix = self.template['text']['topic_prefix']
        full_text = f"{prefix} {display_word.upper()}".strip()
        
        any_korean = any(31360 <= ord(char) <= 55215 for char in full_text)
        chosen_font_path = self.template['assets']['font_kor_path'] if any_korean else font_eng_path
        
        topic_size = typography.get('badge_font_size', 110)
        font_topic = self._load_custom_font(chosen_font_path, topic_size)
        
        while topic_size > 40:
            font_box = draw.textbbox((0, 0), full_text, font=font_topic)
            if (font_box[2] - font_box[0]) <= 840: break
            topic_size -= 5
            font_topic = self._load_custom_font(chosen_font_path, topic_size)
            
        font_box = draw.textbbox((0, 0), full_text, font=font_topic)
        box_w = font_box[2] - font_box[0] + 140
        box_h = font_box[3] - font_box[1] + 50
        
        pad = 150
        badge_canvas_w = box_w + pad
        badge_canvas_h = box_h + pad
        badge_layer = Image.new('RGBA', (badge_canvas_w, badge_canvas_h), (0, 0, 0, 0))
        badge_draw = ImageDraw.Draw(badge_layer)
        
        bx1 = pad / 2
        by1 = pad / 2
        bx2 = bx1 + box_w
        by2 = by1 + box_h
        
        badge_bg_color = colors.get('badge_bg_hex', '#FFD166')
        badge_text_color = colors.get('badge_text_hex', '#2B2D42')
        frame_color = quiz_cfg.get('frame_color_hex', '#2B2D42')
        
        badge_draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=badge_bg_color, outline=frame_color, width=4)
        badge_draw.text((badge_canvas_w / 2, badge_canvas_h / 2), full_text, font=font_topic, fill=badge_text_color, anchor="mm")
        
        rotation_angle = layout.get('badge_rotation', 0)
        rotated_badge = badge_layer.rotate(rotation_angle, resample=Image.Resampling.BICUBIC, expand=True)
        
        if draw_badge:
            badge_center_y = self.height * layout['badge_y_fraction']
            rb_w, rb_h = rotated_badge.size
            paste_x = int((self.width - rb_w) / 2)
            paste_y = int(badge_center_y - rb_h / 2)
            base_image.paste(rotated_badge, (paste_x, paste_y), rotated_badge)
            return base_image, bg_color, selected_phrase
        else:
            return base_image, bg_color, selected_phrase, rotated_badge

    def save_preview_as_image(self, display_word, output_png_path="preview_test.png"):
        img, _, _ = self.generate_static_thumbnail(display_word, draw_badge=True)
        img.save(output_png_path)
        print(f"📸 UI/UX превью успешно сохранено: {output_png_path}")

    def render_preview_clip(self, display_word):
        timings = self.template.get('timings', {})
        toggles = self.template.get('features_toggles', {})
        audio_settings = self.template.get('audio_settings', {})
        layout = self.template['layout']
        
        base_img, bg_color, selected_phrase, rotated_badge = self.generate_static_thumbnail(
            display_word, draw_badge=False
        )
        
        if self.template.get('colors', {}).get('bg_mode') == 'cycle':
            self.color_cycle_index += 1
            
        static_frame_base = np.array(base_img)
        
        audio_clips = []
        voice_vol = audio_settings.get('voice_volume', 1.0)
        
        p_start = timings.get('phrase_audio_start', 0.1)
        phrase_duration = 0.0
        
        # Озвучка по-прежнему берет ПОЛНУЮ фразу (со всеми восклицаниями и призывами)
        if toggles.get('play_phrase_voiceover', True):
            phrase_audio_path = self._get_phrase_audio_path(selected_phrase)
            if os.path.exists(phrase_audio_path):
                p_clip = AudioFileClip(phrase_audio_path)
                phrase_duration = p_clip.duration
                audio_clips.append(p_clip.set_start(p_start).volumex(voice_vol))
        
        gap_after_phrase = 0.15  
        t1 = p_start + phrase_duration + gap_after_phrase
        t2 = t1 + 0.7  
        t3 = t2 + 0.7
        duration = t3 + 0.9  
        
        def make_frame(t):
            frame_img = Image.fromarray(static_frame_base)
            
            pulse_scale = 1.0 + 0.04 * np.sin(2 * np.pi * 0.8 * t)
            
            orig_w, orig_h = rotated_badge.size
            new_w = max(1, int(orig_w * pulse_scale))
            new_h = max(1, int(orig_h * pulse_scale))
            
            scaled_badge = rotated_badge.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            badge_center_y = self.height * layout['badge_y_fraction']
            paste_x = int((self.width - new_w) / 2)
            paste_y = int(badge_center_y - new_h / 2)
            
            frame_img.paste(scaled_badge, (paste_x, paste_y), scaled_badge)
            
            if not toggles.get('show_counter', True):
                return np.array(frame_img)
                
            draw = ImageDraw.Draw(frame_img)
            font_eng_path = self.template['assets']['font_eng_path']
            colors = self.template.get('colors', {})
            typography = self.template.get('typography', {})
            
            count_text = ""
            t_rel = 0.0
            
            if t1 <= t < t2:
                count_text = "1"
                t_rel = (t - t1) / (t2 - t1)
            elif t2 <= t < t3:
                count_text = "2"
                t_rel = (t - t2) / (t3 - t2)
            elif t3 <= t <= duration:
                count_text = "3"
                t_rel = (t - t3) / (duration - t3)
                
            if count_text:
                scale_factor = 0.4 + 1.3 * (t_rel ** 0.6)
                base_counter_size = typography.get('counter_font_size', 320)
                dynamic_size = int(base_counter_size * scale_factor)
                
                counter_color = colors.get('counter_text_hex', '#2B2D42')
                font_num = self._load_custom_font(font_eng_path, dynamic_size)
                draw.text((self.width / 2, self.height * layout['counter_y_fraction']), 
                          count_text, font=font_num, fill=counter_color, anchor="mm")
                          
            return np.array(frame_img)
            
        video_clip = VideoClip(make_frame, duration=duration)
        
        audio_mapping = {
            t1: "assets/audio/count_1.mp3",
            t2: "assets/audio/count_2.mp3",
            t3: "assets/audio/count_3.mp3"
        }
        for start_time, audio_path in audio_mapping.items():
            if os.path.exists(audio_path):
                audio_clips.append(AudioFileClip(audio_path).set_start(start_time).volumex(voice_vol))
                
        if audio_clips:
            video_clip = video_clip.set_audio(CompositeAudioClip(audio_clips))
            
        return video_clip