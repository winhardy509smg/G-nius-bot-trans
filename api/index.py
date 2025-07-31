import json
import requests
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)

ACCESS_TOKEN = 'EAAccCD0UlBYBPIYABnatsjiXZBrTJ2muSHxH5FMjCUBkO7FyoLhde5hZAZCiKw2taeAaUY5K3NFoVlm76WMfX72qX64ZBAJGOxmydnckonWdlPOaLRwkI8XSrwtzqZAO1pb5IpWNH3BWjZAM7VgHhAB0CZAUyDIMzhGMwZCSa2XYbZCZBJrkPp2KK1a9BgljLDXl0cJrHhAHqBLwZDZD'
VERIFY_TOKEN = '1'
RAPIDAPI_KEY = '25a0bc49d4mshc853ca05fe33cd6p14a1fdjsn911b5297e50b'

bot = Bot(ACCESS_TOKEN)
user_message_buffer = {}

@app.route('/ping', methods=['GET'])
def ping():
    return "hello world"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        if token == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    payload = request.get_json()
    for entry in payload.get('entry', []):
        for messaging_event in entry.get('messaging', []):
            if messaging_event.get('message'):
                sender_id = messaging_event['sender']['id']
                message = messaging_event['message']

                if 'quick_reply' in message:
                    target_lang = message['quick_reply']['payload']
                    original_text = user_message_buffer.pop(sender_id, None)
                    if original_text:
                        url = "https://google-translate-v21.p.rapidapi.com/translate"
                        translate_payload = {
                            "text_to_translate": original_text,
                            "dest": target_lang
                        }
                        headers = {
                            "x-rapidapi-key": RAPIDAPI_KEY,
                            "x-rapidapi-host": "google-translate-v21.p.rapidapi.com",
                            "Content-Type": "application/json"
                        }
                        res = requests.post(url, json=translate_payload, headers=headers)
                        result = res.json()
                        info = result.get("translation_info", "")
                        translation = result.get("translation", "")
                        bot.send_text_message(sender_id, info)
                        bot.send_text_message(sender_id, translation)
                    continue

                text = message.get('text')
                if text:
                    url = "https://google-translate-v21.p.rapidapi.com/detect"
                    detect_payload = { "text": text }
                    headers = {
                        "x-rapidapi-key": RAPIDAPI_KEY,
                        "x-rapidapi-host": "google-translate-v21.p.rapidapi.com",
                        "Content-Type": "application/json"
                    }
                    res = requests.post(url, json=detect_payload, headers=headers)
                    language = res.json().get("detected_language", "")

                    user_message_buffer[sender_id] = text

                    languages = {
                        '🇲🇬Malagasy': 'mg',
                        '🇬🇧Anglais':  'en',
                        '🇫🇷Français': 'fr',
                        '🇪🇸Espagnol': 'es',
                        '🇩🇪Allemand': 'de',
                        '🇦🇪Arabe': 'ar',
                        '🇮🇱Hebrew': 'he',
                        '🇰🇷Coréen': 'ko',
                        '🇯🇵Japonais': 'ja',
                        '🇮🇹Italien': 'it',
                        '🇨🇳Chinois': 'zh-cn'
                    }
                    languages = {name: code for name, code in languages.items() if code != language}

                    quick_replies = [
                        {
                            "content_type": "text",
                            "title": name,
                            "payload": code
                        } for name, code in languages.items()
                    ]

                    response_payload = {
                        "recipient": {"id": sender_id},
                        "message": {
                            "text": "Ho adika amin'ny teny 👇",
                            "quick_replies": quick_replies
                        }
                    }

                    requests.post(
                        'https://graph.facebook.com/v12.0/me/messages',
                        params={"access_token": ACCESS_TOKEN},
                        headers={"Content-Type": "application/json"},
                        json=response_payload
                    )
    return "ok", 200

