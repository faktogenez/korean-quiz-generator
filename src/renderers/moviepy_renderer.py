import json
import numpy as np
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, 
    concatenate_audioclips, CompositeAudioClip, VideoClip
)
from src.renderers.animation_engine import AnimationEngine

class MoviePyRenderer:
    def __init__(self, template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)
        self.animator = AnimationEngine(self.template)

    def render_video(self, blueprint, output_path):
        clips = []
        for item in blueprint:
            audio_q = AudioFileClip(item['audio_question_path'])
            q_duration = audio_q.duration
            total_q_duration = q_duration + 3 # Длина аудио + 3 секунды таймера

            # ИСПРАВЛЕНИЕ: Привязываем текущий item и q_duration к контексту функции 
            # через параметры по умолчанию (current_item=item, q_dur=q_duration)
            def make_q_frame(t, current_item=item, q_dur=q_duration):
                if t < q_dur:
                    # Пока идет озвучка, полоска таймера на нуле (0.0)
                    return np.array(self.animator.draw_card(current_item, is_answer=False, timer_progress=0.0))
                else:
                    # Когда включается таймер, полоска плавно растет от 0.0 до 1.0 за 3 секунды
                    t_timer = t - q_dur
                    return np.array(self.animator.draw_card(current_item, is_answer=False, timer_progress=min(t_timer / 3.0, 1.0)))

            # Создаем динамический клип вопроса на основе исправленной функции
            clip_q = VideoClip(make_q_frame, duration=total_q_duration)
            sfx_timer = AudioFileClip("assets/tick.mp3").set_duration(3).set_start(q_duration)
            clip_q = clip_q.set_audio(CompositeAudioClip([audio_q, sfx_timer]))
            
            # Клип ответа (Дзынь + Озвучка ответа)
            audio_a = AudioFileClip(item['audio_answer_path'])
            audio_a_seq = concatenate_audioclips([AudioFileClip("assets/ding.mp3"), audio_a])
            
            clip_a = ImageClip(np.array(self.animator.draw_card(item, is_answer=True, correct_idx=item['correct_index'])))
            clip_a = clip_a.set_duration(audio_a_seq.duration)
            clip_a = clip_a.set_audio(audio_a_seq)
            
            clips.extend([clip_q, clip_a])
            
        final_video = concatenate_videoclips(clips)
        final_video.write_videofile(output_path, fps=24)