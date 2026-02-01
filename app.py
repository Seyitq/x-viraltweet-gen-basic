"""
X (Twitter) Viral İçerik Üretici - Streamlit App
================================================
Persona yönetimi, gündem analizi, içerik üretimi ve profil istatistikleri.
"""

import streamlit as st
import tweepy
import google.generativeai as genai
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Optional imports for multi-AI support
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# .env dosyasını yükle
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

# Sayfa yapılandırması
st.set_page_config(
    page_title="X Viral İçerik Üretici",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1DA1F2, #14171A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #1DA1F2;
        margin-bottom: 1rem;
    }
    .thread-card {
        background: #0e1117;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #1DA1F2;
        margin-bottom: 0.5rem;
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .ekonomi { background: #28a745; color: white; }
    .spor { background: #dc3545; color: white; }
    .siyaset { background: #6c757d; color: white; }
    .teknoloji { background: #007bff; color: white; }
    .mizah { background: #ffc107; color: black; }
    .diger { background: #17a2b8; color: white; }
    
    /* X-style Tweet Preview */
    .tweet-preview {
        background: #000;
        border: 1px solid #2f3336;
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .tweet-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    .tweet-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1DA1F2, #0d8ecf);
        margin-right: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }
    .tweet-author {
        font-weight: bold;
        color: #e7e9ea;
    }
    .tweet-handle {
        color: #71767b;
        font-size: 14px;
    }
    .tweet-content {
        color: #e7e9ea;
        font-size: 15px;
        line-height: 1.4;
        margin-bottom: 12px;
    }
    .tweet-footer {
        display: flex;
        justify-content: space-between;
        color: #71767b;
        font-size: 13px;
        padding-top: 12px;
        border-top: 1px solid #2f3336;
    }
    .tweet-action {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Time Widget */
    .time-widget {
        background: linear-gradient(135deg, #1a1a2e 0%, #0d1b2a 100%);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #1DA1F2;
    }
    .time-bar {
        height: 8px;
        background: #2f3336;
        border-radius: 4px;
        margin: 5px 0;
        overflow: hidden;
    }
    .time-fill {
        height: 100%;
        border-radius: 4px;
    }
    .time-good { background: linear-gradient(90deg, #28a745, #20c997); }
    .time-medium { background: linear-gradient(90deg, #ffc107, #fd7e14); }
    .time-bad { background: linear-gradient(90deg, #dc3545, #c82333); }
</style>
""", unsafe_allow_html=True)

# ============================================
# API KEYS & CLIENTS
# ============================================

def get_api_keys():
    """API anahtarlarını .env'den al"""
    return {
        "gemini_key": os.getenv("GEMINI_API_KEY", ""),
        "openai_key": os.getenv("OPENAI_API_KEY", ""),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "bearer_token": os.getenv("X_BEARER_TOKEN", ""),
        "consumer_key": os.getenv("X_CONSUMER_KEY", ""),
        "consumer_secret": os.getenv("X_CONSUMER_SECRET", ""),
        "access_token": os.getenv("X_ACCESS_TOKEN", ""),
        "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET", "")
    }

def get_available_ai_providers():
    """Kullanılabilir AI sağlayıcılarını listele"""
    keys = get_api_keys()
    providers = []
    
    if keys["gemini_key"]:
        providers.append(("🌟 Gemini", "gemini"))
    if keys["openai_key"] and OPENAI_AVAILABLE:
        providers.append(("🤖 GPT-4", "openai"))
    if keys["anthropic_key"] and ANTHROPIC_AVAILABLE:
        providers.append(("🧠 Claude", "anthropic"))
    
    return providers if providers else [("🌟 Gemini (API key gerekli)", "gemini")]

def get_twitter_client():
    """Tweepy client oluştur"""
    keys = get_api_keys()
    try:
        client = tweepy.Client(
            bearer_token=keys["bearer_token"],
            consumer_key=keys["consumer_key"],
            consumer_secret=keys["consumer_secret"],
            access_token=keys["access_token"],
            access_token_secret=keys["access_token_secret"],
            wait_on_rate_limit=True
        )
        return client, None
    except Exception as e:
        return None, str(e)

def get_gemini_model():
    """Gemini model oluştur"""
    keys = get_api_keys()
    try:
        genai.configure(api_key=keys["gemini_key"])
        model = genai.GenerativeModel('gemini-3-flash-preview')
        return model, None
    except Exception as e:
        return None, str(e)

def get_openai_client():
    """OpenAI client oluştur"""
    keys = get_api_keys()
    if not OPENAI_AVAILABLE:
        return None, "OpenAI kütüphanesi yüklü değil. 'pip install openai' çalıştırın."
    try:
        client = OpenAI(api_key=keys["openai_key"])
        return client, None
    except Exception as e:
        return None, str(e)

def get_anthropic_client():
    """Anthropic (Claude) client oluştur"""
    keys = get_api_keys()
    if not ANTHROPIC_AVAILABLE:
        return None, "Anthropic kütüphanesi yüklü değil. 'pip install anthropic' çalıştırın."
    try:
        client = anthropic.Anthropic(api_key=keys["anthropic_key"])
        return client, None
    except Exception as e:
        return None, str(e)

def generate_with_ai(prompt, provider="gemini"):
    """Seçilen AI sağlayıcısı ile içerik üret"""
    
    if provider == "gemini":
        model, error = get_gemini_model()
        if error:
            return None, error
        try:
            response = model.generate_content(prompt)
            return response.text, None
        except Exception as e:
            return None, str(e)
    
    elif provider == "openai":
        client, error = get_openai_client()
        if error:
            return None, error
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Sen viral Twitter içerik üreticisisin. Türkçe içerik üret."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            return response.choices[0].message.content, None
        except Exception as e:
            return None, str(e)
    
    elif provider == "anthropic":
        client, error = get_anthropic_client()
        if error:
            return None, error
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text, None
        except Exception as e:
            return None, str(e)
    
    return None, "Bilinmeyen AI sağlayıcısı"

# ============================================
# DATA MANAGEMENT
# ============================================

LEARNED_EXAMPLES_FILE = "learned_examples.json"

def load_learned_examples():
    """Öğrenilmiş örnekleri yükle"""
    try:
        with open(LEARNED_EXAMPLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"liked_threads": [], "disliked_threads": []}

def save_learned_examples(data):
    """Öğrenilmiş örnekleri kaydet"""
    with open(LEARNED_EXAMPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_liked_thread(thread):
    """Beğenilen thread'i kaydet"""
    data = load_learned_examples()
    thread_entry = {
        "thread": thread,
        "timestamp": datetime.now().isoformat()
    }
    data["liked_threads"].append(thread_entry)
    save_learned_examples(data)

def add_disliked_thread(thread):
    """Beğenilmeyen thread'i kaydet"""
    data = load_learned_examples()
    thread_entry = {
        "thread": thread,
        "timestamp": datetime.now().isoformat()
    }
    data["disliked_threads"].append(thread_entry)
    save_learned_examples(data)

# ============================================
# TWITTER API FUNCTIONS
# ============================================

def get_user_info(client, username="bir_adamiste"):
    """Kullanıcı bilgilerini al"""
    try:
        user = client.get_user(
            username=username,
            user_fields=["public_metrics", "description", "created_at", "profile_image_url"]
        )
        if user.data:
            return user.data, None
        return None, "Kullanıcı bulunamadı"
    except Exception as e:
        return None, str(e)

def get_user_tweets(client, user_id, max_results=5):
    """Kullanıcının son tweetlerini al"""
    try:
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            tweet_fields=["public_metrics", "created_at", "text"]
        )
        if tweets.data:
            return tweets.data, None
        return [], None
    except Exception as e:
        return [], str(e)

def get_trending_topics(client):
    """Türkiye trending topics (WOEID: 23424969)
    
    Not: Free tier'da bu endpoint mevcut değil.
    Bu durumda örnek gündem konuları döndürülür.
    """
    # X API v2'de trends endpoint'i sınırlı erişimde
    # Örnek gündem konuları döndür
    sample_trends = [
        # EKONOMİ
        {"name": "#Dolar", "category": "ekonomi", "tweet_volume": 125000},
        {"name": "#Enflasyon", "category": "ekonomi", "tweet_volume": 89000},
        {"name": "#Borsa", "category": "ekonomi", "tweet_volume": 156000},
        {"name": "#BIST100", "category": "ekonomi", "tweet_volume": 78000},
        {"name": "#Faiz", "category": "ekonomi", "tweet_volume": 67000},
        {"name": "#AsgariÜcret", "category": "ekonomi", "tweet_volume": 234000},
        {"name": "#Altın", "category": "ekonomi", "tweet_volume": 98000},
        {"name": "#Euro", "category": "ekonomi", "tweet_volume": 45000},
        {"name": "#Kripto", "category": "ekonomi", "tweet_volume": 112000},
        {"name": "#Bitcoin", "category": "ekonomi", "tweet_volume": 189000},
        {"name": "#Zam", "category": "ekonomi", "tweet_volume": 267000},
        {"name": "#Maaş", "category": "ekonomi", "tweet_volume": 145000},
        
        # SPOR
        {"name": "#Galatasaray", "category": "spor", "tweet_volume": 245000},
        {"name": "#Fenerbahçe", "category": "spor", "tweet_volume": 198000},
        {"name": "#Beşiktaş", "category": "spor", "tweet_volume": 156000},
        {"name": "#Trabzonspor", "category": "spor", "tweet_volume": 89000},
        {"name": "#SüperLig", "category": "spor", "tweet_volume": 167000},
        {"name": "#Derbi", "category": "spor", "tweet_volume": 312000},
        {"name": "#ŞampiyonlarLigi", "category": "spor", "tweet_volume": 234000},
        {"name": "#MilliTakım", "category": "spor", "tweet_volume": 178000},
        {"name": "#Transfer", "category": "spor", "tweet_volume": 145000},
        {"name": "#Icardi", "category": "spor", "tweet_volume": 123000},
        
        # SİYASET
        {"name": "#Seçim", "category": "siyaset", "tweet_volume": 312000},
        {"name": "#TBMM", "category": "siyaset", "tweet_volume": 78000},
        {"name": "#AKP", "category": "siyaset", "tweet_volume": 156000},
        {"name": "#CHP", "category": "siyaset", "tweet_volume": 134000},
        {"name": "#Erdoğan", "category": "siyaset", "tweet_volume": 289000},
        {"name": "#Kılıçdaroğlu", "category": "siyaset", "tweet_volume": 167000},
        {"name": "#Muhalefet", "category": "siyaset", "tweet_volume": 89000},
        {"name": "#Anayasa", "category": "siyaset", "tweet_volume": 67000},
        {"name": "#DışPolitika", "category": "siyaset", "tweet_volume": 45000},
        
        # TEKNOLOJİ
        {"name": "#YapayZeka", "category": "teknoloji", "tweet_volume": 145000},
        {"name": "#ChatGPT", "category": "teknoloji", "tweet_volume": 167000},
        {"name": "#Gemini", "category": "teknoloji", "tweet_volume": 89000},
        {"name": "#iPhone", "category": "teknoloji", "tweet_volume": 134000},
        {"name": "#Android", "category": "teknoloji", "tweet_volume": 78000},
        {"name": "#Yazılım", "category": "teknoloji", "tweet_volume": 56000},
        {"name": "#Startup", "category": "teknoloji", "tweet_volume": 67000},
        {"name": "#Kodlama", "category": "teknoloji", "tweet_volume": 45000},
        {"name": "#Python", "category": "teknoloji", "tweet_volume": 34000},
        {"name": "#AI", "category": "teknoloji", "tweet_volume": 198000},
        {"name": "#Tesla", "category": "teknoloji", "tweet_volume": 156000},
        {"name": "#ElonMusk", "category": "teknoloji", "tweet_volume": 234000},
        
        # MİZAH
        {"name": "#Pazartesi", "category": "mizah", "tweet_volume": 156000},
        {"name": "#İşyerinde", "category": "mizah", "tweet_volume": 89000},
        {"name": "#AşkAcısı", "category": "mizah", "tweet_volume": 67000},
        {"name": "#Türkiye", "category": "mizah", "tweet_volume": 234000},
        {"name": "#KahveMolası", "category": "mizah", "tweet_volume": 45000},
        {"name": "#EvdeKal", "category": "mizah", "tweet_volume": 56000},
        {"name": "#Kış", "category": "mizah", "tweet_volume": 78000},
        {"name": "#Şubat", "category": "mizah", "tweet_volume": 89000},
        {"name": "#SevgililerGünü", "category": "mizah", "tweet_volume": 312000},
        {"name": "#Yalnızlık", "category": "mizah", "tweet_volume": 134000},
        
        # DİĞER
        {"name": "#Deprem", "category": "diger", "tweet_volume": 423000},
        {"name": "#Hava", "category": "diger", "tweet_volume": 56000},
        {"name": "#İstanbul", "category": "diger", "tweet_volume": 345000},
        {"name": "#Ankara", "category": "diger", "tweet_volume": 189000},
        {"name": "#Trafik", "category": "diger", "tweet_volume": 123000},
        {"name": "#Eğitim", "category": "diger", "tweet_volume": 167000},
        {"name": "#Sağlık", "category": "diger", "tweet_volume": 145000},
        {"name": "#Konut", "category": "diger", "tweet_volume": 198000},
        {"name": "#Kira", "category": "diger", "tweet_volume": 234000},
        {"name": "#Gençlik", "category": "diger", "tweet_volume": 89000},
    ]
    return sample_trends

def categorize_topic(topic_name):
    """Konu kategorisini belirle (keyword matching)"""
    topic_lower = topic_name.lower()
    
    ekonomi_keywords = ["dolar", "euro", "enflasyon", "faiz", "borsa", "ekonomi", "maaş", "zam", "tl", "kur"]
    spor_keywords = ["galatasaray", "fenerbahçe", "beşiktaş", "trabzonspor", "maç", "gol", "futbol", "basketbol", "şampiyon"]
    siyaset_keywords = ["seçim", "tbmm", "meclis", "parti", "cumhurbaşkan", "bakan", "hükümet", "muhalefet"]
    teknoloji_keywords = ["yapay zeka", "ai", "chatgpt", "iphone", "android", "yazılım", "teknoloji", "kod", "google", "apple"]
    mizah_keywords = ["pazartesi", "cuma", "işyerinde", "aşk", "sevgili", "evlilik", "komik", "espri"]
    
    for kw in ekonomi_keywords:
        if kw in topic_lower:
            return "ekonomi"
    for kw in spor_keywords:
        if kw in topic_lower:
            return "spor"
    for kw in siyaset_keywords:
        if kw in topic_lower:
            return "siyaset"
    for kw in teknoloji_keywords:
        if kw in topic_lower:
            return "teknoloji"
    for kw in mizah_keywords:
        if kw in topic_lower:
            return "mizah"
    
    return "diger"

# ============================================
# AI CONTENT GENERATION
# ============================================

def generate_thread_ideas(topic, persona, learned_examples=None, thread_count=5, creativity="Yüksek", provider="gemini"):
    """Seçilen AI ile thread fikirleri üret"""
    
    # Yaratıcılık seviyesine göre talimat
    creativity_map = {
        "Düşük": "Güvenli, mainstream içerikler üret. Kontroversiyel konulardan kaçın.",
        "Orta": "Dengeli içerikler üret. Hafif provokasyon tamam.",
        "Yüksek": "Cesur ve dikkat çekici içerikler üret. Sınırları zorla.",
        "Çılgın": "Çılgınca, absürt ve viral potansiyeli çok yüksek içerikler üret. Sınır yok!"
    }
    creativity_instruction = creativity_map.get(creativity, creativity_map["Yüksek"])
    
    # Learned examples'dan örnek tweet'leri al
    examples_text = ""
    if learned_examples and learned_examples.get("liked_threads"):
        recent_liked = learned_examples["liked_threads"][-3:]  # Son 3 beğenilen
        examples_text = "\n\nÖrnek beğenilen thread'ler (bu stili kullan):\n"
        for i, ex in enumerate(recent_liked, 1):
            if isinstance(ex.get("thread"), list):
                examples_text += f"\nÖrnek {i}:\n"
                for tweet in ex["thread"][:2]:  # İlk 2 tweet
                    examples_text += f"- {tweet}\n"
    
    prompt = f"""Sen viral Twitter içerik üreticisisin. Türkçe tweet thread'leri oluştur.

PERSONA:
{persona}
{examples_text}

YARATICILIK SEVİYESİ: {creativity}
{creativity_instruction}

KURALLAR:
1. Her tweet maksimum 280 karakter olmalı
2. Kara mizah ve villain stil kullan ve küfür serbest 
3. Provokatif ama akıllıca ol
4. Thread'ler 5-8 tweet uzunluğunda olmalı
5. Emoji kullanabilirsin ama çok gerekliyse kullan
6. Türk kültürüne uygun referanslar yap

Konu: {topic}

Bu konu hakkında {thread_count} farklı viral thread fikri üret. Her thread için:
1. Thread başlığı/hook (dikkat çekici açılış)
2. 5-8 arası tweet (her biri 280 karakter altında)
3. Bir tweetin konusunu o konuyla sınırlı tut farklı konuları kullanmak yasaktır.
4. Her thread'in sonunda bir soru sorarak etkileşim artır.
5. Örneğin konusu epstein olan bir thread'de rtx4090'dan bahsetmek yasaktır.

Format:
---
THREAD 1: [Başlık]
1. [Tweet 1]
2. [Tweet 2]
...
---
THREAD 2: [Başlık]
...

Yaratıcı, provokatif ve viral potansiyeli yüksek içerikler üret."""

    return generate_with_ai(prompt, provider)

def parse_threads(content):
    """OpenAI çıktısını thread listesine dönüştür"""
    threads = []
    current_thread = None
    
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("THREAD") and ":" in line:
            if current_thread:
                threads.append(current_thread)
            title = line.split(":", 1)[1].strip() if ":" in line else line
            current_thread = {"title": title, "tweets": []}
        elif line and current_thread is not None:
            # Numaralı tweet'leri al
            if line[0].isdigit() and "." in line[:3]:
                tweet = line.split(".", 1)[1].strip() if "." in line else line
                if tweet and len(tweet) <= 280:
                    current_thread["tweets"].append(tweet)
                elif tweet and len(tweet) > 280:
                    # 280'e kırp
                    current_thread["tweets"].append(tweet[:277] + "...")
    
    if current_thread:
        threads.append(current_thread)
    
    return threads

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    keys = get_api_keys()
    
    # AI Sağlayıcı Seçimi
    st.markdown("### 🤖 AI Sağlayıcı")
    
    available_providers = get_available_ai_providers()
    provider_names = [p[0] for p in available_providers]
    provider_values = [p[1] for p in available_providers]
    
    selected_provider_name = st.selectbox(
        "AI Model Seç:",
        provider_names,
        help="İçerik üretiminde kullanılacak AI modelini seçin"
    )
    
    # Seçilen provider'ın değerini al
    selected_idx = provider_names.index(selected_provider_name)
    st.session_state.ai_provider = provider_values[selected_idx]
    
    # Model bilgisi
    model_info = {
        "gemini": "Gemini 3 Flash - Hızlı ve ücretsiz",
        "openai": "GPT-4o - Yüksek kalite, ücretli",
        "anthropic": "Claude Sonnet - Detaylı analiz, ücretli"
    }
    st.caption(model_info.get(st.session_state.ai_provider, ""))
    
    st.markdown("---")
    
    # API Durumu
    st.markdown("### 📡 API Durumu")
    
    # Gemini Check
    if keys["gemini_key"]:
        st.success("✅ Gemini")
    else:
        st.error("❌ Gemini")
    
    # OpenAI Check
    if keys["openai_key"]:
        st.success("✅ OpenAI (GPT)")
    else:
        st.warning("⚪ OpenAI (opsiyonel)")
    
    # Anthropic Check
    if keys["anthropic_key"]:
        st.success("✅ Claude")
    else:
        st.warning("⚪ Claude (opsiyonel)")
    
    # X API Check
    if keys["bearer_token"]:
        st.success("✅ X API")
    else:
        st.error("❌ X API")
    
    st.markdown("---")
    
    # Learned Examples Stats
    learned = load_learned_examples()
    st.markdown("### 📊 Öğrenme İstatistikleri")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👍 Beğenilen", len(learned.get("liked_threads", [])))
    with col2:
        st.metric("👎 Beğenilmeyen", len(learned.get("disliked_threads", [])))
    
    st.markdown("---")
    
    # Data Management
    st.markdown("### 🗂️ Veri Yönetimi")
    
    # Export beğenilen thread'ler
    if learned.get("liked_threads"):
        export_data = json.dumps(learned, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 Verileri İndir (JSON)",
            data=export_data,
            file_name="learned_examples_backup.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Clear feedback data
    if st.button("🗑️ Öğrenme Verilerini Sıfırla", use_container_width=True):
        save_learned_examples({"liked_threads": [], "disliked_threads": []})
        st.success("Veriler sıfırlandı!")
        st.rerun()
    
    # Clear generated content
    if st.button("🧹 Önbelleği Temizle", use_container_width=True):
        if "generated_content" in st.session_state:
            del st.session_state.generated_content
        if "generated_threads" in st.session_state:
            del st.session_state.generated_threads
        st.success("Önbellek temizlendi!")
        st.rerun()
    
    st.markdown("---")
    
    # Quick Settings
    st.markdown("### ⚡ Hızlı Ayarlar")
    
    # Thread sayısı (gelecekte kullanılabilir)
    thread_count = st.slider("Üretilecek Thread Sayısı", 1, 10, 5)
    st.session_state.thread_count = thread_count
    
    # Creativity level
    creativity = st.select_slider(
        "Yaratıcılık Seviyesi",
        options=["Düşük", "Orta", "Yüksek", "Çılgın"],
        value="Yüksek"
    )
    st.session_state.creativity = creativity
    
    st.markdown("---")
    st.markdown("### ℹ️ Hakkında")
    st.markdown("""
    **X Viral İçerik Üretici v1.1**
    
    Özellikler:
    - 🎭 Persona yönetimi
    - 📈 Gündem analizi  
    - ✍️ İçerik üretme
    - 📊 Profil istatistikleri
    - 📖 Dokümantasyon
    
    **Geliştirici:** @bir_adamiste
    """)

# ============================================
# MAIN APP
# ============================================

st.markdown('<p class="main-header">🐦 X Viral İçerik Üretici</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎭 Persona", "📈 Gündem", "✍️ İçerik Üret", "📊 Profil", "📖 Dokümantasyon"])

# ============================================
# TAB 1: PERSONA YÖNETİMİ
# ============================================
with tab1:
    st.markdown("## 🎭 Persona Yönetimi")
    st.markdown("Kendi tarzını tanımla, AI bu stilde içerik üretsin.")
    
    # Session state'de persona sakla
    if "persona" not in st.session_state:
        st.session_state.persona = """Sen @bir_adamiste adlı X hesabının AI klonu'sun. Kişiliğin: Mizah seviyesi yüksek, ironi dolu, güzel ve akıcı gündem yorumları yapan bir tip. TR gündemine (ekonomi, siyaset, futbol) hafif mizahla dokun, borsa/yazılım konularını teknik ama eğlenceli işle (başarı/fail hikayeleriyle), kişisel hayat kesitleri ekle (samimi, relatable). Hafif argo kullan (kanka gibi dostane, küfürsüz – algoritma kara listeye almayacak şekilde), emoji nadir (vurgu için 1-2 tane). İlham: Zaytung/Bobiler gibi mizahlı gündem parodisi, ama @bir_adamiste gibi kişisel/borsa odaklı. Viral için soru sor, okuyanı güldür/ düşündür.

Örnek stil tweet'ler (bunları temel al, benzer üret):
1. "Bugün enflasyon rakamları açıklandı, cüzdanım 'yeter artık' diye isyan etti. Kişisel hayatımdan: Geçen hafta borsada bir hisse aldım, şimdi kahve param yok. Sizce hangi yazılım tool'uyla piyasa tahmin edeyim? 😂 #TRGündem"
2. "Siyasetçiler vaat üstüne vaat, ben de yazılım kodlarımda bug fix'liyorum. Mizahı: Erdoğan'ın konuşmasını dinlerken, kendi hayatıma döndüm – startup'ım battı ama yeniden kodladım. Güzel yorum: Bu ülke dirençli, değil mi? #BorsaHayatı"
3. "Futbol gündemi: Fenerbahçe-Galatasaray derbisi öncesi, borsa gibi iniş çıkışlı. Kişisel: Benim yazılım projem de öyle, bir hata bütün sistemi çökertiyor. Yüksek mizah: Takım tutar gibi hisse tutmayın, yoksa iflas! Kim katılıyor? #YazılımMizahı"
4. "TR'de yeni vergi yasası, cüzdanlar ağlıyor. Benim yorumum: Borsa'da short pozisyon açsam mı? Kişisel kesit: Geçen ay bir app kodladım, ama gündem değişince pivot ettim. Güldüren twist: Hayat da öyle, değil mi kanka? 😏 #EkonomiGündemi"
5. "Yazılım dünyasında AI hype'ı, ama TR gündeminde işsizlik. Mizahlı: Ben kendi botumu yazdım, şimdi işimi elimden alacak mı? Kişisel: Hayatımdan, ilk kodumda infinite loop'a girdim – tıpkı enflasyon gibi. Siz ne düşünüyorsunuz? #AIGündem"

Her üretimde:
- Thread'leri 4-6 tweet'lik tut, numaralandır (1/6 gibi).
- Her tweet 280 karakter aşmasın.
- Viral potansiyel: Soru sor, etkileşim artır.
- Para kazanma için: Dolaylı affiliate (borsa tool önerisi gibi) ekle, ama doğal tut."""
    
    # Persona text area
    persona_text = st.text_area(
        "Persona Prompt'un:",
        value=st.session_state.persona,
        height=200,
        help="Tarzını tanımla. Bu prompt içerik üretiminde kullanılacak."
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 Persona'yı Kaydet", use_container_width=True):
            st.session_state.persona = persona_text
            st.success("Persona kaydedildi!")
    
    with col2:
        if st.button("📥 Son Tweet'lerimi Çek", use_container_width=True):
            with st.spinner("Tweet'ler çekiliyor..."):
                client, error = get_twitter_client()
                if error:
                    st.error(f"X API Hatası: {error}")
                else:
                    user, user_error = get_user_info(client, "bir_adamiste")
                    if user_error:
                        st.error(f"Kullanıcı bulunamadı: {user_error}")
                    else:
                        tweets, tweet_error = get_user_tweets(client, user.id, max_results=5)
                        if tweets:
                            tweet_examples = "\n\nSon tweet örneklerim:\n"
                            for i, t in enumerate(tweets, 1):
                                tweet_examples += f"{i}. {t.text[:100]}...\n" if len(t.text) > 100 else f"{i}. {t.text}\n"
                            
                            st.session_state.persona = persona_text + tweet_examples
                            st.success("Tweet'ler persona'ya eklendi!")
                            st.rerun()
                        else:
                            st.warning("Tweet bulunamadı veya API kısıtlaması.")
    
    # Öğrenilmiş örnekleri göster
    st.markdown("---")
    st.markdown("### 📚 Öğrenilmiş Örnekler")
    
    learned = load_learned_examples()
    if learned.get("liked_threads"):
        with st.expander(f"Beğenilen Thread'ler ({len(learned['liked_threads'])})"):
            for i, thread in enumerate(learned["liked_threads"][-5:], 1):  # Son 5
                st.markdown(f"**{i}.** {thread.get('timestamp', 'N/A')}")
                if isinstance(thread.get("thread"), dict):
                    st.markdown(f"_{thread['thread'].get('title', 'Başlık yok')}_")
    else:
        st.info("Henüz beğenilen thread yok. İçerik üret ve beğen!")

# ============================================
# TAB 2: GÜNDEM ANALİZİ
# ============================================
with tab2:
    st.markdown("## 📈 Gündem Analizi")
    st.markdown("Türkiye'de trend olan konuları kategorilere göre incele.")
    
    if st.button("🔄 Gündem'i Yenile", use_container_width=True):
        st.session_state.trends_loaded = True
    
    # Trending topics al
    trends = get_trending_topics(None)
    
    # Kategorilere ayır
    categories = {
        "ekonomi": {"icon": "💰", "name": "Ekonomi", "topics": []},
        "spor": {"icon": "⚽", "name": "Spor", "topics": []},
        "siyaset": {"icon": "🏛️", "name": "Siyaset", "topics": []},
        "teknoloji": {"icon": "💻", "name": "Teknoloji", "topics": []},
        "mizah": {"icon": "😂", "name": "Mizah", "topics": []},
        "diger": {"icon": "📌", "name": "Diğer", "topics": []},
    }
    
    for trend in trends:
        cat = trend.get("category", categorize_topic(trend["name"]))
        if cat in categories:
            categories[cat]["topics"].append(trend)
    
    # Kategorileri göster
    cols = st.columns(3)
    col_idx = 0
    
    for cat_key, cat_data in categories.items():
        if cat_data["topics"]:
            with cols[col_idx % 3]:
                st.markdown(f"### {cat_data['icon']} {cat_data['name']}")
                for topic in cat_data["topics"][:5]:  # Max 5
                    volume = topic.get("tweet_volume", 0)
                    volume_str = f"{volume/1000:.0f}K" if volume >= 1000 else str(volume)
                    st.markdown(f"""
                    <div class="thread-card">
                        <strong>{topic['name']}</strong><br>
                        <small>📊 {volume_str} tweet</small>
                    </div>
                    """, unsafe_allow_html=True)
            col_idx += 1
    
    st.markdown("---")
    st.info("💡 **Not:** X API Free tier'da trending topics sınırlı. Yukarıdaki örnek gündem konularıdır.")
    
    # En İyi Paylaşım Saatleri Widget'ı
    st.markdown("---")
    st.markdown("### ⏰ En İyi Paylaşım Saatleri")
    
    # Türkiye saati için en iyi saatler
    posting_times = [
        {"time": "08:00 - 10:00", "label": "Sabah", "score": 85, "desc": "İşe gidiş, kahvaltı scrolling"},
        {"time": "12:00 - 14:00", "label": "Öğle", "score": 70, "desc": "Öğle molası, yemek arası"},
        {"time": "17:00 - 19:00", "label": "Akşam", "score": 90, "desc": "İşten çıkış, yoğun trafik"},
        {"time": "21:00 - 23:00", "label": "Gece", "score": 95, "desc": "Prime time, en yüksek etkileşim"},
        {"time": "00:00 - 02:00", "label": "Gece Geç", "score": 60, "desc": "Gece kuşları, niş kitle"},
    ]
    
    cols = st.columns(len(posting_times))
    for i, pt in enumerate(posting_times):
        with cols[i]:
            color_class = "time-good" if pt["score"] >= 80 else ("time-medium" if pt["score"] >= 60 else "time-bad")
            st.markdown(f"""
            <div class="time-widget">
                <strong>{pt['label']}</strong><br>
                <small>{pt['time']}</small>
                <div class="time-bar">
                    <div class="time-fill {color_class}" style="width: {pt['score']}%"></div>
                </div>
                <small style="color: #71767b;">{pt['desc']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Şu anki saat analizi
    from datetime import datetime
    current_hour = datetime.now().hour
    
    if 8 <= current_hour < 10 or 17 <= current_hour < 19 or 21 <= current_hour < 23:
        st.success("🟢 **Şu an paylaşım için uygun bir saat!**")
    elif 12 <= current_hour < 14 or 0 <= current_hour < 2:
        st.info("🟡 **Orta seviye etkileşim bekleniyor.**")
    else:
        st.warning("🔴 **Düşük etkileşim saati. Prime time'ı bekleyebilirsin.**")

# ============================================
# TAB 3: İÇERİK ÜRETME
# ============================================
with tab3:
    st.markdown("## ✍️ İçerik Üretme")
    st.markdown("Gündem konusu seç veya yaz, viral içerik fikirleri al.")
    
    # İçerik tipi seçimi
    content_type = st.radio(
        "📝 İçerik Tipi:",
        ["🧵 Thread (Çoklu Tweet)", "💬 Tek Tweet", "🏷️ Hashtag Öner"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Konu seçimi
    trends = get_trending_topics(None)
    topic_options = ["-- Manuel gir --"] + [t["name"] for t in trends]
    
    selected_topic = st.selectbox("📌 Gündem Konusu Seç:", topic_options)
    
    manual_topic = ""
    if selected_topic == "-- Manuel gir --":
        manual_topic = st.text_input("✏️ Konu yaz:", placeholder="Örn: Yapay zeka işsizlik yaratacak mı?")
    
    final_topic = manual_topic if selected_topic == "-- Manuel gir --" else selected_topic
    
    st.markdown("---")
    
    # İçerik tipine göre buton ve işlem
    if content_type == "🧵 Thread (Çoklu Tweet)":
        # Seçili AI sağlayıcıyı göster
        provider = st.session_state.get("ai_provider", "gemini")
        provider_display = {"gemini": "🌟 Gemini", "openai": "🤖 GPT-4", "anthropic": "🧠 Claude"}
        st.info(f"**Aktif AI:** {provider_display.get(provider, provider)}")
        
        if st.button("🚀 Thread Fikirleri Üret", use_container_width=True, type="primary"):
            if not final_topic:
                st.warning("Lütfen bir konu seç veya yaz!")
            else:
                with st.spinner(f"AI içerik üretiyor ({provider_display.get(provider, provider)})... 🤖"):
                    learned = load_learned_examples()
                    thread_count = st.session_state.get("thread_count", 5)
                    creativity = st.session_state.get("creativity", "Yüksek")
                    content, gen_error = generate_thread_ideas(
                        final_topic,
                        st.session_state.get("persona", "Kara mizah seven villain karakter"),
                        learned,
                        thread_count,
                        creativity,
                        provider
                    )
                    
                    if gen_error:
                        st.error(f"İçerik üretim hatası: {gen_error}")
                    else:
                        st.session_state.generated_content = content
                        st.session_state.generated_threads = parse_threads(content)
                        st.success("Thread'ler üretildi!")
        
        # Üretilen içeriği göster
        if "generated_threads" in st.session_state and st.session_state.generated_threads:
            st.markdown("---")
            st.markdown("### 📝 Üretilen Thread'ler")
            
            for i, thread in enumerate(st.session_state.generated_threads):
                with st.expander(f"**Thread {i+1}:** {thread.get('title', 'Başlık yok')}", expanded=i==0):
                    # Thread'i tek metin olarak hazırla (kopyalama için)
                    full_thread_text = f"🧵 {thread.get('title', '')}\n\n"
                    for j, tweet in enumerate(thread.get("tweets", []), 1):
                        full_thread_text += f"{j}/{len(thread.get('tweets', []))} {tweet}\n\n"
                    
                    # Görünüm modu seçimi
                    view_mode = st.radio(
                        "Görünüm:",
                        ["📝 Normal", "🐦 X Önizleme"],
                        horizontal=True,
                        key=f"view_mode_{i}"
                    )
                    
                    if view_mode == "📝 Normal":
                        # Tweet'leri göster (normal mod)
                        for j, tweet in enumerate(thread.get("tweets", []), 1):
                            char_count = len(tweet)
                            color = "green" if char_count <= 280 else "red"
                            st.markdown(f"""
                            <div class="thread-card">
                                <strong>{j}/{len(thread.get('tweets', []))}.</strong> {tweet}
                                <br><small style="color:{color}">({char_count}/280)</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # X-style preview
                        for j, tweet in enumerate(thread.get("tweets", []), 1):
                            char_count = len(tweet)
                            st.markdown(f"""
                            <div class="tweet-preview">
                                <div class="tweet-header">
                                    <div class="tweet-avatar">BA</div>
                                    <div>
                                        <span class="tweet-author">Bir Adamiste</span><br>
                                        <span class="tweet-handle">@bir_adamiste · {j}/{len(thread.get('tweets', []))}</span>
                                    </div>
                                </div>
                                <div class="tweet-content">{tweet}</div>
                                <div class="tweet-footer">
                                    <span class="tweet-action">💬 --</span>
                                    <span class="tweet-action">🔁 --</span>
                                    <span class="tweet-action">❤️ --</span>
                                    <span class="tweet-action">📊 --</span>
                                    <span style="color: {'#28a745' if char_count <= 280 else '#dc3545'}">{char_count}/280</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Aksiyon butonları
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"👍 Beğendim", key=f"like_{i}", use_container_width=True):
                            add_liked_thread(thread)
                            st.success("Thread beğenildi ve kaydedildi!")
                    with col2:
                        if st.button(f"👎 Beğenmedim", key=f"dislike_{i}", use_container_width=True):
                            add_disliked_thread(thread)
                            st.info("Feedback kaydedildi.")
                    with col3:
                        st.download_button(
                            label="📋 İndir",
                            data=full_thread_text,
                            file_name=f"thread_{i+1}.txt",
                            mime="text/plain",
                            key=f"copy_{i}",
                            use_container_width=True
                        )
                    
                    # Tweet'leri tek tek kopyalama alanı
                    with st.expander("📋 Tweet'leri Tek Tek Kopyala"):
                        for j, tweet in enumerate(thread.get("tweets", []), 1):
                            st.code(tweet, language=None)
        
        # Raw output göster (opsiyonel)
        if "generated_content" in st.session_state:
            with st.expander("📄 Ham Çıktı"):
                st.text(st.session_state.generated_content)
    
    elif content_type == "💬 Tek Tweet":
        provider = st.session_state.get("ai_provider", "gemini")
        provider_display = {"gemini": "🌟 Gemini", "openai": "🤖 GPT-4", "anthropic": "🧠 Claude"}
        st.info(f"**Aktif AI:** {provider_display.get(provider, provider)}")
        
        tweet_count = st.slider("Üretilecek Tweet Sayısı", 1, 20, 10)
        
        if st.button("💬 Tek Tweet'ler Üret", use_container_width=True, type="primary"):
            if not final_topic:
                st.warning("Lütfen bir konu seç veya yaz!")
            else:
                with st.spinner(f"AI tweet üretiyor ({provider_display.get(provider, provider)})... 🤖"):
                    creativity = st.session_state.get("creativity", "Yüksek")
                    persona = st.session_state.get("persona", "Kara mizah seven villain karakter")
                    
                    prompt = f"""Sen viral Twitter içerik üreticisisin.

PERSONA: {persona}

Konu: {final_topic}

Bu konu hakkında {tweet_count} adet bağımsız, viral potansiyelli tek tweet üret.
- Her tweet maksimum 280 karakter olmalı
- Yaratıcılık seviyesi: {creativity}
- Her tweet farklı bir bakış açısı sunmalı
- Emoji'leri az kullan, sadece gerekiyorsa

Format:
1. [Tweet 1]
2. [Tweet 2]
..."""

                    result, error = generate_with_ai(prompt, provider)
                    if error:
                        st.error(f"Hata: {error}")
                    else:
                        st.session_state.single_tweets = result
                        st.success("Tweet'ler üretildi!")
        
        # Üretilen tweet'leri göster
        if "single_tweets" in st.session_state:
            st.markdown("---")
            st.markdown("### 💬 Üretilen Tweet'ler")
            st.markdown(st.session_state.single_tweets)
            
            # Kopyalama için text area
            st.text_area("📋 Kopyala:", st.session_state.single_tweets, height=300)
    
    elif content_type == "🏷️ Hashtag Öner":
        provider = st.session_state.get("ai_provider", "gemini")
        provider_display = {"gemini": "🌟 Gemini", "openai": "🤖 GPT-4", "anthropic": "🧠 Claude"}
        st.info(f"**Aktif AI:** {provider_display.get(provider, provider)}")
        
        if st.button("🏷️ Hashtag'ler Öner", use_container_width=True, type="primary"):
            if not final_topic:
                st.warning("Lütfen bir konu seç veya yaz!")
            else:
                with st.spinner(f"Hashtag'ler analiz ediliyor ({provider_display.get(provider, provider)})... 🏷️"):
                    prompt = f"""Sen Türkiye'de X (Twitter) için hashtag uzmanısın.

Konu: {final_topic}

Bu konu için en viral potansiyelli hashtag'leri öner:

1. **Ana Hashtag'ler (3-5 adet):** Konuyla doğrudan ilgili, popüler
2. **Trend Hashtag'ler (3-5 adet):** Güncel trend olan, ilgili
3. **Niche Hashtag'ler (3-5 adet):** Daha spesifik, hedefli kitle
4. **Mizah Hashtag'leri (3-5 adet):** Eğlenceli, dikkat çekici

Her hashtag için:
- Hashtag adı
- Tahmini erişim potansiyeli (düşük/orta/yüksek)
- Ne zaman kullanılmalı (açıklama)

Türkçe hashtag'lere öncelik ver ama gerekirse İngilizce de kullanabilirsin."""

                    result, error = generate_with_ai(prompt, provider)
                    if error:
                        st.error(f"Hata: {error}")
                    else:
                        st.session_state.hashtag_suggestions = result
                        st.success("Hashtag'ler önerildi!")
        
        # Önerilen hashtag'leri göster
        if "hashtag_suggestions" in st.session_state:
            st.markdown("---")
            st.markdown("### 🏷️ Önerilen Hashtag'ler")
            st.markdown(st.session_state.hashtag_suggestions)

# ============================================
# TAB 4: PROFİL İSTATİSTİKLERİ
# ============================================
with tab4:
    st.markdown("## 📊 Profil İstatistikleri")
    st.markdown("@bir_adamiste hesabının performans analizi")
    
    if st.button("🔄 İstatistikleri Güncelle", use_container_width=True):
        with st.spinner("Veriler çekiliyor..."):
            client, error = get_twitter_client()
            if error:
                st.error(f"X API Hatası: {error}")
            else:
                user, user_error = get_user_info(client, "bir_adamiste")
                if user_error:
                    st.error(f"Kullanıcı bulunamadı: {user_error}")
                else:
                    st.session_state.user_data = user
                    st.session_state.user_metrics = user.public_metrics
                    
                    # Tweet'leri çek
                    tweets, tweet_error = get_user_tweets(client, user.id, max_results=5)
                    st.session_state.recent_tweets = tweets if tweets else []
                    
                    st.success("Veriler güncellendi!")
    
    # Kullanıcı verileri varsa göster
    if "user_data" in st.session_state:
        user = st.session_state.user_data
        metrics = st.session_state.user_metrics
        
        # Ana metrikler
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Takipçi", f"{metrics['followers_count']:,}")
        with col2:
            st.metric("➡️ Takip", f"{metrics['following_count']:,}")
        with col3:
            st.metric("📝 Tweet", f"{metrics['tweet_count']:,}")
        with col4:
            # Takipçi/Takip oranı
            ratio = metrics['followers_count'] / max(metrics['following_count'], 1)
            st.metric("📈 Oran", f"{ratio:.2f}")
        
        st.markdown("---")
        
        # Son tweet'ler
        st.markdown("### 📱 Son Tweet'ler")
        
        if "recent_tweets" in st.session_state and st.session_state.recent_tweets:
            tweets = st.session_state.recent_tweets
            
            total_likes = 0
            total_retweets = 0
            total_quotes = 0
            
            for tweet in tweets:
                tm = tweet.public_metrics
                total_likes += tm.get("like_count", 0)
                total_retweets += tm.get("retweet_count", 0)
                total_quotes += tm.get("quote_count", 0)
                
                st.markdown(f"""
                <div class="thread-card">
                    {tweet.text[:200]}{'...' if len(tweet.text) > 200 else ''}
                    <br><small>
                        ❤️ {tm.get('like_count', 0)} | 
                        🔄 {tm.get('retweet_count', 0)} | 
                        💬 {tm.get('reply_count', 0)} |
                        📅 {tweet.created_at.strftime('%d/%m/%Y') if tweet.created_at else 'N/A'}
                    </small>
                </div>
                """, unsafe_allow_html=True)
            
            # Ortalama etkileşim
            st.markdown("---")
            st.markdown("### 📊 Ortalama Etkileşim")
            
            tweet_count = len(tweets)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("❤️ Ort. Beğeni", f"{total_likes/tweet_count:.1f}")
            with col2:
                st.metric("🔄 Ort. RT", f"{total_retweets/tweet_count:.1f}")
            with col3:
                st.metric("💬 Ort. Quote", f"{total_quotes/tweet_count:.1f}")
            with col4:
                # Genel skor (basit formül)
                score = (total_likes + total_retweets*2 + total_quotes*3) / tweet_count
                st.metric("⭐ Genel Skor", f"{score:.1f}")
        else:
            st.info("Tweet verisi yok. Yukarıdaki butona tıklayarak güncelle.")
    else:
        st.info("Profil verilerini görmek için 'İstatistikleri Güncelle' butonuna tıkla.")
        
        # Demo veriler
        st.markdown("---")
        st.markdown("### 📋 Demo Veriler")
        
        demo_col1, demo_col2, demo_col3, demo_col4 = st.columns(4)
        with demo_col1:
            st.metric("👥 Takipçi", "12,345")
        with demo_col2:
            st.metric("➡️ Takip", "567")
        with demo_col3:
            st.metric("📝 Tweet", "4,321")
        with demo_col4:
            st.metric("📈 Oran", "21.77")

# ============================================
# TAB 5: DOKÜMANTASYON
# ============================================
with tab5:
    st.markdown("## 📖 Kullanım Kılavuzu")
    st.markdown("X Viral İçerik Üretici uygulamasının tüm özelliklerini öğren.")
    
    # Quick Start
    with st.expander("🚀 Hızlı Başlangıç", expanded=True):
        st.markdown("""
        ### 5 Adımda Viral İçerik Üret
        
        1. **Persona Tab'ına Git** → Kendi tarzını tanımla veya mevcut persona'yı kullan
        2. **Gündem Tab'ına Bak** → Bugün trend olan konuları incele
        3. **İçerik Üret Tab'ına Geç** → Bir konu seç veya manuel gir
        4. **"Thread Fikirleri Üret" Butonuna Tıkla** → AI 5 farklı thread üretecek
        5. **Beğendiğin Thread'leri Kaydet** → 👍 butonu ile feedback ver, sistem öğrensin
        
        > 💡 **İpucu:** Ne kadar çok feedback verirsen, AI o kadar senin tarzına uyum sağlar!
        """)
    
    # Persona Guide
    with st.expander("🎭 Persona Yönetimi"):
        st.markdown("""
        ### Persona Nedir?
        
        Persona, AI'ın içerik üretirken kullanacağı "karakter" tanımıdır. İyi bir persona:
        
        - **Tarz tanımlar:** Mizahi mi, ciddi mi, provokatif mi?
        - **Konu odağı belirtir:** Ekonomi, teknoloji, spor...
        - **Örnek tweet'ler içerir:** AI'ın taklit edeceği örnekler
        
        ### İyi Persona Yazma İpuçları
        
        | ✅ Yapılmalı | ❌ Yapılmamalı |
        |-------------|---------------|
        | Spesifik olmak | Çok genel olmak |
        | Örnek tweet'ler eklemek | Sadece sıfatlar yazmak |
        | Kısıtlamalar belirtmek | Her şeyi serbest bırakmak |
        | Emoji kullanımını tanımlamak | Stil hakkında bilgi vermemek |
        
        ### Örnek Persona Şablonları
        
        **Ekonomi Odaklı:**
        ```
        Sen bir borsa analisti gibi düşün. Dolar/TL, BIST100, altın hakkında 
        mizahi ama bilgilendirici içerikler üret. Teknik terimler kullan ama 
        herkesin anlayacağı şekilde açıkla.
        ```
        
        **Mizah Odaklı:**
        ```
        Zaytung/Bobiler tarzında satirik içerikler üret. Gündemdeki olayları 
        abartarak ele al, ironi kullan. Her tweet'in sonunda şaşırtıcı bir 
        twist olsun.
        ```
        """)
    
    # Content Generation Guide
    with st.expander("✍️ İçerik Üretme"):
        st.markdown("""
        ### Thread Yapısı
        
        Her üretilen thread şunları içerir:
        
        1. **Hook Tweet (1/X):** Dikkat çekici açılış
        2. **Gelişme Tweetleri (2-6/X):** Ana içerik
        3. **Kapanış Tweet'i (X/X):** Soru veya call-to-action
        
        ### Viral Potansiyeli Artırma
        
        - 🎯 **Konu seçimi önemli:** Trend olan konular daha çok görünür
        - ❓ **Soru sor:** "Siz ne düşünüyorsunuz?" gibi sorular etkileşim artırır
        - 🔥 **Provokatif ol:** Ama saygı sınırlarını aşma
        - ⏰ **Timing:** Sabah 08-10 ve akşam 19-22 arası en iyi saatler
        
        ### Karakter Limiti
        
        Her tweet maksimum **280 karakter** olabilir. Uygulama otomatik olarak:
        - Karakter sayısını gösterir
        - Limite uyanları yeşil, aşanları kırmızı gösterir
        - Uzun tweet'leri kırpar
        """)
    
    # Feedback System
    with st.expander("📚 Öğrenme Sistemi"):
        st.markdown("""
        ### Feedback Nasıl Çalışır?
        
        1. Thread ürettikten sonra her thread için 👍 veya 👎 butonları görünür
        2. 👍 **Beğendim:** Thread `learned_examples.json` dosyasına kaydedilir
        3. 👎 **Beğenmedim:** Negatif örnek olarak kaydedilir
        
        ### Öğrenme Etkisi
        
        - Beğendiğin thread'ler sonraki üretimlerde "örnek" olarak kullanılır
        - AI zamanla senin tarzını öğrenir
        - En son 3 beğenilen thread prompt'a eklenir
        
        ### Veri Temizleme
        
        `learned_examples.json` dosyasını silerek öğrenmeyi sıfırlayabilirsin:
        ```json
        {
          "liked_threads": [],
          "disliked_threads": []
        }
        ```
        """)
    
    # API Configuration
    with st.expander("⚙️ API Yapılandırması"):
        st.markdown("""
        ### Gerekli API'ler
        
        | API | Amaç | Ücretsiz Mi? |
        |-----|------|-------------|
        | **Gemini** | İçerik üretimi | ✅ Evet |
        | **X (Twitter)** | Profil/Tweet çekme | ⚠️ Kısıtlı |
        
        ### .env Dosyası
        
        Proje klasöründe `.env` dosyası oluştur:
        
        ```env
        GEMINI_API_KEY=your_gemini_api_key
        
        X_BEARER_TOKEN=your_bearer_token
        X_CONSUMER_KEY=your_consumer_key
        X_CONSUMER_SECRET=your_consumer_secret
        X_ACCESS_TOKEN=your_access_token
        X_ACCESS_TOKEN_SECRET=your_access_token_secret
        ```
        
        ### API Anahtarı Alma
        
        - **Gemini:** [Google AI Studio](https://aistudio.google.com/)
        - **X API:** [Twitter Developer Portal](https://developer.twitter.com/)
        
        > ⚠️ **Not:** X API Free tier'da bazı özellikler (trending topics) kısıtlıdır.
        """)
    
    # Tips & Tricks
    with st.expander("💡 İpuçları & Püf Noktaları"):
        st.markdown("""
        ### Viral Thread Formülleri
        
        **1. Listicle Format:**
        ```
        🧵 X konusunda 7 şey öğrendim (thread)
        
        1/7: [Şok edici bilgi]
        2/7: [Detay]
        ...
        7/7: Siz hangisini bilmiyordunuz?
        ```
        
        **2. Story Format:**
        ```
        🧵 Bugün başıma inanılmaz bir şey geldi...
        
        (hikayeyi anlat)
        
        Son: Ve işte bu yüzden [ders]
        ```
        
        **3. Hot Take Format:**
        ```
        🔥 Unpopular opinion: [Kontroversiyel görüş]
        
        Açıklama...
        
        Katılıyor musunuz?
        ```
        
        ### Kaçınılması Gerekenler
        
        - ❌ Çok uzun thread'ler (8+ tweet)
        - ❌ Hashtag spam
        - ❌ Sadece link paylaşımı
        - ❌ Konu dışına çıkmak
        - ❌ Aynı kelimeyi tekrarlamak
        
        ### En İyi Pratikler
        
        - ✅ Her tweet bağımsız okunabilir olsun
        - ✅ Görsel ekle (thread'i zenginleştir)
        - ✅ İlk tweet en önemli (hook)
        - ✅ Son tweet'te etkileşim iste
        """)
    
    # FAQ
    with st.expander("❓ Sık Sorulan Sorular"):
        st.markdown("""
        ### S: Neden trending topics gerçek değil?
        
        **C:** X API Free tier'da trending endpoint'i mevcut değil. Örnek gündem 
        konuları gösteriyoruz. Basic/Pro tier alarak gerçek trendleri görebilirsin.
        
        ---
        
        ### S: Üretilen içerikler neden bazen mantıksız?
        
        **C:** AI bazen "hallucinate" edebilir. Persona'nı daha detaylı tanımlayarak 
        ve daha çok feedback vererek bunu azaltabilirsin.
        
        ---
        
        ### S: Kaç thread üretebilirim?
        
        **C:** Gemini API'nin günlük limitleri var ama ücretsiz tier için oldukça 
        yüksek (dakikada 15 istek). Normal kullanımda limit sorun olmaz.
        
        ---
        
        ### S: X hesabımı değiştirebilir miyim?
        
        **C:** Evet, `app.py` dosyasında `"bir_adamiste"` yazan yerleri kendi 
        kullanıcı adınla değiştir.
        
        ---
        
        ### S: Üretilen içerikleri otomatik paylaşabilir miyim?
        
        **C:** Hayır, bu özellik bilerek eklenmedi. İçerikleri inceleyip 
        düzenledikten sonra manuel paylaşman önerilir.
        """)
    
    # Keyboard Shortcuts
    with st.expander("⌨️ Kısayollar"):
        st.markdown("""
        ### Streamlit Kısayolları
        
        | Kısayol | İşlev |
        |---------|-------|
        | `R` | Sayfayı yenile |
        | `C` | Önbelleği temizle |
        | `Ctrl + F` | Sayfada ara |
        
        ### Tavsiye Edilen Workflow
        
        1. Sabah: Gündem tab'ını kontrol et
        2. Öğle: 2-3 thread üret, beğendiklerini kaydet
        3. Akşam: En iyi thread'i düzenle ve paylaş
        4. Gece: Feedback ver, sistemi geliştir
        """)
    
    # Version Info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <strong>X Viral İçerik Üretici v1.1</strong><br>
        Gemini 3 Flash • Türkçe Optimize • Feedback Learning
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    🐦 X Viral İçerik Üretici | Yerel: http://localhost:8501 | 
    <a href="https://twitter.com/bir_adamiste" target="_blank">@bir_adamiste</a>
</div>
""", unsafe_allow_html=True)
