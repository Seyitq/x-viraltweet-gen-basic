# 🐦 X (Twitter) Viral İçerik Üretici

X (Twitter) platformu için yapay zeka destekli viral içerik üretme aracı.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-green.svg)
![Status](https://img.shields.io/badge/Status-Beta-yellow.svg)

## 📖 Hakkında

Bu proje, X (Twitter) için viral içerik üretmeyi kolaylaştıran basit bir Streamlit uygulamasıdır. Yapay zeka modelleri kullanarak gündem analizi yapar ve içerik önerileri sunar.

> ⚠️ **Not:** Bu proje büyük ölçüde yapay zeka araçları (GitHub Copilot, Claude, vb.) kullanılarak geliştirilmiştir ve hala geliştirme aşamasındadır.

## ✨ Özellikler

- 🤖 **Çoklu AI Desteği** - Google Gemini, OpenAI GPT ve Anthropic Claude
- 📊 **Gündem Analizi** - Twitter trendlerini analiz etme
- ✍️ **İçerik Üretimi** - Viral tweet ve thread oluşturma
- 👤 **Persona Yönetimi** - Farklı yazım tarzları tanımlama
- 📈 **Profil İstatistikleri** - Hesap performans takibi

## 🚀 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/kullanici/x-tweet.git
cd x-tweet
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. `.env.example` dosyasını `.env` olarak kopyalayın ve API anahtarlarınızı ekleyin:
```bash
cp .env.example .env
```

4. Uygulamayı başlatın:
```bash
streamlit run app.py
```

## ⚙️ Gereksinimler

- Python 3.8+
- X (Twitter) API anahtarları
- AI API anahtarı (Gemini, OpenAI veya Anthropic)

## 📦 Bağımlılıklar

| Paket | Açıklama |
|-------|----------|
| `streamlit` | Web arayüzü |
| `google-generativeai` | Google Gemini AI |
| `openai` | OpenAI GPT |
| `anthropic` | Anthropic Claude |
| `tweepy` | Twitter API |
| `python-dotenv` | Ortam değişkenleri |

## 🛠️ Geliştirme

Bu proje **basit** ve **geliştirmeye açık** bir yapıdadır. Katkıda bulunmak isterseniz:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

### 💡 Geliştirme Fikirleri

- [ ] Daha fazla AI modeli desteği
- [ ] Zamanlanmış tweet gönderimi
- [ ] Analytics dashboard geliştirmeleri
- [ ] Çoklu hesap desteği
- [ ] Daha gelişmiş persona özellikleri

## 📄 Lisans

Bu proje MIT lisansı altında sunulmaktadır.

## 🤝 Katkıda Bulunanlar

Bu proje yapay zeka araçlarının yardımıyla oluşturulmuştur.

---

<p align="center">
  <sub>🤖 Bu proje AI destekli araçlar kullanılarak geliştirilmiştir</sub>
</p>
