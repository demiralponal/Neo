import random
import google.generativeai as genai
import resend
import streamlit as st

# 1. API Ayarları (Secrets Kutusundan Çekilir)
resend.api_key = st.secrets["RESEND_API_KEY"]
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Gemini Yapay Zeka Modelini Başlatma
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Neo AI", page_icon="🤖", layout="centered")

# 2. Oturum Durumlarını (Session State) Başlatma
if "dogrulama_kodu" not in st.session_state:
    st.session_state.dogrulama_kodu = None
if "giris_basarili" not in st.session_state:
    st.session_state.giris_basarili = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# AŞAMA 1: GİRİŞ VE E-POSTA DOĞRULAMA EKRANI
# ---------------------------------------------------------
if not st.session_state.giris_basarili:
    st.title("🤖 Neo AI'ya Hoş Geldiniz")
    st.write("Sisteme giriş yapmak için e-posta adresinizi girin.")

    eposta = st.text_input("E-posta Adresiniz:", placeholder="ornek@gmail.com")

    if st.button("Doğrulama Kodu Gönder"):
        if eposta:
            # 6 haneli rastgele kod üretimi
            kod = str(random.randint(100000, 999999))
            st.session_state.dogrulama_kodu = kod

            try:
                # Resend üzerinden otomatik noreply e-postası gönderimi
                resend.Emails.send(
                    {
                        "from": "Neo AI <onboarding@resend.dev>",
                        "to": eposta,
                        "subject": "Neo AI - Giriş Doğrulama Kodunuz",
                        "html": f"""
                        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                            <h2 style="color: #2c3e50;">Neo AI Giriş Doğrulama</h2>
                            <p>Sisteme giriş yapabilmek için kullanacağınız doğrulama kodunuz aşağıdadır:</p>
                            <h1 style="color: #27ae60; letter-spacing: 4px;">{kod}</h1>
                            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                            <p style="font-size: 12px; color: #7f8c8d;">
                                Bu e-posta sistem tarafından otomatik olarak gönderilmiştir, lütfen yanıtlamayınız (noreply).
                            </p>
                        </div>
                    """,
                    }
                )
                st.success(
                    "Doğrulama kodu e-posta adresinize otomatik olarak gönderildi!"
                )
            except Exception as e:
                st.error(f"E-posta gönderilirken bir hata oluştu: {e}")
        else:
            st.warning("Lütfen geçerli bir e-posta adresi girin.")

    # Kod Onay Kutusu
    if st.session_state.dogrulama_kodu:
        st.divider()
        girilen_kod = st.text_input(
            "E-postanıza gelen 6 haneli kodu girin:", type="password"
        )
        if st.button("Giriş Yap"):
            if girilen_kod == st.session_state.dogrulama_kodu:
                st.session_state.giris_basarili = True
                st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                st.rerun()
            else:
                st.error("Hatalı kod girdiniz, lütfen tekrar deneyin.")

# ---------------------------------------------------------
# AŞAMA 2: NEO AI SOHBET EKRANI (GİRİŞ YAPILDIKTAN SONRA)
# ---------------------------------------------------------
else:
    st.title("💬 Neo AI Asistan")

    # Geçmiş Mesajları Listeleme
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcı Mesaj Girişi
    if prompt := st.chat_input("Neo AI'ya bir şeyler yazın..."):
        # Kullanıcı mesajını ekrana ve hafızaya ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Yapay Zeka Cevabını Üretme
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
                    st.error(f"Yanıt üretilirken hata oluştu: {e}")
