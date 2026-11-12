# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ============================================================
# СЮДА ВСТАВЬТЕ СВОИ ДАННЫЕ ИЗ TELEGRAM
# ============================================================
TELEGRAM_BOT_TOKEN = "9047299447:AAFE3uX6nG-PFU5ighq0EsjKByrtKC-IbCc"
TELEGRAM_CHAT_ID = "5268550316"

import os
from datetime import datetime

# ... ваши остальные импорты и настройки ...

def send_tg_notification(name, phone, service, date, time):
    # Текущее время отправки заявки
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    text = (
        f"🌸 *Новая заявка!*\n\n"
        f"👤 *Имя:* {name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"💆 *Услуга:* {service}\n"
        f"📅 *Дата визита:* {date}\n"
        f"🕐 *Время визита:* {time}\n\n"
        f"⏱ _Заявка отправлена: {now}_"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"=== Статус Telegram: {response.status_code}")
        print(f"=== Ответ Telegram: {response.text}")
    except Exception as e:
        print(f"=== Ошибка сети: {e}")

@app.route("/booking", methods=["POST"])
def booking():
    # Получаем все данные из формы
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    
    if all([name, phone, service, date, time]):
        send_tg_notification(name, phone, service, date, time)
        return """
        <script>
            alert('Спасибо, ' + %s + '! Ваша заявка принята. Мы свяжемся с вами! 🌸');
            window.location.href = '/';
        </script>
        """ % repr(name)
    else:
        return """
        <script>
            alert('Пожалуйста, заполните все поля.');
            window.location.href = '/';
        </script>
        """
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)