# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/python")
def python_page():
    return render_template("python.html")


@app.route("/beauty")
def beauty_page():
    return render_template("beauty.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)