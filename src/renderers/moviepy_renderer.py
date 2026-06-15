import json
import numpy as np
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, 
    concatenate_audioclips, CompositeAudioClip, VideoClip, CompositeVideoClip
)
from src.renderers.animation_engine import AnimationEngine

class MoviePyRenderer:
    def __init__(self, template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)
        self.animator = AnimationEngine(self.template)

    def render_video(self, blueprint, output_path):
        card_clips = []
        width, height = self.template['width'], self.template['height']
        
        for item in blueprint:
            # --- БЛОК ВОПРОСА ---
            audio_q = AudioFileClip(item['audio_question_path'])
            q_duration = audio_q.duration
            total_q_duration = q_duration + 3

            def make_q_frame(t, current_item=item, q_dur=q_duration):
                if t < q_dur:
                    return np.array(self.animator.draw_card(current_item, is_answer=False, timer_progress=0.0))
                else:
                    t_timer = t - q_dur
                    return np.array(self.animator.draw_card(current_item, is_answer=False, timer_progress=min(t_timer / 3.0, 1.0)))

            clip_q = VideoClip(make_q_frame, duration=total_q_duration)
            sfx_timer = AudioFileClip("assets/tick.mp3").set_duration(3).set_start(q_duration)
            clip_q = clip_q.set_audio(CompositeAudioClip([audio_q, sfx_timer]))
            
            # --- БЛОК ОТВЕТА / CTA ---
            audio_a = AudioFileClip(item['audio_answer_path'])
            audio_a_seq = concatenate_audioclips([AudioFileClip("assets/ding.mp3"), audio_a])
            
            ans_duration = audio_a_seq.duration
            if item.get('is_last', False):
                ans_duration += 10.0  # Удержание 10 секунд в конце для сбора комментариев
            
            clip_a = ImageClip(np.array(self.animator.draw_card(item, is_answer=True, correct_idx=item['correct_index'])))
            clip_a = clip_a.set_duration(ans_duration)
            clip_a = clip_a.set_audio(audio_a_seq)
            
            # Собираем одну готовую карточку (Вопрос + Ответ)
            single_card_clip = concatenate_videoclips([clip_q, clip_a])
            card_clips.append(single_card_clip)
            
        # --- СБОРКА С СИНХРОННОЙ АНИМАЦИЕЙ КАРАУСЕЛИ (СВАЙП ВЛЕВО) ---
        transition_duration = 0.4  # Длительность перехода
        animated_clips = [card_clips[0]]
        
        for i in range(1, len(card_clips)):
            prev_clip = animated_clips[-1]
            next_clip = card_clips[i]
            
            # Рассчитываем момент времени начала анимации внутри старого клипа
            start_transition_time = prev_clip.duration - transition_duration
            
            # Отрезаем кусок старого клипа, который будет анимироваться
            prev_transition_segment = prev_clip.subclip(start_transition_time)
            
            # 1. СМЕЩЕНИЕ СТАРОЙ КАРТОЧКИ: движется влево от 0 до -width
            moving_prev = prev_transition_segment.set_position(
                lambda t, w=width: (-int((w / transition_duration) * t), 0)
            )
            
            # 2. СМЕЩЕНИЕ НОВОЙ КАРТОЧКИ: заезжает слева от width до 0
            moving_next = next_clip.set_position(
                lambda t, w=width: (max(int(w - (w / transition_duration) * t), 0), 0)
            ).set_start(0) # Начинает движение синхронно с первой координатой t=0 в композиции
            
            # Компонуем обе движущиеся карточки на одном холсте
            transition_composite = CompositeVideoClip(
                [moving_prev, moving_next], 
                size=(width, height)
            ).set_duration(transition_duration)
            
            # Пересобираем последовательность: 
            # Оставляем чистую статичную часть старого клипа + добавляем созданную композицию карусели
            animated_clips[-1] = prev_clip.subclip(0, start_transition_time)
            animated_clips.append(transition_composite)
            
            # Добавляем оставшуюся (основную) часть новой карточки
            animated_clips.append(next_clip.subclip(transition_duration))
            
        # Окончательная склейка всей ленты карусели
        final_video = concatenate_videoclips(animated_clips)
        final_video.write_videofile(output_path, fps=24)