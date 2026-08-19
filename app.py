import os
import random
import smtplib
import time
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st
from streamlit_oauth import OAuth2Component

# Sayfa Yapılandırması
st.set_page_config(page_title="Neo AI", page_icon="🤖", layout="centered")

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

# Custom CSS - Modern Koyu Tema
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        color: #c9d1d9;
    }
    h1 {
        background: linear-gradient(90deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(22, 27, 34, 0.8);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stTextInput > div > div > input {
        background-color: #0d1117;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    [data-testid="stChatInput"] {
        border-radius: 14px;
        border: 1px solid #30363d;
        background-color: #161b22;
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

# Giriş Ekranı
if not st.session_state.authenticated:
    st.title("🤖 Neo AI")
    st.markdown("##### Geleceğin Yapay Zeka Deneyimine Hoş Geldiniz")
    st.divider()

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

    st.subheader("E-posta ile Hızlı Giriş")
    email_input = st.text_input("E-posta Adresiniz", placeholder="ornek@gmail.com")

    if st.button("Doğrulama Kodu Gönder", use_container_width=True):
        if "@" in email_input and "." in email_input:
            generated_code = str(random.randint(100000, 999999))
            st.session_state.otp_code = generated_code
            st.session_state.user_email = email_input

            with st.spinner("Kod iletiliyor..."):
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
        user_otp = st.text_input("6 Haneli Doğrulama Kodu", max_chars=6)
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if user_otp == st.session_state.otp_code:
                st.session_state.authenticated = True
                st.session_state.otp_code = None
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Girdiğiniz kod hatalı!")

# Sohbet Ekranı
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.title("🤖 Neo AI")
    with col_logout:
        if st.button("Çıkış Yap"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()

    st.caption(f"Aktif Kullanıcı: **{st.session_state.user_email}**")
    st.divider()

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Neo'ya bir soru sorun..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
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
