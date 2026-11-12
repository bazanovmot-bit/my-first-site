# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ============================================================
# СЮДА ВСТАВЬТЕ СВОИ ДАННЫЕ ИЗ TELEGRAM
# ============================================================
TELEGRAM_BOT_TOKEN = "9047299447:AAFE3uX6nG-PFU5ighq0EsjKByrtKC-IbCc"
TELEGRAM_CHAT_ID = "5268550316"

def send_tg_notification(phone):
    text = f"🌸 Новая заявка с сайта!\n\n📞 Телефон: {phone}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        # Эти строки будут видны в логах Render
        print(f"=== Статус Telegram: {response.status_code}")
        print(f"=== Ответ Telegram: {response.text}")
    except Exception as e:
        print(f"=== Ошибка отправки: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/casino")
def casino_page():
    return render_template("casino.html")

@app.route("/python")
def python_page():
    return render_template("python.html")

@app.route("/booking", methods=["POST"])
def booking():
    phone = request.form.get("phone", "").strip()
    
    if phone:
        send_tg_notification(phone)
        return """
        <script>
            alert('Спасибо! Ваш номер ' + %s + ' отправлен. Мы свяжемся с вами! 🌸');
            window.location.href = '/';
        </script>
        """ % repr(phone)
    else:
        return """
        <script>
            alert('Пожалуйста, введите номер телефона.');
            window.location.href = '/';
        </script>
        """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)