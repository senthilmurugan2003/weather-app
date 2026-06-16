from flask import Flask
from api.app import app

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask on Vercel!"