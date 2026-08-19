import os
import random
import smtplib
import time
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st
from streamlit_oauth import OAuth2Component

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Neo AI - Akıllı Asistan", page_icon="🤖", layout="centered"
)


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

# --- ÖZEL MODERN TASARIM VE RENK PALETİ ---
st.markdown(
    """
    <style>
    /* Ana Arka Plan - Derin Lacivert & Koyu Gri */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
    }
    
    /* Kapak / Başlık Bölümü */
    .hero-container {
        text-align: center;
        padding: 30px 10px 10px 10px;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }

    /* Bilgi Kartları (Giriş Ekranı Doldurma) */
    .feature-card {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 15px;
    }
    .feature-card h4 {
        color: #38bdf8;
        margin-bottom: 5px;
        font-size: 1rem;
    }
    .feature-card p {
        color: #94a3b8;
        font-size: 0.85rem;
        margin: 0;
    }

    /* Buton Tasarımı */
    .stButton > button {
        background: linear-gradient(90deg, #0284c7 0%, #2563eb 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0369a1 0%, #1d4ed8 100%);
        color: #ffffff;
    }

    /* Input Alanları */
    .stTextInput > div > div > input {
        background-color: #0f172a;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    /* Chat Balonları */
    [data-testid="stChatMessage"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 12px 18px;
    }

    /* Sayfa Alt Bilgisi (Footer) */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #334155;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def eposta_gonder(alici_eposta, kod):
  if not SMTP_GENDEREN_EPOSTA or not SMTP_UYGULAMA_SIFRESI:
    return False
  try:
    konu = "Neo AI - Oturum Doğrulama Kodu"
    icerik = f"Neo AI sistemine giriş için kullanabileceğiniz doğrulama kodunuz: {kod}"
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
  # Kapak Başlığı
  st.markdown(
      """
      <div class="hero-container">
          <div class="hero-title">🤖 Neo AI</div>
          <div class="hero-subtitle">Yeni Nesil Akıllı Asistan Deneyimi</div>
      </div>
  """,
      unsafe_allow_html=True,
  )

  # Özellik Kartları (Ekranı Zenginleştiren Alan)
  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        """
        <div class="feature-card">
            <h4>⚡ Hızlı Yanıt</h4>
            <p>Sorularınıza anında akıllı çözümler alın.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        """
        <div class="feature-card">
            <h4>💻 Kod & Analiz</h4>
            <p>Yazılım ve içerik üretimi desteği.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🔒 Güvenli</h4>
            <p>E-posta veya Google ile doğrulama yapın.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

  st.write("")

  # Giriş Seçenekleri
  st.subheader("Giriş Yap")

  # Google ile Giriş
  result = oauth2.authorize_button(
      name="Google Hesabı ile Devam Et",
      icon="https://www.google.com/favicon.ico",
      redirect_uri="https://share.streamlit.app",
      scope="openid email profile",
      key="google_login",
  )

  if result and "token" in result:
    st.session_state.authenticated = True
    st.session_state.user_email = "Google Kullanıcısı"
    st.rerun()

  st.divider()

  # E-posta ile Giriş
  st.markdown("##### E-posta ile Doğrulama")
  email_input = st.text_input(
      "E-posta Adresi", placeholder="ornek@gmail.com", label_visibility="collapsed"
  )

  if st.button("Doğrulama Kodu Gönder", use_container_width=True):
    if "@" in email_input and "." in email_input:
      generated_code = str(random.randint(100000, 999999))
      st.session_state.otp_code = generated_code
      st.session_state.user_email = email_input

      with st.spinner("Kod iletiliyor..."):
        basarili = eposta_gonder(email_input, generated_code)
        if basarili:
          st.success(
              f"Doğrulama kodu **{email_input}** adresine e-posta ile gönderildi!"
          )
        else:
          st.info(f"🔑 Test Kodunuz: **{generated_code}**")
    else:
      st.error("Lütfen geçerli bir e-posta adresi girin.")

  if st.session_state.otp_code:
    st.write("")
    user_otp = st.text_input(
        "6 Haneli Kodu Girin",
        max_chars=6,
        placeholder="123456",
        label_visibility="collapsed",
    )
    if st.button("Giriş Yap ve Başla", use_container_width=True):
      if user_otp == st.session_state.otp_code:
        st.session_state.authenticated = True
        st.session_state.otp_code = None
        st.rerun()
      else:
        st.error("Girdiğiniz kod hatalı!")

  # Sayfa Altı Zenginleştirme (Alt Bilgiler)
  st.markdown(
      """
      <div class="footer">
          <p>Neo AI Engine v2.0 • Gemini Altyapısı ile Güçlendirilmiştir</p>
          <p>© 2026 Neo Inc. Tüm hakları saklıdır.</p>
      </div>
  """,
      unsafe_allow_html=True,
  )

# --- SOHBET EKRANI ---
else:
  col_title, col_logout = st.columns([5, 1])
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
          system_instruction = (
              "Senin adın Neo. Yardımsever, samimi ve zeki bir yapay zeka"
              " asistanısın."
          )
          response = model.generate_content(
              f"{system_instruction}\n\nKullanıcı: {prompt}\nNeo:"
          )
          full_response = response.text
        except Exception as e:
          full_response = f"Bir bağlantı hatası oluştu: {e}"
      else:
        full_response = (
            "API anahtarı bulunamadı. Lütfen Secrets bölümünden GEMINI_API_KEY"
            " tanımını kontrol edin."
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
