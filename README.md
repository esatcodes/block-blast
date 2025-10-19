# 🎮 Block Blast

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Zekice Yerleştirme, Stratejik Temizleme!**  
Renkli blokları yerleştir, satırları tamamla ve yüksek skorlar elde et!

[Özellikler](#-özellikler) • [Kurulum](#-kurulum) • [Oynanış](#-oynanış) • [Ekran Görüntüleri](#-ekran-görüntüleri) • [İndirme](#-indirme)

</div>

## 🎯 Özellikler

### 🎨 Görsel Özellikler
- **Renkli ve Canlı Grafikler**: Parlak renklerle bezeli bloklar ve ızgaralar
- **Animasyon Efektleri**: Blok yerleştirme, patlama ve parçacık efektleri
- **Yüzen Metinler**: Skor artışları ve combo bilgileri için animasyonlu metinler
- **Gece Modu Tema**: Göz yormayan koyu tema

### 🎵 Ses & Müzik
- **3 Farklı Müzik Stili**:
  - 🎹 **Enhanced**: Zengin orkestral melodi
  - ⚡ **Upbeat**: Enerjik 8-bit tarzı
  - 🌊 **Calm**: Sakin ve rahatlatıcı
- **Özel Ses Efektleri**: Blok yerleştirme, temizleme, özel efektler
- **Ses Ayarları**: Master, müzik ve efekt sesleri için ayrı kontroller

### 🎮 Oyun Mekanikleri
- **3 Zorluk Seviyesi**:
  - 🟢 **Kolay**: 500 puan hedef, 1.0 çarpan
  - 🟡 **Normal**: 1000 puan hedef, 1.5 çarpan  
  - 🔴 **Zor**: 2000 puan hedef, 2.0 çarpan
- **Combo Sistemi**: Ardışık temizlemelerde artan çarpan
- **Power-up'lar**:
  - 💣 **Bomb**: Rastgele 3 hücreyi temizler
  - ⚡ **Lightning**: Tüm bir sütunu temizler
  - 🌈 **Rainbow**: Aynı renkteki tüm blokları temizler

### 📊 İlerleme & İstatistikler
- **Skor Takibi**: Gerçek zamanlı skor ve hedef takibi
- **Yüksek Skor Kaydı**: Zorluk seviyelerine göre rekorlar
- **Oyun İstatistikleri**: Oynanan oyun sayıları
- **Otomatik Kaydetme**: İlerleme otomatik olarak kaydedilir

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- Pygame kütüphanesi
- NumPy kütüphanesi

### Adım Adım Kurulum

1. **Depoyu Klonlayın**:
```bash
git clone https://github.com/TETech-Studios/block-blast.git
cd block-blast
pip install pygame numpy
python block_blast.py
{
  "graphics": {
    "cell_size": 40,
    "grid_size": 8,
    "animations": true
  },
  "audio": {
    "master_volume": 1.0,
    "music_volume": 0.7,
    "sfx_volume": 0.8
  }
}
MIT License

Copyright (c) 2024 TETech Studios

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
MIT License

Copyright (c) 2024 TETech Studios

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
pygame>=2.0.0
numpy>=1.21.0
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
dist/
build/
*.egg-info/

# PyInstaller
*.exe
*.spec

# Game data
block_blast_stats.json
*.save
*.sav

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
# Changelog

## [1.0.0] - 2024-01-XX
### Added
- Temel oyun mekanikleri
- 3 zorluk seviyesi
- Power-up sistemi
- Ses ve müzik sistemi
- Skor kaydetme
- Ana menü ve ayarlar

### Features
- Combo sistemi
- Animasyonlar
- Parçacık efektleri
- 3 farklı müzik stili
# Katkıda Bulunma Rehberi

## Nasıl Katkıda Bulunabilirim?
1. Issue açarak hata bildirebilirsiniz
2. Yeni özellikler önerebilirsiniz
3. Kod geliştirmeleri yapabilirsiniz
4. Dokümantasyon iyileştirmeleri yapabilirsiniz

## Kod Standartları
- PEP 8 standartlarına uyun
- Anlamlı değişken isimleri kullanın
- Yorum satırları ekleyin
- Test edin

## Pull Request Süreci
1. Fork'layın
2. Branch oluşturun
3. Değişiklikleri yapın
4. Test edin
5. Pull Request açın
