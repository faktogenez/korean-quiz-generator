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
            # 1. Аудио
            audio_q = AudioFileClip(item['audio_question_path'])
            sfx_timer = AudioFileClip("assets/tick.mp3").set_duration(3)
            
            # 2. Клип вопроса (фраза + корейское слово)
            # Статическая часть (пока звучит голос)
            img_static = np.array(self.animator.draw_card(item, is_answer=False, timer_progress=0.0))
            clip_q_static = ImageClip(img_static).set_duration(audio_q.duration)
            
            # Анимация таймера (плавный рост за 3 сек)
            def make_frame(t):
                # t идет от 0 до 3
                return np.array(self.animator.draw_card(item, is_answer=False, timer_progress=min(t / 3.0, 1.0)))
            
            clip_q_timer = VideoClip(make_frame, duration=3)
            
            # Собираем вопрос
            full_q = concatenate_videoclips([clip_q_static, clip_q_timer])
            full_q = full_q.set_audio(CompositeAudioClip([audio_q.set_duration(audio_q.duration), 
                                                         sfx_timer.set_start(audio_q.duration)]))
            
            # 3. Клип ответа
            audio_a = AudioFileClip(item['audio_answer_path'])
            audio_a_seq = concatenate_audioclips([AudioFileClip("assets/ding.mp3"), audio_a])
            
            clip_a = ImageClip(np.array(self.animator.draw_card(item, True, item['correct_index']))).set_duration(audio_a_seq.duration)
            clip_a = clip_a.set_audio(audio_a_seq)
            
            clips.extend([full_q, clip_a])
            
        concatenate_videoclips(clips).write_videofile(output_path, fps=24)