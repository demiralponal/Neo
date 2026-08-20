import random
import google.generativeai as genai
import resend
import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="Neo AI", page_icon="⚡", layout="centered")

# Modern Renkli Tema (Neon / Gradient CSS)
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
    }
    h1, h2, h3 {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
    }
    .stTextInput input {
        background-color: rgba(30, 41, 59, 0.7) !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# API Yapılandırmaları
resend.api_key = st.secrets.get("RESEND_API_KEY", "")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

# Oturum Durumları
if "dogrulama_kodu" not in st.session_state:
    st.session_state.dogrulama_kodu = None
if "giris_basarili" not in st.session_state:
    st.session_state.giris_basarili = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AŞAMA 1: GİRİŞ EKRANI ---
if not st.session_state.giris_basarili:
    st.title("⚡ Neo AI")
    st.write("Sisteme giriş yapmak için e-posta adresinizi girin.")

    eposta = st.text_input(
        "E-posta Adresiniz:", placeholder="ornek@gmail.com"
    )

    if st.button("Doğrulama Kodu Gönder"):
        if eposta:
            kod = str(random.randint(100000, 999999))
            st.session_state.dogrulama_kodu = kod

            # Eklediğin HTML Tasarımının E-Posta Entegre Hali
            html_content = f"""
            <!DOCTYPE html>
            <html lang="tr">
            <head>
              <meta charset="UTF-8">
            </head>
            <body style="background-color: #fcf9f2; color: #2d3748; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px;">
              <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 500px; background-color: #fcf9f2; border-collapse: collapse;">
                <tr>
                  <td style="padding: 10px;">
                    
                    <!-- Banner -->
                    <div style="background-color: #2cb67d; color: #ffffff; padding: 35px 20px; border-radius: 15px; text-align: center;">
                      <h1 style="font-family: 'Georgia', serif; font-size: 32px; margin: 0 0 5px 0;">Neo'ya hoşgeldiniz</h1>
                      <p style="margin: 0; font-size: 16px; opacity: 0.9;">Türkiye'nin yeni yapay zekası</p>
                    </div>

                    <!-- Alt Başlık -->
                    <h2 style="font-family: 'Georgia', serif; color: #2cb67d; font-size: 22px; margin-top: 25px; text-align: center;">
                      Giriş Doğrulama Kodunuz
                    </h2>

                    <!-- Form / Kod Kutusu -->
                    <div style="background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 30px 20px; margin-top: 15px; text-align: center;">
                      <h3 style="font-family: 'Impact', 'Arial Black', sans-serif; font-size: 26px; text-transform: uppercase; color: #000000; margin: 0 0 15px 0;">
                        NEO DOĞRULAMA KODU
                      </h3>
                      
                      <div style="background-color: #2cb67d; color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 8px; padding: 15px 25px; border-radius: 10px; display: inline-block; margin: 10px 0;">
                        {kod}
                      </div>

                      <p style="font-size: 13px; color: #718096; margin-top: 20px; margin-bottom: 0;">
                        Bu kodu kimseyle paylaşmayın. Bu e-posta otomatiktir, lütfen yanıtlamayınız.
                      </p>
                    </div>

                    <!-- Footer -->
                    <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #a0aec0;">
                      <p style="margin: 0;">© Neo AI - Tüm hakları saklıdır.</p>
                    </div>

                  </td>
                </tr>
              </table>
            </body>
            </html>
            """

            try:
                resend.Emails.send(
                    {
                        "from": "Neo AI <onboarding@resend.dev>",
                        "to": eposta,
                        "subject": "Neo AI - Giriş Doğrulama Kodunuz",
                        "html": html_content,
                    }
                )
                st.success(
                    "Doğrulama kodu yeni şablonla e-postanıza gönderildi!"
                )
            except Exception as e:
                st.error(f"E-posta Gönderim Hatası: {e}")
        else:
            st.warning("Lütfen e-posta adresinizi girin.")

    if st.session_state.dogrulama_kodu:
        st.divider()
        girilen_kod = st.text_input("6 Haneli Kodu Girin:", type="password")
        if st.button("Giriş Yap"):
            if girilen_kod == st.session_state.dogrulama_kodu:
                st.session_state.giris_basarili = True
                st.rerun()
            else:
                st.error("Hatalı kod!")

# --- AŞAMA 2: NEO AI SOHBET EKRANI ---
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
                    st.error(f"Yanıt oluşturulurken hata oluştu: {e}")
