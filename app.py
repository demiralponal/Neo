import random
import google.generativeai as genai
import resend
import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="Neo AI", page_icon="⚡", layout="centered")

# Secrets Yapılandırmaları
RESEND_KEY = st.secrets.get("RESEND_API_KEY", "")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")

resend.api_key = RESEND_KEY

# Gemini Yapılandırması (Düzeltilen Model İsmi)
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        # 'latest' takısı kaldırıldı, doğrudan stabil model çağırılıyor
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.error(f"Gemini Başlatma Hatası: {e}")

# Session State
if "dogrulama_kodu" not in st.session_state:
    st.session_state.dogrulama_kodu = None
if "giris_basarili" not in st.session_state:
    st.session_state.giris_basarili = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AŞAMA 1: GİRİŞ EKRANI ---
if not st.session_state.giris_basarili:

    st.markdown(
        """
    <style>
      .stApp { background-color: #fcf9f2 !important; color: #2d3748 !important; }
      .hero-banner { background-color: #2cb67d; color: #ffffff; padding: 35px 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
      .hero-banner h1 { font-family: 'Georgia', serif; font-size: 32px; margin: 0; color: #ffffff !important; }
      .hero-banner p { margin: 5px 0 0 0; font-size: 16px; opacity: 0.9; }
      .action-title { font-family: 'Georgia', serif; color: #2cb67d; font-size: 22px; text-align: center; margin-bottom: 15px; }
      .form-title { font-family: 'Impact', 'Arial Black', sans-serif; font-size: 26px; text-transform: uppercase; color: #000000; text-align: center; margin-bottom: 15px; }
      .stButton>button { background-color: #2cb67d !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; width: 100%; }
      .stTextInput input { background-color: #ffffff !important; color: #2d3748 !important; border: 1px solid #e0e0e0 !important; border-radius: 8px !important; }
    </style>

    <div class="hero-banner">
      <h1>Neo'ya hoşgeldiniz</h1>
      <p>Türkiye'nin yeni yapay zekası</p>
    </div>
    <div class="action-title">Burdan kayıt ve giriş işlemlerini yapabilirsin</div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(
            '<div class="form-title">NEO KAYIT FORMU</div>',
            unsafe_allow_html=True,
        )

        eposta = st.text_input(
            "E-posta Adresiniz:", placeholder="E-posta adresinizi girin"
        )

        if st.button("Doğrulama Kodu Gönder"):
            if not RESEND_KEY:
                st.error("RESEND_API_KEY Secrets ayarlarında bulunamadı!")
            elif eposta:
                kod = str(random.randint(100000, 999999))
                st.session_state.dogrulama_kodu = kod

                html_content = f"""
                <!DOCTYPE html>
                <html lang="tr">
                <head><meta charset="UTF-8"></head>
                <body style="margin: 0; padding: 0; background-color: #f4f4f7;">
                  <div style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
                    <div style="max-width: 500px; margin: auto; background: white; padding: 30px; border-radius: 15px; text-align: center;">
                      <h2 style="color: #2cb67d; margin-top: 0;">Neo–e posta doğrulama kodunuz</h2>
                      <p style="color: #444;">Kayıt işleminizi tamamlamak için aşağıdaki 6 haneli doğrulama kodunu kullanın:</p>
                      <h1 style="font-size: 38px; letter-spacing: 6px; color: #fc4a1a; margin: 20px 0;">{kod}</h1>
                      <p style="font-size: 12px; color: #777;">Bu kodu hiç kimseyle paylaşmamakla birlikte bu E postaya yanıt vermeyin.</p>
                      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                      <p style="font-size: 11px; color: #aaa; margin-bottom: 0;">© Neo yeni nesil yapay zeka</p>
                    </div>
                  </div>
                </body>
                </html>
                """

                try:
                    resend.Emails.send(
                        {
                            "from": "Neo AI <onboarding@resend.dev>",
                            "to": eposta,
                            "subject": "Neo AI - Doğrulama Kodunuz",
                            "html": html_content,
                        }
                    )
                    st.success("Doğrulama kodu e-postanıza gönderildi!")
                except Exception as e:
                    st.error(f"E-posta Gönderim Hatası: {str(e)}")
            else:
                st.warning("Lütfen e-posta adresinizi girin.")

        if st.session_state.dogrulama_kodu:
            st.divider()
            girilen_kod = st.text_input(
                "E-postanıza Gelen Kodu Girin:", type="password"
            )
            if st.button("Giriş Yap"):
                if girilen_kod == st.session_state.dogrulama_kodu:
                    st.session_state.giris_basarili = True
                    st.rerun()
                else:
                    st.error("Hatalı kod!")

# --- AŞAMA 2: SOHBET EKRANI ---
else:
    st.title("💬 Neo AI Asistan")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Neo AI'ya bir mesaj yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Neo düşünüyor..."):
                try:
                    response = model.generate_content(prompt)
                    bot_reply = response.text
                    st.markdown(bot_reply)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": bot_reply}
                    )
                except Exception as e:
                    st.error(f"Gemini API Hatası: {e}")
