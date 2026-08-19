import os
import random
import smtplib
import time
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st
from streamlit_oauth import OAuth2Component

# Sayfa Yapılandırması
st.set_page_config(page_title="Neo", page_icon="💬", layout="centered")


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

# --- SADE VE PREMİUM CSS (DARK MODE) ---
st.markdown(
    """
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #0e1117;
        color: #e6e9ef;
    }
    
    /* Konteyner ve Kart Yapısı */
    .auth-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        margin-top: 10px;
    }
    
    /* Butonlar */
    .stButton > button {
        background-color: #238636;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 16px;
        transition: background-color 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
        color: #ffffff;
    }

    /* Input Alanları */
    .stTextInput > div > div > input {
        background-color: #0d1117;
        color: #f0f6fc;
        border: 1px solid #30363d;
        border-radius: 8px;
    }

    /* Chat Balonları */
    [data-testid="stChatMessage"] {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 12px 16px;
    }
    
    /* Chat Input Alt Kısım */
    [data-testid="stChatInput"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def eposta_gonder(alici_eposta, kod):
  if not SMTP_GENDEREN_EPOSTA or not SMTP_UYGULAMA_SIFRESI:
    return False
  try:
    konu = "Neo - Giriş Kodunuz"
    icerik = f"Neo hesabınıza giriş yapmak için doğrulama kodunuz: {kod}"
    mesaj = MIMEText(icerik, "plain", "utf-8")
    mesaj["Subject"] = konu
    mesaj["From"] = f"Neo <{SMTP_GENDEREN_EPOSTA}>"
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
  st.title("Neo")
  st.caption("Yapay Zeka Asistanı")

  # Google ile Giriş
  result = oauth2.authorize_button(
      name="Google ile Giriş Yap",
      icon="https://www.google.com/favicon.ico",
      redirect_uri="https://share.streamlit.app",
      scope="openid email profile",
      key="google_login",
  )

  if result and "token" in result:
    st.session_state.authenticated = True
    st.session_state.user_email = "Google Kullanıcısı"
    st.success("Giriş yapıldı.")
    st.rerun()

  st.divider()

  # E-posta ile Giriş
  st.subheader("E-posta ile Oturum Aç")
  email_input = st.text_input(
      "E-posta Adresi", placeholder="ornek@domain.com", label_visibility="collapsed"
  )

  if st.button("Doğrulama Kodu Gönder", use_container_width=True):
    if "@" in email_input and "." in email_input:
      generated_code = str(random.randint(100000, 999999))
      st.session_state.otp_code = generated_code
      st.session_state.user_email = email_input

      with st.spinner("Kod gönderiliyor..."):
        basarili = eposta_gonder(email_input, generated_code)
        if basarili:
          st.success(f"Kod **{email_input}** adresine gönderildi.")
        else:
          st.info(f"Kod oluşturuldu. Test Kodunuz: **{generated_code}**")
    else:
      st.error("Lütfen geçerli bir e-posta adresi girin.")

  if st.session_state.otp_code:
    st.write("")
    user_otp = st.text_input(
        "Doğrulama Kodu",
        max_chars=6,
        placeholder="6 haneli kod",
        label_visibility="collapsed",
    )
    if st.button("Giriş Yap", use_container_width=True):
      if user_otp == st.session_state.otp_code:
        st.session_state.authenticated = True
        st.session_state.otp_code = None
        st.rerun()
      else:
        st.error("Kod hatalı.")

# --- SOHBET EKRANI ---
else:
  col_title, col_logout = st.columns([5, 1])
  with col_title:
    st.title("Neo")
  with col_logout:
    if st.button("Çıkış"):
      st.session_state.authenticated = False
      st.session_state.messages = []
      st.rerun()

  st.caption(f"Oturum: {st.session_state.user_email}")
  st.divider()

  for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
      st.markdown(message["content"])

  if prompt := st.chat_input("Bir mesaj yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
      st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
      message_placeholder = st.empty()

      if model:
        try:
          system_instruction = (
              "Senin adın Neo. Yardımsever, net ve zeki bir yapay zeka"
              " asistanısın."
          )
          response = model.generate_content(
              f"{system_instruction}\n\nKullanıcı: {prompt}\nNeo:"
          )
          full_response = response.text
        except Exception as e:
          full_response = f"Hata oluştu: {e}"
      else:
        full_response = (
            "API anahtarı eksik. Lütfen GEMINI_API_KEY tanımını kontrol edin."
        )

      typed_response = ""
      for word in full_response.split(" "):
        typed_response += word + " "
        time.sleep(0.02)
        message_placeholder.markdown(typed_response + "▌")
      message_placeholder.markdown(typed_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": typed_response}
    )
