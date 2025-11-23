
import os, json, requests, smtplib, ssl
from email.message import EmailMessage

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "email": "",
    "password": "",
    "contacts": [],
    "emergency_number": "911",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "video_duration": 10,
    "audio_enabled": True
}

def ensure_app_dirs():
    app_dir = os.path.join(os.getcwd(), "sos_data")
    os.makedirs(app_dir, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    return app_dir

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def get_location_ipinfo():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=6)
        if r.status_code == 200:
            d = r.json()
            return f"{d.get('city')}, {d.get('region')}, {d.get('country')} | loc: {d.get('loc')}"
        return "لم يتم الحصول على الموقع."
    except Exception as e:
        return f"خطأ بجلب الموقع: {e}"

def send_email(config, location, video_path=None, audio_path=None, image_path=None, transcript=""):
    contacts = config.get("contacts", [])
    if not contacts:
        return

    msg = EmailMessage()
    msg["From"] = config["email"]
    msg["To"] = ", ".join(contacts)
    msg["Subject"] = "🚨 SOS Emergency Alert"

    body = f"""🚨 تنبيه طوارئ

الموقع:
{location}

النص المحول من الصوت:
{transcript}

رقم الطوارئ: {config.get("emergency_number")}
"""
    msg.set_content(body)

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="photo.png")

    if video_path and os.path.exists(video_path):
        with open(video_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="video", subtype="mp4", filename="video.mp4")

    if audio_path and os.path.exists(audio_path):
        with open(audio_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="audio", subtype="mp4", filename="audio.m4a")

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls(context=context)
        smtp.login(config["email"], config["password"])
        smtp.send_message(msg)

def send_telegram(config, text, video_path=None, audio_path=None, image_path=None):
    token = config.get("telegram_bot_token", "").strip()
    chat_id = config.get("telegram_chat_id", "").strip()
    if not token or not chat_id:
        return
    base = f"https://api.telegram.org/bot{token}"

    try:
        import requests
        requests.post(f"{base}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=10)

        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                requests.post(f"{base}/sendPhoto", data={"chat_id": chat_id}, files={"photo": f}, timeout=30)

        if video_path and os.path.exists(video_path):
            with open(video_path, "rb") as f:
                requests.post(f"{base}/sendVideo", data={"chat_id": chat_id}, files={"video": f}, timeout=60)

        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                requests.post(f"{base}/sendAudio", data={"chat_id": chat_id}, files={"audio": f}, timeout=60)
    except Exception as e:
        print("خطأ في إرسال تيليجرام:", e)
