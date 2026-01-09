"""
ChwiliTranslate İkon Oluşturucu
Modern, çeviri temalı ikon
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Farklı boyutlarda ikon oluşturur"""
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Arka plan - gradient efekti için iki daire
        # Dış daire - koyu mavi
        padding = size // 10
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill=(10, 15, 30, 255)
        )
        
        # İç daire - cyan glow efekti
        inner_pad = size // 6
        draw.ellipse(
            [inner_pad, inner_pad, size - inner_pad, size - inner_pad],
            fill=(0, 40, 60, 255)
        )
        
        # Çeviri sembolü - iki konuşma balonu
        center = size // 2
        
        # Sol balon (kaynak dil)
        bubble_size = size // 3
        left_x = center - bubble_size // 2 - size // 10
        top_y = center - bubble_size // 2 - size // 12
        
        # Sağ balon (hedef dil) - cyan
        right_x = center - bubble_size // 2 + size // 10
        bottom_y = center - bubble_size // 2 + size // 12
        
        # Sol balon çiz (beyaz)
        draw.rounded_rectangle(
            [left_x, top_y, left_x + bubble_size, top_y + bubble_size * 0.7],
            radius=size // 12,
            fill=(255, 255, 255, 230)
        )
        
        # Sağ balon çiz (cyan)
        draw.rounded_rectangle(
            [right_x, bottom_y, right_x + bubble_size, bottom_y + bubble_size * 0.7],
            radius=size // 12,
            fill=(0, 212, 255, 255)
        )
        
        # Ok işareti (çeviri yönü)
        arrow_y = center
        arrow_start = center - size // 6
        arrow_end = center + size // 6
        arrow_width = max(2, size // 20)
        
        # Ok çizgisi
        draw.line(
            [(arrow_start, arrow_y), (arrow_end, arrow_y)],
            fill=(0, 212, 255, 255),
            width=arrow_width
        )
        
        # Ok ucu
        arrow_head = size // 10
        draw.polygon([
            (arrow_end, arrow_y),
            (arrow_end - arrow_head, arrow_y - arrow_head // 2),
            (arrow_end - arrow_head, arrow_y + arrow_head // 2)
        ], fill=(0, 212, 255, 255))
        
        # Kaydet
        img.save(f'icon_{size}.png')
        print(f"icon_{size}.png oluşturuldu")
    
    # ICO dosyası oluştur (Windows için)
    images = []
    for size in [16, 32, 48, 256]:
        images.append(Image.open(f'icon_{size}.png'))
    
    images[0].save(
        'app_icon.ico',
        format='ICO',
        sizes=[(s, s) for s in [16, 32, 48, 256]]
    )
    print("app_icon.ico oluşturuldu")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_icon()
