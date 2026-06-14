import json
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
from src.renderers.animation_engine import AnimationEngine

class MoviePyRenderer:
    def __init__(self, template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)
        self.animator = AnimationEngine(self.template)

    def render_video(self, blueprint, output_path):
        clips = []
        for item in blueprint:
            # 1. Вопрос
            audio_q = AudioFileClip(item['audio_question_path'])
            sfx_timer = AudioFileClip("assets/tick.mp3").set_start(audio_q.duration).set_duration(3)
            
            clip_q = ImageClip(np.array(self.animator.draw_card(item, False))).set_duration(audio_q.duration + 3)
            clip_q = clip_q.set_audio(CompositeAudioClip([audio_q, sfx_timer]))
            
            # 2. Ответ (Ding + Озвучка)
            audio_a = AudioFileClip(item['audio_answer_path'])
            ding = AudioFileClip("assets/ding.mp3")
            # Склеиваем: Ding, затем сразу озвучка ответа
            audio_a_sequence = concatenate_audioclips([ding, audio_a])
            
            clip_a = ImageClip(np.array(self.animator.draw_card(item, True, item['correct_index']))).set_duration(audio_a_sequence.duration)
            clip_a = clip_a.set_audio(audio_a_sequence)
            
            clips.extend([clip_q, clip_a])
            
        concatenate_videoclips(clips).write_videofile(output_path, fps=24)