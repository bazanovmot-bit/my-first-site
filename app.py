# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

# ============================================================
# НАСТРОЙКИ TELEGRAM
# (Значения берутся из переменных окружения на Render)
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_tg_notification(name, phone, service, date, time):
    """Отправляет красивое уведомление в Telegram."""
    # Текущее время отправки заявки
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    text = (
        f"🌸 *Новая заявка на сайте!*\n\n"
        f"👤 *Имя:* {name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"💆 *Услуга:* {service}\n"
        f"📅 *Дата визита:* {date}\n"
        f"🕐 *Время визита:* {time}\n\n"
        f"⏱ _Отправлено: {now}_"
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


# ============================================================
# МАРШРУТЫ САЙТА
# ============================================================
@app.route("/")
def home():
    return render_template("index.html")     # Косметология (главная)


@app.route("/casino")
def casino_page():
    return render_template("casino.html")    # Казино


@app.route("/python")
def python_page():
    return render_template("python.html")    # Сайт про Python


@app.route("/booking", methods=["GET", "POST"])
def booking():
    # Если пользователь просто открыл ссылку /booking в браузере
    if request.method == "GET":
        return redirect("/")

    # Если пришли данные из формы (POST)
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    
    # Проверяем, что все поля заполнены
    if all([name, phone, service, date, time]):
        send_tg_notification(name, phone, service, date, time)
        
        # Показываем всплывающее окно и возвращаем на главную
        return f"""
        <script>
            alert('Спасибо, {name}! Ваша заявка принята. Мы свяжемся с вами! 🌸');
            window.location.href = '/';
        </script>
        """
    else:
        # Если что-то не заполнено
        return """
        <script>
            alert('Пожалуйста, заполните все поля.');
            window.location.href = '/#booking';
        </script>
        """


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)