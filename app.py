import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(page_title="Neo - Yapay Zeka", page_icon="🤖", layout="centered")

# --- OTURUM VE DURUM (SESSION STATE) YÖNETİMİ ---
if "page" not in st.session_state:
    st.session_state.page = "register"

if "maintenance_mode" not in st.session_state:
    st.session_state.maintenance_mode = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "total_views" not in st.session_state:
    st.session_state.total_views = 0

if "registered_users" not in st.session_state:
    st.session_state.registered_users = []

# Ziyaretçi sayacını artır
st.session_state.total_views += 1

# Sayfa Değiştirme Fonksiyonu
def navigate_to(page_name):
    st.session_state.page = page_name

# URL Parametresi Kontrolü (?page=admin kontrolü)
query_params = st.query_params
if query_params.get("page") == "admin" and st.session_state.page != "admin":
    st.session_state.page = "admin"

# --- CSS STİLLERİ ---
st.markdown("""
    <style>
    .stApp { background-color: #fcf9f2; }
    .hero-banner { background-color: #2cb67d; color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 25px; }
    .hero-banner h1 { font-family: 'Georgia', serif; margin-bottom: 5px; }
    .card { background-color: #ffffff; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid #e0e0e0; }
    .admin-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- BAKIM MODU KONTROLÜ ---
# Yönetici haricindeki kullanıcılar bakım modundayken bu ekranı görür
if st.session_state.maintenance_mode and st.session_state.page != "admin":
    st.error("🛠️ **SİSTEM BAKIMDA**")
    st.info("Neo şu anda bakımdadır. Lütfen daha sonra tekrar deneyiniz.")
    st.stop()

# --- 1. SAYFA: KAYIT EKRANI ---
if st.session_state.page == "register":
    st.markdown("""
        <div class="hero-banner">
            <h1>Neo'ya hoşgeldiniz</h1>
            <p>Türkiye'nin yeni yapay zekası</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Neler beklemelisiniz?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='card' style='background-color: #d17bb8; color: white;'>DJ'ler nostaljik şarkılar ve dans hitleri çalıyor</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card' style='background-color: #2cb67d; color: white;'>Özel menü<br>ve içecekler</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card' style='background-color: #f7e1a0;'>Neon<br>fotoğraf kabini</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Burdan kayıt ve giriş işlemlerini yapabilirsin")
    
    with st.form("kayit_formu"):
        st.markdown("## NEO KAYIT FORMU")
        email = st.text_input("E posta")
        fullname = st.text_input("Ad soyad")
        password = st.text_input("Şifre", type="password")
        
        submit = st.form_submit_button("Kayıt Ol ve Doğrula")
        if submit:
            if email and fullname and password:
                # Kullanıcıyı listeye kaydet (İstatistik için)
                st.session_state.registered_users.append({
                    "email": email,
                    "fullname": fullname
                })
                navigate_to("verify")
                st.rerun()
            else:
                st.warning("Lütfen tüm alanları doldurun.")

# --- 2. SAYFA: DOĞRULAMA EKRANI ---
elif st.session_state.page == "verify":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f7b733, #fc4a1a, #e14efa); padding: 30px; border-radius: 15px; color: white; text-align: center;">
            <h1>Neo–e posta<br>doğrulama kodunuz</h1>
            <p style="font-size: 12px;">Bu kodu hiç kimseyle paylaşmamakla birlikte bu E postaya yanıt vermeyin</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Doğrulama kodu</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("Hatasız ve sınırsız ∞")
    with col2:
        st.success("Çevre dostu 🌿")
    with col3:
        st.warning("Hızlı ve güvenli 🔐")

    if st.button("Ana Sayfaya Dön", use_container_width=True):
        navigate_to("register")
        st.rerun()

# --- 3. SAYFA: ADMIN PANELI ---
elif st.session_state.page == "admin":
    st.title("🔒 Neo Yönetici Paneli")

    # Giriş Yapılmamışsa Şifre Ekranı Göster
    if not st.session_state.admin_logged_in:
        admin_password = st.text_input("Yönetici Şifresi", type="password")
        if st.button("Giriş Yap"):
            if admin_password == "040608.demir":
                st.session_state.admin_logged_in = True
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Hatalı şifre!")
    else:
        # Yönetici Paneli İçeriği
        st.subheader("⚙️ Sistem Kontrolleri")
        
        # Bakım Modu Anahtarı (Toggle)
        maintenance = st.toggle("Bakım Modunu Aktif Et", value=st.session_state.maintenance_mode)
        if maintenance != st.session_state.maintenance_mode:
            st.session_state.maintenance_mode = maintenance
            if maintenance:
                st.warning("Bakım modu açıldı. Kullanıcılar siteye erişemez.")
            else:
                st.success("Bakım modu kapatıldı. Site erişime açık.")

        st.markdown("---")
        st.subheader("📊 Canlı İstatistikler")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Sayfa Görüntülenmesi", value=st.session_state.total_views)
        with col2:
            st.metric(label="Toplam Kayıtlı Kullanıcı", value=len(st.session_state.registered_users))

        # Kayıtlı Kullanıcı Listesi
        st.markdown("### 👥 Son Kaydolan Kullanıcılar")
        if st.session_state.registered_users:
            st.dataframe(st.session_state.registered_users, use_container_width=True)
        else:
            st.info("Henüz kayıtlı kullanıcı bulunmuyor.")

        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Çıkış Yap"):
                st.session_state.admin_logged_in = False
                navigate_to("register")
                st.rerun()
        with col_btn2:
            if st.button("Ana Sayfaya Git"):
                navigate_to("register")
                st.rerun()

# --- SOL MENÜDEN YÖNETİCİ ARAMASI ---
st.sidebar.markdown("### 🔗 Hızlı Linkler")
if st.sidebar.button("Yönetici Paneli (Admin)"):
    navigate_to("admin")
    st.rerun()
