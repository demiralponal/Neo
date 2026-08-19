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
    /* Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
    }
    
    /* Gradient Başlıklar */
    h1, h2, h3 {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Şık Renkli Butonlar */
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
    
    /* Input Kutuları */
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
    
    /* Mesaj Baloncukları */
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
    # Düzeltilen model ismi:
    model = genai.GenerativeModel("gemini-1.5-flash")
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

            try:
                resend.Emails.send(
                    {
                        "from": "Neo AI <onboarding@resend.dev>",
                        "to": eposta,
                        "subject": "Neo AI - Giriş Kodunuz",
                        "html": f"""
                        <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #0f172a; color: #ffffff; border-radius: 12px;">
                            <h2 style="color: #38bdf8;">Neo AI Giriş</h2>
                            <p>Doğrulama kodunuz:</p>
                            <h1 style="color: #a855f7; letter-spacing: 5px;">{kod}</h1>
                            <hr style="border-color: #334155;" />
                            <p style="font-size: 12px; color: #94a3b8;">Bu e-posta otomatiktir, lütfen yanıtlamayınız (noreply).</p>
                        </div>
                    """,
                    }
                )
                st.success("Doğrulama kodu e-postanıza otomatik olarak gönderildi!")
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
