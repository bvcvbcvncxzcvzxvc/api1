import requests

def get_settings():
    url = "https://tg-api-service.onrender.com/settings.json"
    response = requests.get(url)
    data = response.json()
    return data['bot_token'], data['chat_id']

BOT_TOKEN, CHAT_ID = get_settings()
