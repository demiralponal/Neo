import streamlit as st
import random
import time
import smtplib
from email.mime.text import MIMEText
import google.generativeai as genai
from streamlit_oauth import OAuth2Component

# Sayfa Yapılandırması
st.set_page_config(page_title="Neo AI", page_icon="🤖", layout="centered")

# --- GÜVENLİ KASA (SECRETS) İLE API AYARLARI ---
# Tüm gizli bilgiler st.secrets üzerinden okunur
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    model = None

# Google OAuth Bilgileri
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")

# OAuth Bileşeni Kurulumu
oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID, 
    GOOGLE_CLIENT_SECRET, 
    "https://accounts.google.com/o/oauth2/v2/auth", 
    "https://oauth2.googleapis.com/token", 
    "https://oauth2.googleapis.com/token", 
    "https://oauth2.googleapis.com/revoke"
)

# E-posta Gönderme Fonksiyonu (SMTP)
SMTP_GENDEREN_EPOSTA = st.secrets.get("SMTP_GENDEREN_EPOSTA", "")
SMTP_UYGULAMA_SIFRESI = st.secrets.get("SMTP_UYGULAMA_SIFRESI", "")

def eposta_gonder(alici_eposta, kod):
    if not SMTP_GENDEREN_EPOSTA or not SMTP_UYGULAMA_SIFRESI:
        return False
    try:
        konu = "Neo AI - Giriş Doğrulama Kodunuz"
        icerik = f"Neo AI hesabınıza giriş yapabilmek için doğrulama kodunuz: {kod}"
        mesaj = MIMEText(icerik, 'plain', 'utf-8')
        mesaj['Subject'] = konu
        mesaj['From'] = f"Neo AI <{SMTP_GENDEREN_EPOSTA}>"
        mesaj['To'] = alici_eposta

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_GENDEREN_EPOSTA, SMTP_UYGULAMA_SIFRESI)
            server.sendmail(SMTP_GENDEREN_EPOSTA, alici_eposta, mesaj.as_string())
        return True
    except Exception:
        return False

# Oturum Durumları (Session State)
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
    st.title("🤖 Neo AI'ya Hoş Geldin")
    st.write("Devam etmek için giriş yapın")

    # 1. Google ile Giriş
    result = oauth2.authorize_button(
        name="🌐 Google ile Giriş Yap",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://share.streamlit.app",
        scope="openid email profile",
        key="google_login",
    )

    if result and "token" in result:
        st.session_state.authenticated = True
        st.session_state.user_email = "Google Hesabı"
        st.success("Google ile giriş başarılı!")
        st.rerun()

    st.divider()

    # 2. E-posta ile Giriş (OTP)
    st.subheader("E-posta ile Giriş")
    email_input = st.text_input("E-posta Adresiniz", placeholder="ornek@gmail.com")

    if st.button("Doğrulama Kodu Gönder", use_container_width=True):
        if "@" in email_input and "." in email_input:
            generated_code = str(random.randint(100000, 999999))
            st.session_state.otp_code = generated_code
            st.session_state.user_email = email_input
            
            with st.spinner("Kod oluşturuluyor..."):
                basarili = eposta_gonder(email_input, generated_code)
                if basarili:
                    st.success(f"Doğrulama kodu **{email_input}** adresine e-posta ile gönderildi!")
                else:
                    st.success(f"Doğrulama kodu {email_input} için oluşturuldu!")
                    st.info(f"🔑 Test Doğrulama Kodunuz: **{generated_code}**")
        else:
            st.error("Lütfen geçerli bir e-posta adresi girin.")

    if st.session_state.otp_code:
        st.divider()
        user_otp = st.text_input("6 Haneli Doğrulama Kodu", max_chars=6)
        if st.button("Giriş Yap", use_container_width=True):
            if user_otp == st.session_state.otp_code:
                st.session_state.authenticated = True
                st.session_state.otp_code = None
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Kod hatalı!")

# --- NEO AI SOHBET EKRANI ---
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.title("🤖 Neo AI")
    with col_logout:
        if st.button("Çıkış Yap"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()

    st.caption(f"Aktif Oturum: **{st.session_state.user_email}**")
    st.divider()

    # Sohbet Geçmişini Göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcı Mesajı Al ve Yanıtla
    if prompt := st.chat_input("Neo'ya bir şey sor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            if model:
                try:
                    system_instruction = "Senin adın Neo. Yardımsever, zeki, hızlı ve samimi bir yapay zeka asistanısın."
                    response = model.generate_content(f"{system_instruction}\n\nKullanıcı: {prompt}\nNeo:")
                    full_response = response.text
                except Exception as e:
                    full_response = f"Bağlantı hatası oluştu: {e}"
            else:
                full_response = "Gemini API anahtarı Streamlit Secrets alanına henüz eklenmedi."

            typed_response = ""
            for word in full_response.split(" "):
                typed_response += word + " "
                time.sleep(0.02)
                message_placeholder.markdown(typed_response + "▌")
            message_placeholder.markdown(typed_response)

        st.session_state.messages.append({"role": "assistant", "content": typed_response})
