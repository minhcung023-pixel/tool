from flask import Flask, request, render_template_string
import re
import cloudscraper
from bs4 import BeautifulSoup
import sqlite3
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Minh Tool - Multi Bypass</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body { background: linear-gradient(135deg, #09090b 0%, #1a0b2e 50%, #001f3f 100%); color: #fff; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { width: 100%; max-width: 420px; background: rgba(15, 15, 20, 0.85); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; position: relative; }
        .container::before { content: ''; position: absolute; top: -1px; left: -1px; right: -1px; bottom: -1px; background: linear-gradient(45deg, #ff007f, #00e5ff); z-index: -1; border-radius: 21px; opacity: 0.5; }
        .logo { font-size: 32px; font-weight: 900; background: linear-gradient(90deg, #00e5ff, #ff007f); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; margin-bottom: 5px; text-transform: uppercase; }
        .subtitle { color: #00e5ff; font-size: 12px; margin-bottom: 15px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700; }
        .traffic { color: #ffeb3b; font-size: 12px; margin-bottom: 15px; font-weight: 700; text-transform: uppercase; }
        .tabs { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px; }
        .tab-btn { padding: 8px 12px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: #aaa; font-size: 12px; font-weight: 700; cursor: pointer; transition: 0.3s; }
        .tab-btn.active { background: linear-gradient(90deg, #ff007f, #7000ff); color: #fff; border-color: transparent; box-shadow: 0 0 10px rgba(255,0,127,0.4); }
        input { width: 100%; padding: 16px; border-radius: 12px; border: 1px solid rgba(0, 229, 255, 0.3); background: rgba(0, 0, 0, 0.6); color: #fff; font-size: 15px; outline: none; transition: 0.2s; margin-bottom: 15px; }
        input:focus { border-color: #ff007f; box-shadow: 0 0 10px rgba(255, 0, 127, 0.3); }
        button[type="submit"] { width: 100%; padding: 16px; border-radius: 12px; border: none; background: linear-gradient(90deg, #ff007f, #7000ff); color: #fff; font-size: 16px; font-weight: 900; text-transform: uppercase; cursor: pointer; transition: 0.2s; }
        button[type="submit"]:active { transform: scale(0.96); }
        .result-box { margin-top: 20px; padding: 15px; border-radius: 12px; background: rgba(0, 0, 0, 0.8); border: 1px solid #00e5ff; text-align: left; display: block; }
        .result-box.error { border-color: #ff007f; color: #ff007f; }
        .result-label { font-size: 12px; color: #aaa; margin-bottom: 8px; text-transform: uppercase; font-weight: 700;}
        .result-link { display: block; color: #00e5ff; font-size: 14px; font-weight: 700; text-decoration: none; word-break: break-all; background: rgba(0, 229, 255, 0.1); padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Minh Tool</div>
        <div class="subtitle">Multi Bypass</div>
        <div class="traffic">🔥 Tổng lượt vượt: {{ traffic }}</div>
        
        <div class="tabs">
            <div class="tab-btn active" onclick="setTab('link4m', this)">Link4M</div>
            <div class="tab-btn" onclick="setTab('link4me', this)">Link4.Me</div>
            <div class="tab-btn" onclick="setTab('trafficvn', this)">Traffic.vn</div>
            <div class="tab-btn" onclick="setTab('layarkaca', this)">LayarKaca</div>
            <div class="tab-btn" onclick="setTab('link1s', this)">Link1s</div>
            <div class="tab-btn" onclick="setTab('other', this)">Khác</div>
        </div>

        <form method="POST" action="/">
            <input type="url" id="urlInput" name="url" placeholder="Dán link Link4M vào đây..." required autocomplete="off">
            <button type="submit">Vượt Ngay</button>
        </form>
        
        {% if result_link %}
        <div class="result-box">
            <div class="result-label">Link gốc đây bro:</div>
            <a href="{{ result_link }}" class="result-link" target="_blank">{{ result_link }}</a>
        </div>
        {% endif %}

        {% if error %}
        <div class="result-box error">Lỗi: {{ error }}</div>
        {% endif %}
    </div>

    <script>
        const placeholders = {
            'link4m': 'Dán link Link4M vào đây...',
            'link4me': 'Dán link Link4.Me vào đây...',
            'trafficvn': 'Dán link Traffic.vn vào đây...',
            'layarkaca': 'Dán link LayarKaca vào đây...',
            'link1s': 'Dán link Link1s vào đây...',
            'other': 'Dán link rút gọn bất kỳ...'
        };
        function setTab(tabName, btnElement) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            btnElement.classList.add('active');
            document.getElementById('urlInput').placeholder = placeholders[tabName];
        }
    </script>
</body>
</html>
"""

def init_db():
    conn = sqlite3.connect('minhtool.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS traffic (id INTEGER PRIMARY KEY, count INTEGER)')
    c.execute('INSERT OR IGNORE INTO traffic (id, count) VALUES (1, 0)')
    conn.commit()
    conn.close()

def get_traffic():
    try:
        conn = sqlite3.connect('minhtool.db')
        c = conn.cursor()
        c.execute('SELECT count FROM traffic WHERE id = 1')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 0
    except:
        return 0

def add_traffic():
    try:
        conn = sqlite3.connect('minhtool.db')
        c = conn.cursor()
        c.execute('UPDATE traffic SET count = count + 1 WHERE id = 1')
        conn.commit()
        conn.close()
    except:
        pass

def bypass_logic(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    try:
        r = scraper.get(url, timeout=20)
    except Exception as e:
        return None, f"Lỗi mạng: {str(e)}"

    if r.status_code != 200:
        return None, f"Bị chặn (Status: {r.status_code})"

    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form", id="go-link") 
    if not form:
        for f in soup.find_all("form"):
            if f.find("input", type="hidden") or f.find("button"):
                form = f
                break

    if not form:
        m = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)', r.text)
        if m: return m.group(1), None
        meta = soup.find("meta", attrs={"http-equiv": re.compile("refresh", re.I)})
        if meta and "url=" in meta.get("content", "").lower():
            return meta["content"].split("url=")[-1].strip(" '\""), None
        return None, "Không tìm thấy form token hay link ẩn. (Có thể bị Captcha/Turnstile)"

    action = form.get("action") or url
    if action.startswith("/"):
        domain_match = re.match(r'(https?://[^/]+)', url)
        if domain_match: action = domain_match.group(1) + action

    payload = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if name: payload[name] = inp.get("value", "")

    try:
        resp = scraper.post(action, data=payload, timeout=20, allow_redirects=False)
    except Exception as e:
        return None, f"Lỗi gửi POST: {str(e)}"

    if resp.status_code in (301, 302, 303, 307, 308):
        return resp.headers.get("Location"), None

    m = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)', resp.text)
    if m: return m.group(1), None

    try:
        data = resp.json()
        if isinstance(data, dict):
            for key in ["url", "links", "destination"]:
                if key in data: return data[key], None
    except: pass

    urls = re.findall(r'https?://[^\s"\'<>]+', resp.text)
    for u in urls:
        if not any(x in u for x in ["link4m", "link4.me", "traffic.vn", "layarkaca", "cloudflare", "google"]):
            return u, None

    return None, "Đéo tìm thấy link đích. (Turnstile nó chặn rồi)"

@app.route('/', methods=['GET', 'POST'])
def home():
    init_db()
    traffic = get_traffic()
    
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template_string(HTML_PAGE, error="Mày chưa nhập link.", traffic=traffic)
            
        final_url, err = bypass_logic(url)
        
        if final_url:
            add_traffic()
            traffic = get_traffic()
            
        return render_template_string(HTML_PAGE, result_link=final_url, error=err, traffic=traffic)
        
    return render_template_string(HTML_PAGE, traffic=traffic)

if __name__ == '__main__':
    home()
    app.run(host='0.0.0.0', port=5000)
