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
            
            ans_duration = audio_a_seq.duration + 2.0 # Добавляем 2 секунды тишины/паузы в конце слайда
            if item.get('is_last', False):
                ans_duration += 8.0  # Суммарно 10 секунд на финальном квесте
            
            def make_a_frame(t, current_item=item):
                pulse_size = None
                if current_item.get('is_last', False):
                    base_s = self.template['typography']['size_pulse_question_base']
                    # Пульсация знака от базового размера до +30 пикселей сверху
                    pulse_size = base_s + 15 * math.sin(t * 2 * math.pi * 1.0)
                return np.array(self.animator.draw_card(
                    current_item, is_answer=True, correct_idx=current_item['correct_index'], 
                    pulse_font_size=pulse_size, anti_ban_noise=True
                ))

            clip_a = VideoClip(make_a_frame, duration=ans_duration)
            clip_a = clip_a.set_audio(audio_a_seq)
            
            single_card_clip = concatenate_videoclips([clip_q, clip_a])
            card_clips.append(single_card_clip)
            
        # --- СБОРКА С КИНЕМАТОГРАФИЧНЫМ ПЛАВНЫМ СВАЙПОМ (0.8 сек) ---
        transition_duration = 0.8
        animated_clips = [card_clips[0]]
        
        for i in range(1, len(card_clips)):
            prev_clip = animated_clips[-1]
            next_clip = card_clips[i]
            
            start_transition_time = prev_clip.duration - transition_duration
            prev_transition_segment = prev_clip.subclip(start_transition_time)
            
            # Функция нелинейного замедления (Ease-Out) для суперплавного движения
            def ease_out_progress(t):
                progress = t / transition_duration
                return 1 - (1 - progress) ** 3  # Кубическое затухание скорости

            moving_prev = prev_transition_segment.set_position(
                lambda t, w=width: (-int(w * ease_out_progress(t)), 0)
            )
            moving_next = next_clip.set_position(
                lambda t, w=width: (max(int(w - (w * ease_out_progress(t))), 0), 0)
            ).set_start(0)
            
            transition_composite = CompositeVideoClip(
                [moving_prev, moving_next], size=(width, height)
            ).set_duration(transition_duration)
            
            animated_clips[-1] = prev_clip.subclip(0, start_transition_time)
            animated_clips.append(transition_composite)
            animated_clips.append(next_clip.subclip(transition_duration))
            
        final_video = concatenate_videoclips(animated_clips)
        video_duration = final_video.duration
        
        # --- НАЛОЖЕНИЕ МУЗЫКИ ---
        bg_music_path = "assets/background_music.mp3"
        if os.path.exists(bg_music_path):
            print(f"[Музыка] Накладываю зацикленный трек...")
            bg_music = AudioFileClip(bg_music_path)
            bg_music = afx.audio_loop(bg_music, duration=video_duration)
            bg_music = bg_music.set_duration(video_duration).volumex(0.15)
            bg_music = afx.audio_fadeout(bg_music, 3.0)
            
            final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, bg_music]))

        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")