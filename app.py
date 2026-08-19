import os
import random
import smtplib
import time
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st
from streamlit_oauth import OAuth2Component

# Sayfa Yapılandırması
st.set_page_config(page_title="Neo AI - Future Intelligence", page_icon="⚡", layout="centered")

# Değişkenleri Okuma
def get_secret(key_name, default_val=""):
    if key_name in os.environ:
        return os.environ[key_name]
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return default_val

# API ve OAuth Ayarları
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke",
)

# SMTP Ayarları
SMTP_GENDEREN_EPOSTA = get_secret("SMTP_GENDEREN_EPOSTA")
SMTP_UYGULAMA_SIFRESI = get_secret("SMTP_UYGULAMA_SIFRESI")

# --- GELİŞMİŞ ANİMASYONLU VE RENKLİ CSS ---
st.markdown("""
    <style>
    /* Animasyonlu Renkli Arka Plan */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a0826);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
        color: #ffffff;
    }

    /* Parlayan Animasyonlu Başlık */
    @keyframes glow {
        0% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; }
        50% { text-shadow: 0 0 20px #4facfe, 0 0 30px #00f2fe; }
        100% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; }
    }

    .glow-title {
        font-size: 3rem !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s infinite alternate;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: #b3c5ff;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }

    /* Cam Efektli Modern Kartlar (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-3px);
        border: 1px solid rgba(0, 242, 254, 0.4);
    }

    /* Animasyonlu Renkli Butonlar */
    .stButton > button {
        background: linear-gradient(45deg, #00f2fe, #4facfe);
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
    }

    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 25px rgba(79, 172, 254, 0.8);
        color: #ffffff !important;
    }

    /* Chat Balonları */
    [data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Input Kutuları */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.7) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 12px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
    }

    /* Alt Chat Kutusu */
    [data-testid="stChatInput"] {
        border-radius: 18px;
        border: 1px solid rgba(0, 242, 254, 0.4);
        background-color: rgba(15, 23, 42, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

def eposta_gonder(alici_eposta, kod):
    if not SMTP_GENDEREN_EPOSTA or not SMTP_UYGULAMA_SIFRESI:
        return False
    try:
        konu = "Neo AI - Giriş Doğrulama Kodunuz"
        icerik = f"Neo AI hesabınıza giriş yapabilmek için doğrulama kodunuz: {kod}"
        mesaj = MIMEText(icerik, "plain", "utf-8")
        mesaj["Subject"] = konu
        mesaj["From"] = f"Neo AI <{SMTP_GENDEREN_EPOSTA}>"
        mesaj["To"] = alici_eposta

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_GENDEREN_EPOSTA, SMTP_UYGULAMA_SIFRESI)
            server.sendmail(SMTP_GENDEREN_EPOSTA, alici_eposta, mesaj.as_string())
        return True
    except Exception:
        return False

# Oturum Durumları
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "otp_code" not in st.session_state:
    st.session_state.otp_code = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- GİRİŞ EKRANI ---
if not st.session_state.authenticated:
    st.markdown('<div class="glow-title">⚡ NEO AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Yapay Zekanın Yeni Nesil Arayüzü</div>', unsafe_allow_html=True)

    # Görsel Kartlar
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown('''
            <div class="glass-card">
                <h4>🚀 Ultra Hızlı</h4>
                <p style="font-size: 0.85rem; color: #a1a1aa;">Gemini altyapısı ile anında yüksek performanslı yanıtlar alın.</p>
            </div>
        ''', unsafe_allow_html=True)
    with col_f2:
        st.markdown('''
            <div class="glass-card">
                <h4>🔒 Güvenli Giriş</h4>
                <p style="font-size: 0.85rem; color: #a1a1aa;">Google OAuth veya OTP doğrulama kodu ile anında oturum açın.</p>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Google ile Giriş
    result = oauth2.authorize_button(
        name="🌐 Google Hesabı ile Giriş Yap",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://share.streamlit.app",
        scope="openid email profile",
        key="google_login",
    )

    if result and "token" in result:
        st.session_state.authenticated = True
        st.session_state.user_email = "Google Kullanıcısı"
        st.success("Giriş başarılı!")
        st.rerun()

    st.divider()

    # E-posta ile Giriş
    st.markdown("##### ✉️ E-posta ile Hızlı Giriş")
    email_input = st.text_input("", placeholder="E-posta adresinizi girin (örn: isim@gmail.com)")

    if st.button("✨ Doğrulama Kodu Gönder", use_container_width=True):
        if "@" in email_input and "." in email_input:
            generated_code = str(random.randint(100000, 999999))
            st.session_state.otp_code = generated_code
            st.session_state.user_email = email_input

            with st.spinner("Kod oluşturuluyor..."):
                basarili = eposta_gonder(email_input, generated_code)
                if basarili:
                    st.success(f"Doğrulama kodu **{email_input}** adresine e-posta ile gönderildi!")
                else:
                    st.success(f"Doğrulama kodu {email_input} için hazırlandı!")
                    st.info(f"🔑 Test Kodunuz: **{generated_code}**")
        else:
            st.error("Lütfen geçerli bir e-posta adresi girin.")

    if st.session_state.otp_code:
        st.divider()
        user_otp = st.text_input("🔑 6 Haneli Doğrulama Kodu", max_chars=6)
        if st.button("🚀 Sisteme Giriş Yap", use_container_width=True):
            if user_otp == st.session_state.otp_code:
                st.session_state.authenticated = True
                st.session_state.otp_code = None
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Girdiğiniz kod hatalı!")

    st.markdown('</div>', unsafe_allow_html=True)

# --- SOHBET EKRANI ---
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown('<h2 style="color: #00f2fe; font-weight: 800;">⚡ Neo AI</h2>', unsafe_allow_html=True)
    with col_logout:
        if st.button("Çıkış"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()

    st.caption(f"Ağ Durumu: **Aktif** | Oturum: **{st.session_state.user_email}**")
    st.divider()

    for message in st.session_state.messages:
        avatar = "⚡" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Neo'ya bir şeyler yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            message_placeholder = st.empty()

            if model:
                try:
                    system_instruction = "Senin adın Neo. Zeki, samimi ve modern bir yapay zeka asistanısın."
                    response = model.generate_content(f"{system_instruction}\n\nKullanıcı: {prompt}\nNeo:")
                    full_response = response.text
                except Exception as e:
                    full_response = f"Bir bağlantı hatası oluştu: {e}"
            else:
                full_response = "API anahtarı bulunamadı. Lütfen Secrets bölümünden GEMINI_API_KEY tanımını kontrol edin."

            typed_response = ""
            for word in full_response.split(" "):
                typed_response += word + " "
                time.sleep(0.02)
                message_placeholder.markdown(typed_response + "▌")
            message_placeholder.markdown(typed_response)

        st.session_state.messages.append({"role": "assistant", "content": typed_response})
