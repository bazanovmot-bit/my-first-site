# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")        # косметология


@app.route("/casino")
def casino_page():
    return render_template("casino.html")       # казино


@app.route("/python")
def python_page():
    return render_template("python.html")       # Python


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)