from flask import Flask, request, render_template_string
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Giao diện HTML (Minh Tool)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Minh Tool</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body { 
            background: linear-gradient(135deg, #09090b 0%, #1a0b2e 50%, #001f3f 100%);
            color: #fff; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px;
        }
        .container {
            width: 100%; max-width: 400px; background: rgba(15, 15, 20, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px;
            padding: 30px 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            text-align: center; position: relative;
        }
        .container::before {
            content: ''; position: absolute; top: -1px; left: -1px; right: -1px; bottom: -1px;
            background: linear-gradient(45deg, #ff007f, #00e5ff); z-index: -1; border-radius: 21px; opacity: 0.5;
        }
        .logo {
            font-size: 36px; font-weight: 900;
            background: linear-gradient(90deg, #00e5ff, #ff007f);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -1px; margin-bottom: 5px; text-transform: uppercase;
        }
        .subtitle { color: #00e5ff; font-size: 13px; margin-bottom: 30px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700; }
        input {
            width: 100%; padding: 16px; border-radius: 12px;
            border: 1px solid rgba(0, 229, 255, 0.3); background: rgba(0, 0, 0, 0.6);
            color: #fff; font-size: 15px; outline: none; transition: 0.2s; margin-bottom: 15px;
        }
        input:focus { border-color: #ff007f; box-shadow: 0 0 10px rgba(255, 0, 127, 0.3); }
        button {
            width: 100%; padding: 16px; border-radius: 12px; border: none;
            background: linear-gradient(90deg, #ff007f, #7000ff); color: #fff;
            font-size: 16px; font-weight: 900; text-transform: uppercase; cursor: pointer; transition: 0.2s;
        }
        button:active { transform: scale(0.96); }
        .result-box {
            margin-top: 20px; padding: 15px; border-radius: 12px;
            background: rgba(0, 0, 0, 0.8); border: 1px solid #00e5ff; text-align: left; display: block;
        }
        .result-box.error { border-color: #ff007f; color: #ff007f; }
        .result-label { font-size: 12px; color: #aaa; margin-bottom: 8px; text-transform: uppercase; font-weight: 700;}
        .result-link {
            display: block; color: #00e5ff; font-size: 14px; font-weight: 700;
            text-decoration: none; word-break: break-all; background: rgba(0, 229, 255, 0.1);
            padding: 10px; border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Minh Tool</div>
        <div class="subtitle">Cyber Bypass</div>
        
        <form method="POST" action="/">
            <input type="url" name="url" placeholder="Dán link4m vào đây..." required autocomplete="off">
            <button type="submit">Vượt Ngay</button>
        </form>
        
        {% if result_link %}
        <div class="result-box">
            <div class="result-label">Link gốc đây bro:</div>
            <a href="{{ result_link }}" class="result-link" target="_blank">{{ result_link }}</a>
        </div>
        {% endif %}

        {% if error %}
        <div class="result-box error">
            Lỗi: {{ error }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def bypass_logic(url):
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://link4m.com/"})
    
    try:
        r = s.get(url, timeout=15)
    except Exception as e:
        return None, f"Lỗi mạng: {str(e)}"

    if r.status_code != 200:
        return None, f"Bị chặn (Status: {r.status_code})"

    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form", id="go-link") or soup.find("form")
    
    if not form:
        m = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)', r.text)
        if m: return m.group(1), None
        return None, "Không tìm thấy form token hay link ẩn."

    action = form.get("action") or url
    if action.startswith("/"):
        action = "https://link4m.com" + action

    payload = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if name:
            payload[name] = inp.get("value", "")

    try:
        resp = s.post(action, data=payload, timeout=15, allow_redirects=False)
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
    except:
        pass

    urls = re.findall(r'https?://[^\s"\'<>]+', resp.text)
    for u in urls:
        if "link4m" not in u and "cloudflare" not in u:
            return u, None

    return None, "Đéo tìm thấy link đích."

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template_string(HTML_PAGE, error="Mày chưa nhập link.")
            
        final_url, err = bypass_logic(url)
        return render_template_string(HTML_PAGE, result_link=final_url, error=err)
        
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
