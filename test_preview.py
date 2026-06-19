import os
from src.preview.preview_engine import PreviewEngine

def run_test():
    os.makedirs("assets/fonts", exist_ok=True)
    os.makedirs("assets/audio", exist_ok=True)

    print("🚀 Запуск дизайнерского движка превью с озвучкой хуков...")
    engine = PreviewEngine()
    
    test_word = "주방" # Пример корейского слова (Кухня)
    
    print("\n1️⃣ Рендерим премиальный PNG-кадр по сетке золотого сечения...")
    engine.save_preview_as_image(display_word=test_word, output_png_path="CHECK_PREVIEW.png")

    print("\n2️⃣ Запускаем видеорендер с английским голосом и корейским счетом...")
    preview_clip = engine.render_preview_clip(display_word=test_word)
    
    output_video = "test_preview_output.mp4"
    preview_clip.write_videofile(
        output_video,
        fps=24,
        codec="libx264",
        preset="ultrafast",
        threads=20
    )
    print(f"\n✅ Успех! Проверяй обновленный CHECK_PREVIEW.png и слушай звук в {output_video}")

if __name__ == "__main__":
    run_test()