import random
import google.generativeai as genai
import resend
import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="Neo AI", page_icon="⚡", layout="centered")

# CSS Tema
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

            # Sadece E-postaya Gidecek HTML Şablonu
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="margin:0; padding:0; background-color:#f4f4f6; font-family: sans-serif;">
                <div style="max-width: 500px; margin: 20px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #ff3385 0%, #ff8833 50%, #ffcc00 100%); padding: 40px 20px; text-align: center; color: #ffffff;">
                        <h1 style="font-size: 28px; font-weight: 700; margin: 0;">Neo-e posta<br>doğrulama<br>kodunuz</h1>
                        <p style="font-size: 12px; margin-top: 10px;">Bu kodu kimseyle paylaşmayın ve bu e-postaya yanıt vermeyin.</p>
                    </div>
                    <div style="padding: 30px 20px; text-align: center;">
                        <p style="font-weight: bold; font-size: 14px; color: #333;">Doğrulama kodu</p>
                        <div style="background: linear-gradient(90deg, #ff7733, #ff3385); color: #ffffff; font-size: 32px; font-weight: bold; letter-spacing: 6px; padding: 12px 25px; border-radius: 50px; display: inline-block;">
                            {kod}
                        </div>
                        <table style="width: 100%; margin-top: 25px; border-spacing: 5px;">
                            <tr>
                                <td style="border: 1px solid #eee; border-radius: 10px; padding: 10px; font-size: 11px; text-align:center;">Hatasız ve sınırsız∞</td>
                                <td style="border: 1px solid #eee; border-radius: 10px; padding: 10px; font-size: 11px; text-align:center;">Çevre dostu🌿</td>
                                <td style="border: 1px solid #eee; border-radius: 10px; padding: 10px; font-size: 11px; text-align:center;">Hızlı ve güvenli🔒</td>
                            </tr>
                        </table>
                    </div>
                    <div style="border-top: 1px solid #ffa66; padding: 15px; text-align: center; font-size: 10px; color: #666; background-color: #fafafa;">
                        <p style="margin: 0;">Bu E-posta Neo yeni nesil yapay zeka tarafından gönderilmiştir.</p>
                        <p style="margin: 3px 0 0 0; font-weight: bold;">© Neo</p>
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
                st.success(
                    "Doğrulama kodu e-postanıza gönderildi! Spama bakmayı unutmayın."
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
