"""
PNG'den ICO'ya dönüştürücü
"""
from PIL import Image
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# PNG dosyasını yükle
img = Image.open("app_icon.png")

# RGBA'ya çevir
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Farklı boyutlarda kaydet
sizes = [16, 32, 48, 64, 128, 256]
images = []

for size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f"icon_{size}.png")
    images.append(resized)
    print(f"icon_{size}.png oluşturuldu")

# ICO dosyası oluştur
img.save("app_icon.ico", format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
print("app_icon.ico oluşturuldu")
