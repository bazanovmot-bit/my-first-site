# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import requests
from flask import redirect, url_for

app = Flask(__name__)

# ============================================================
# СЮДА ВСТАВЬТЕ СВОИ ДАННЫЕ ИЗ TELEGRAM
# ============================================================
TELEGRAM_BOT_TOKEN = "9047299447:AAFE3uX6nG-PFU5ighq0EsjKByrtKC-IbCc"
TELEGRAM_CHAT_ID = "5268550316"

import os
from datetime import datetime

# ... ваши остальные импорты и настройки ...

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        # Получаем данные из формы
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        service = request.form.get("service", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        
        if all([name, phone, service, date, time]):
            send_tg_notification(name, phone, service, date, time)
            # Возвращаем скрипт с сообщением и редиректом на главную
            return f"""
            <script>
                alert('Спасибо, {name}! Ваша заявка принята. Мы свяжемся с вами! 🌸');
                window.location.href = '/';
            </script>
            """
            
    # Если зашли через GET (просто открыли ссылку) — кидаем на главную
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)