import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/settings.json')
def settings():
    return jsonify({
        "bot_token": os.environ.get("BOT_TOKEN"),
        "chat_id": os.environ.get("CHAT_ID")
    })
