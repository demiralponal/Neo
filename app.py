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
        box-shadow: 0 4px 14px 0 rgba(168, 85, 247, 0.39) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(168, 85, 247, 0.6) !important;
    }
    .stTextInput input {
        background-color: rgba(30, 41, 59, 0.7) !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 10px rgba(129, 140, 248, 0.5) !important;
    }
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin-bottom: 10px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# API Yapılandırmaları
resend.api_key = st.secrets.get("RESEND_API_KEY", "")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Güncellenmiş Model Yolu
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    st.error("GEMINI_API_KEY Secrets kutusunda bulunamadı!")

# Oturum Durumları
if "dogrulama_kodu" not in st.session_state:
    st.session_state.dogrulama_kodu = None
if "giris_basarili" not in st.session_state:
    st.session_state.giris_basarili = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AŞAMA 1: E-POSTA DOĞRULAMA GİRİŞ EKRANI ---
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

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body style="margin:0; padding:0; background-color:#f4f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 20px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                    
                    <div style="background: linear-gradient(135deg, #ff3385 0%, #ff8833 50%, #ffcc00 100%); padding: 40px 20px; text-align: center; color: #ffffff;">
                        <h1 style="font-size: 32px; font-weight: 700; margin: 0 0 10px 0; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            Neo-e posta<br>doğrulama<br>kodunuz
                        </h1>
                        <p style="font-size: 13px; margin: 15px 0 0 0; opacity: 0.9; font-weight: 400;">
                            Bu kodu hiç kimseyle paylaşmamakla birlikte bu E postaya yanıt vermeyin
                        </p>
                    </div>

                    <div style="padding: 30px 20px; text-align: center;">
                        <p style="font-style: italic; font-weight: bold; font-family: monospace; font-size: 16px; color: #333333; margin-bottom: 15px;">
                            Doğrulama kodu
                        </p>
                        
                        <div style="background: linear-gradient(90deg, #ff7733, #ff3385); color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 8px; padding: 15px 30px; border-radius: 50px; display: inline-block; box-shadow: 0 4px 15px rgba(255, 51, 133, 0.3);">
                            {kod}
                        </div>

                        <table style="width: 100%; margin-top: 30px; border-spacing: 8px;">
                            <tr>
                                <td style="background-color: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 15px 5px; text-align: center; font-size: 12px; color: #333333;">
                                    Hatasız ve sınırsız∞
                                </td>
                                <td style="background-color: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 15px 5px; text-align: center; font-size: 12px; color: #333333;">
                                    Çevre dostu🌿
                                </td>
                                <td style="background-color: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 15px 5px; text-align: center; font-size: 12px; color: #333333;">
                                    Hızlı ve güvenli🔒
                                </td>
                            </tr>
                        </table>

                        <div style="margin-top: 25px;">
                            <span style="background: linear-gradient(90deg, #ff8833, #ff3385); color: #ffffff; font-weight: bold; padding: 10px 40px; border-radius: 20px; font-size: 14px;">
                                Neo
                            </span>
                        </div>
                    </div>

                    <div style="border-top: 1px solid #ffaa66; padding: 20px; text-align: center; font-size: 11px; color: #555555; background-color: #fafafa;">
                        <p style="margin: 0 0 5px 0;">Bu E posta Neo yeni nesil yapay zeka tarafından gönderilmiştir</p>
                        <p style="margin: 0 0 5px 0;">Tüm hakları saklıdır</p>
                        <p style="margin: 0; font-weight: bold;">© Neo</p>
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
                        "subject": "Neo - E-posta Doğrulama Kodunuz",
                        "html": html_content,
                    }
                )
                st.success("Doğrulama kodu e-postanıza gönderildi!")
            except Exception as e:
                st.error(f"E-posta Gönderim Hatası: {e}")
        else:
            st.warning("Lütfen geçerli bir e-posta adresi girin.")

    if st.session_state.dogrulama_kodu:
        st.divider()
        girilen_kod = st.text_input(
            "E-postanıza gelen 6 haneli kodu girin:", type="password"
        )
        if st.button("Giriş Yap"):
            if girilen_kod == st.session_state.dogrulama_kodu:
                st.session_state.giris_basarili = True
                st.rerun()
            else:
                st.error("Hatalı kod! Lütfen tekrar kontrol edin.")

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
