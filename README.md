# ⚽ Football Data Engineering Project

Premier League 2023/24 sezonunun veri mühendisliği ve analiz projesi. ETL pipeline'ı, veritabanı ve interaktif dashboard içerir.

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.25.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📸 Dashboard Görüntüleri



## 🚀 Özellikler

- **Veri Toplama**: Football-Data.org API'sinden otomatik veri çekme
- **ETL Pipeline**: Veri temizleme, dönüştürme ve yükleme
- **Veritabanı**: SQLite ile yapılandırılmış veri depolama
- **İnteraktif Dashboard**: Streamlit ile görselleştirme
- **Analizler**:
  - Puan durumu ve takım performansları
  - Maç istatistikleri ve trendler
  - Ev sahibi/deplasman analizleri
  - Takım karşılaştırmaları
  - Sezon rekorları

## 🛠️ Teknolojiler

- **Python 3.12**
- **Pandas & NumPy**: Veri işleme
- **SQLite**: Veritabanı
- **Streamlit**: Web dashboard
- **Plotly**: İnteraktif grafikler
- **Football-Data.org API**: Veri kaynağı

## 📦 Kurulum

### 1. Repository'yi klonlayın:

- git clone https://github.com/cagatayserttas/football-data-engineering.git
- cd football-data-engineering


### 2. Virtual environment oluşturun:

• Windows:
- python -m venv venv
- venv\Scripts\activate

• Linux/Mac:
-python -m venv venv
-source venv/bin/activate

### 3. Gereksinimleri yükleyin:

-pip install -r requirements.txt

### 4. .env dosyası oluşturun ve API anahtarınızı ekleyin:

-FOOTBALL_DATA_API_KEY=your_api_key_here

## 🏃‍♂️ Kullanım

### 1. Veri Çekme

-python src/extractors/football_data_extractor.py

### 2. Veri Dönüştürme

-python src/transformers/football_data_transformer.py

### 3. Veritabanına Yükleme

-python src/loaders/database_loader.py

### 4. Dashboard'u Başlatma

-streamlit run dashboard/app.py


## 📊 Veritabanı Şeması

### Tablolar:
- **teams**: Takım bilgileri
- **seasons**: Sezon bilgileri
- **standings**: Puan durumu
- **matches**: Maç detayları

## 🎯 Dashboard Özellikleri

### Ana Sayfa
- Sezon özet istatistikleri
- Top 5 takım grafiği
- En çok gol atan/en az gol yiyen takımlar

### Puan Durumu
- Detaylı lig tablosu
- Renk kodlaması (Şampiyonlar Ligi, Avrupa Ligi, Küme düşme)

### Maç Analizi
- Takım ve hafta bazlı filtreleme
- Gol dağılımı grafikleri
- En yüksek skorlu maçlar

### Takım Performansı
- Detaylı takım istatistikleri
- Ev sahibi/deplasman performans karşılaştırması
- Form analizi
- Sezon boyunca tüm maçlar

### Detaylı İstatistikler
- Lig geneli trendler
- Takım karşılaştırmaları
- Radar grafikler
- Sezon rekorları

## 🚀 Gelecek Geliştirmeler

- [ ] Oyuncu bazlı istatistikler
- [ ] Tahmin modelleri (ML)
- [ ] Canlı veri güncellemeleri
- [ ] Çoklu lig desteği
- [ ] PDF/Excel export

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için lütfen önce issue açın.

### Geliştirme Adımları:
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'e push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [Football-Data.org](https://www.football-data.org/) - Veri sağlayıcı


## 📞 İletişim
Mail : ["cagatayserttas@hotmail.com"]
Proje Linki: [https://github.com/cagatayserttas/football-data-engineering](https://github.com/cagatayserttas/football-data-engineering)

---



