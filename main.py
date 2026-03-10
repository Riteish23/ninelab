import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = "1079652341888270"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

CLIENT_PROMPTS = {
    "default": "You are a helpful WhatsApp assistant. Reply in Marathi or Hindi. Keep answers short — 2-3 lines max.",
}

def get_prompt(phone):
    return CLIENT_PROMPTS.get(phone, CLIENT_PROMPTS["default"])

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

def generate_ai_reply(prompt, user_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object"):
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages")
                if messages:
                    message = messages[0]
                    from_number = message["from"]
                    text = message.get("text", {}).get("body", "")
                    if text:
                        system_prompt = get_prompt(from_number)
                        ai_reply = generate_ai_reply(system_prompt, text)
                        send_whatsapp_message(from_number, ai_reply)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
```

---

**Railway Variables मध्ये हे add कर:**
```
VERIFY_TOKEN = ninelab123
WHATSAPP_TOKEN = तुझा Meta token
OPENAI_API_KEY = तुझी key
