import random
import resend
import streamlit as st

# Resend API Anahtarı Tanımlaması
resend.api_key = st.secrets["RESEND_API_KEY"]

st.title("Neo AI - Giriş Paneli")

# Oturum durumlarını başlatma
if "dogrulama_kodu" not in st.session_state:
    st.session_state.dogrulama_kodu = None
if "giris_basarili" not in st.session_state:
    st.session_state.giris_basarili = False

# Giriş Yapılmadıysa Giriş Formunu Göster
if not st.session_state.giris_basarili:
    eposta = st.text_input("E-posta Adresiniz:")

    if st.button("Doğrulama Kodu Gönder"):
        if eposta:
            # 6 haneli rastgele kod üretme
            kod = str(random.randint(100000, 999999))
            st.session_state.dogrulama_kodu = kod

            try:
                # Resend üzerinden otomatik mail gönderimi
                resend.Emails.send(
                    {
                        "from": "Neo AI <onboarding@resend.dev>",
                        "to": eposta,
                        "subject": "Neo AI - Otomatik Doğrulama Kodunuz",
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

    # Kod Onay Alanı
    if st.session_state.dogrulama_kodu:
        girilen_kod = st.text_input("E-postanıza gelen 6 haneli kodu girin:")
        if st.button("Giriş Yap"):
            if girilen_kod == st.session_state.dogrulama_kodu:
                st.session_state.giris_basarili = True
                st.rerun()
            else:
                st.error("Hatalı kod girdiniz, lütfen tekrar deneyin.")

else:
    st.success("Tebrikler! Neo AI sistemine başarıyla giriş yaptınız.")
    # Ana uygulama içerikleri buraya gelecek
