import json
from PIL import Image, ImageDraw, ImageFont

def test_draw_full():
    with open('templates/vertical/template.json', 'r', encoding='utf-8') as f:
        t = json.load(f)

    img = Image.new('RGB', (t['width'], t['height']), color=t['colors']['bg'])
    draw = ImageDraw.Draw(img)

    # 1. Заголовок (brand)
    f_brand = ImageFont.truetype(t['fonts']['brand']['path'], t['fonts']['brand']['size'])
    draw.text((t['width']//2, t['coordinates']['brand']['y']), t['coordinates']['brand']['text'], 
              fill=t['colors']['brand_text'], anchor="mm", font=f_brand)

    # 2. Слово (word)
    f_word = ImageFont.truetype(t['fonts']['word']['path'], t['fonts']['word']['size'])
    draw.text((t['width']//2, 800), "빨간색", fill=t['colors']['text'], anchor="mm", font=f_word)

    # 3. Кнопки вариантов (option1 и option2)
    for i, opt in enumerate(['Option 1', 'Option 2']):
        y_pos = 1200 + (i * (t['coordinates']['option1']['h'] + t['gaps']['options_gap']))
        x = t['coordinates']['option1']['x']
        w, h = t['coordinates']['option1']['w'], t['coordinates']['option1']['h']
        
        # Рисуем прямоугольник кнопки
        draw.rectangle([x, y_pos, x + w, y_pos + h], outline=t['colors']['option_border'], width=3)
        # Рисуем текст кнопки
        f_opt = ImageFont.truetype(t['fonts']['option']['path'], t['fonts']['option']['size'])
        draw.text((x + 50, y_pos + 40), opt, fill=t['colors']['text'], font=f_opt)

    # 4. Прогресс-бар
    p = t['coordinates']['progress_bar']
    draw.rectangle([p['x'], p['y'], p['x'] + p['w'], p['y'] + p['h']], fill=t['colors']['progress_bg'])
    draw.rectangle([p['x'], p['y'], p['x'] + int(p['w'] * 0.5), p['y'] + p['h']], fill=t['colors']['progress_fill'])

    img.save('test_full.png')
    print("Полная карточка 'test_full.png' создана!")

if __name__ == "__main__":
    test_draw_full()