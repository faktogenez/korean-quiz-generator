import json
import os
import math
import numpy as np
from moviepy.editor import (
    AudioFileClip, concatenate_videoclips, concatenate_audioclips, 
    CompositeAudioClip, VideoClip, CompositeVideoClip, afx
)
from src.renderers.animation_engine import AnimationEngine

class MoviePyRenderer:
    def __init__(self, template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)
        self.animator = AnimationEngine(self.template)

    def render_video(self, blueprint, output_path):
        card_clips = []
        width, height = self.template['dimensions']['width'], self.template['dimensions']['height']
        
        # Сначала генерируем чистые клипы для каждой карточки
        for item in blueprint:
            # --- БЛОК ВОПРОСА ---
            audio_q = AudioFileClip(item['audio_question_path'])
            q_duration = audio_q.duration
            total_q_duration = q_duration + 3

            def make_q_frame(t, current_item=item, q_dur=q_duration):
                timer_progress = 0.0 if t < q_dur else min((t - q_dur) / 3.0, 1.0)
                return np.array(self.animator.draw_card(
                    current_item, is_answer=False, timer_progress=timer_progress, anti_ban_noise=True
                ))

            clip_q = VideoClip(make_q_frame, duration=total_q_duration)
            sfx_timer = AudioFileClip("assets/tick.mp3").set_duration(3).set_start(q_duration)
            clip_q = clip_q.set_audio(CompositeAudioClip([audio_q, sfx_timer]))
            
            # --- БЛОК ОТВЕТА / CTA (+2 секунды комфортной паузы) ---
            audio_a = AudioFileClip(item['audio_answer_path'])
            audio_a_seq = concatenate_audioclips([AudioFileClip("assets/ding.mp3"), audio_a])
            
            ans_duration = audio_a_seq.duration + 2.0
            if item.get('is_last', False):
                ans_duration += 8.0  
            
            def make_a_frame(t, current_item=item):
                pulse_size = None
                if current_item.get('is_last', False):
                    base_s = self.template['typography']['size_pulse_question_base']
                    pulse_size = base_s + 15 * math.sin(t * 2 * math.pi * 1.0)
                return np.array(self.animator.draw_card(
                    current_item, is_answer=True, correct_idx=current_item['correct_index'], 
                    pulse_font_size=pulse_size, anti_ban_noise=True
                ))

            clip_a = VideoClip(make_a_frame, duration=ans_duration)
            clip_a = clip_a.set_audio(audio_a_seq)
            
            single_card_clip = concatenate_videoclips([clip_q, clip_a])
            card_clips.append(single_card_clip)
            
        # --- СБОРКА С ЭФФЕКТОМ "КАРУСЕЛЬ" (СИНХРОННЫЙ СДВИГ) ---
        transition_duration = 0.8
        
        # Функция-фабрика: создает индивидуальную логику движения для каждой карточки
        def create_carousel_position(is_first, is_last, clip_duration):
            def position(t):
                # Функция нелинейного замедления (Ease-Out)
                def ease_out(progress):
                    return 1 - (1 - progress) ** 3

                # 1. ВЪЕЗД (справа налево в центр) — для всех карточек, кроме первой
                if not is_first and t <= transition_duration:
                    progress = t / transition_duration
                    return (max(int(width - (width * ease_out(progress))), 0), 0)
                
                # 2. ВЫЕЗД (из центра налево за экран) — для всех карточек, кроме последней
                time_until_end = clip_duration - t
                if not is_last and time_until_end <= transition_duration:
                    # Защита от мелких погрешностей времени (уход в минус)
                    out_t = max(transition_duration - time_until_end, 0) 
                    progress = out_t / transition_duration
                    return (-int(width * ease_out(progress)), 0)
                
                # 3. СТАТИКА (карточка стоит по центру)
                return (0, 0)
            return position

        final_layers = []
        current_time = 0.0
        num_clips = len(card_clips)

        # Выкладываем карточки на таймлайн внахлест
        for i, clip in enumerate(card_clips):
            is_first = (i == 0)
            is_last = (i == num_clips - 1)
            
            # Присваиваем клипу логику карусели, зная его полную длительность
            pos_func = create_carousel_position(is_first, is_last, clip.duration)
            
            if is_first:
                animated_clip = clip.set_start(0).set_position(pos_func)
                final_layers.append(animated_clip)
                current_time = clip.duration
            else:
                # Накладываем следующую карточку за 0.8 сек до конца предыдущей
                start_transition = current_time - transition_duration
                animated_clip = clip.set_start(start_transition).set_position(pos_func)
                final_layers.append(animated_clip)
                current_time = start_transition + clip.duration

        # Собираем всё в один финальный видеоряд
        final_video = CompositeVideoClip(final_layers, size=(width, height)).set_duration(current_time)
        video_duration = final_video.duration
        
        # --- НАЛОЖЕНИЕ МУЗЫКИ ---
        bg_music_path = "assets/background_music.mp3"
        if os.path.exists(bg_music_path):
            print(f"[Музыка] Накладываю зацикленный трек под длительность: {video_duration:.2f} сек.")
            bg_music = AudioFileClip(bg_music_path)
            bg_music = afx.audio_loop(bg_music, duration=video_duration)
            bg_music = bg_music.set_duration(video_duration).volumex(0.15)
            bg_music = afx.audio_fadeout(bg_music, 3.0)
            
            final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, bg_music]))

        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")