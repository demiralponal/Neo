from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- TEMPLATE: Kayıt Sayfası (Görsel 6 & 7 Entegre) ---
HTML_REGISTER = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Neo - Türkiye'nin Yeni Yapay Zekası</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #fcf9f2; color: #2d3748; display: flex; justify-content: center; padding: 20px 10px; }
    .container { width: 100%; max-width: 500px; background-color: #fdfbf7; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .hero-banner { background-color: #2cb67d; color: #ffffff; padding: 35px 20px 25px 20px; text-align: center; }
    .hero-banner h1 { font-family: 'Georgia', serif; font-size: 32px; font-weight: 500; margin-bottom: 5px; }
    .hero-banner p { font-size: 14px; opacity: 0.9; margin-bottom: 25px; }
    .btn-register { display: inline-block; background-color: #ffffff; color: #1a1a1a; padding: 10px 24px; border-radius: 20px; text-decoration: none; font-size: 13px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .section-title { font-family: 'Georgia', serif; color: #2cb67d; font-size: 26px; text-align: center; margin: 30px 0 20px 0; font-weight: 500; }
    .cards-grid { display: flex; justify-content: space-between; gap: 10px; padding: 0 15px; margin-bottom: 35px; }
    .card { flex: 1; border-radius: 12px; padding: 15px 8px; text-align: center; min-height: 140px; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; }
    .card-purple { background-color: #d17bb8; color: #ffffff; }
    .card-green { background-color: #2cb67d; color: #ffffff; }
    .card-yellow { background-color: #f7e1a0; color: #333333; }
    .card p { font-size: 11px; line-height: 1.3; font-weight: 500; }
    .action-section { padding: 0 20px; margin-bottom: 30px; }
    .action-title { font-family: 'Georgia', serif; color: #2cb67d; font-size: 24px; line-height: 1.2; margin-bottom: 20px; }
    .form-container { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 25px 20px; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
    .form-title { font-family: 'Impact', 'Arial Black', sans-serif; font-size: 28px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 15px; color: #000000; }
    .form-group { margin-bottom: 18px; text-align: left; }
    .form-group label { display: block; font-size: 14px; font-weight: 700; margin-bottom: 6px; color: #000000; }
    .form-group input { width: 100%; padding: 12px; border: 1px solid #333333; font-size: 14px; outline: none; }
    .btn-submit { width: 100%; background-color: #2cb67d; color: #ffffff; border: none; padding: 12px; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 10px; }
    .btn-submit:hover { background-color: #249667; }
    .footer { text-align: center; padding: 20px 15px 30px 15px; font-size: 12px; color: #666666; }
  </style>
</head>
<body>
  <div class="container">
    <div class="hero-banner">
      <h1>Neo'ya hoşgeldiniz</h1>
      <p>Türkiye'nin yeni yapay zekası</p>
      <a href="#kayit-formu" class="btn-register">KAYIT OLMAK İSTİYORUM</a>
    </div>

    <h2 class="section-title">Neler beklemelisiniz?</h2>
    
    <div class="cards-grid">
      <div class="card card-purple"><p>DJ'ler nostaljik şarkılar ve dans hitleri çalıyor</p></div>
      <div class="card card-green"><p>Özel menü<br>ve içecekler</p></div>
      <div class="card card-yellow"><p>Neon<br>fotoğraf kabini</p></div>
    </div>

    <div class="action-section">
      <h2 class="action-title">Burdan kayıt<br>ve giriş<br>işlemlerini<br>yapabilirsin</h2>

      <div id="kayit-formu" class="form-container">
        <h3 class="form-title">NEO KAYIT FORMU</h3>
        <form action="/register" method="POST">
          <div class="form-group">
            <label for="email">E posta</label>
            <input type="email" id="email" name="email" required>
          </div>
          <div class="form-group">
            <label for="fullname">Ad soyad</label>
            <input type="text" id="fullname" name="fullname" required>
          </div>
          <div class="form-group">
            <label for="password">Şifre</label>
            <input type="password" id="password" name="password" required>
          </div>
          <button type="submit" class="btn-submit">Kayıt Ol ve Doğrula</button>
        </form>
      </div>
    </div>

    <div class="footer">
      <p>Neo yeni yapay zeka tüm hakları saklıdır</p>
    </div>
  </div>
</body>
</html>
"""

# --- TEMPLATE: Doğrulama Ekranı (Görsel 1, 2, 3, 4, 5 Entegre) ---
HTML_VERIFY = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Neo - E-Posta Doğrulama</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #f4f4f7; display: flex; justify-content: center; align-items: center; padding: 20px; }
    .email-card { width: 100%; max-width: 500px; background-color: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08); text-align: center; }
    .header-banner { background: linear-gradient(135deg, #f7b733 0%, #fc4a1a 40%, #e14efa 70%, #ff007f 100%); padding: 40px 20px 30px 20px; color: #ffffff; }
    .header-banner h1 { font-size: 32px; font-weight: 700; line-height: 1.2; margin-bottom: 15px; }
    .header-banner p { font-size: 13px; opacity: 0.95; max-width: 380px; margin: 0 auto; }
    .content-area { padding: 30px 20px; }
    .code-title { font-family: "Courier New", Courier, monospace; font-size: 18px; font-weight: 700; color: #333333; margin-bottom: 20px; }
    .features-grid { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 30px; }
    .feature-card { flex: 1; background-color: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; padding: 15px 8px; display: flex; flex-direction: column; align-items: center; }
    .feature-card img { width: 48px; height: 48px; object-fit: contain; margin-bottom: 12px; }
    .feature-card p { font-size: 12px; color: #444444; font-weight: 600; }
    .neo-btn { display: inline-block; width: 160px; padding: 12px 0; background: linear-gradient(135deg, #ff8a00, #e52e71); color: #ffffff; font-size: 15px; font-weight: 700; border-radius: 25px; text-decoration: none; margin-bottom: 10px; }
    .divider { height: 1px; background: linear-gradient(90deg, #ff8a00 0%, #e52e71 50%, #8a238c 100%); margin: 20px 0 25px 0; opacity: 0.6; }
    .footer { font-size: 12px; color: #666666; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="email-card">
    <div class="header-banner">
      <h1>Neo–e posta<br>doğrulama<br>kodunuz</h1>
      <p>Bu kodu hiç kimseyle paylaşmamakla birlikte bu E postaya yanıt vermeyin</p>
    </div>

    <div class="content-area">
      <div class="code-title">Doğrulama kodu</div>

      <div class="features-grid">
        <div class="feature-card">
          <img src="{{ url_for('static', filename='image_2.png') }}" alt="Hatasız ve sınırsız">
          <p>Hatasız ve<br>sınırsız∞</p>
        </div>
        <div class="feature-card">
          <img src="{{ url_for('static', filename='image_3.png') }}" alt="Çevre dostu">
          <p>Çevre dostu🌿</p>
        </div>
        <div class="feature-card">
          <img src="{{ url_for('static', filename='image_4.png') }}" alt="Hızlı ve güvenli">
          <p>Hızlı ve güvenli🔐</p>
        </div>
      </div>

      <a href="/" class="neo-btn">Neo</a>

      <div class="divider"></div>

      <div class="footer">
        <p>Bu E posta Neo yeni nesil yapay zeka tarafından gönderilmiştir</p>
        <p>Tüm hakları saklıdır</p>
        <p><strong>© Neo</strong></p>
      </div>
    </div>
  </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    return render_template_string(HTML_REGISTER)

@app.route('/register', methods=['POST'])
def register():
    # Form verilerini yakalama alanı
    email = request.form.get('email')
    fullname = request.form.get('fullname')
    password = request.form.get('password')
    
    # Kayıt işlemleri gerçekleştirildikten sonra doğrulama koduna yönlendirme
    return redirect(url_for('verify'))

@app.route('/verify')
def verify():
    return render_template_string(HTML_VERIFY)

if __name__ == '__main__':
    app.run(debug=True)
