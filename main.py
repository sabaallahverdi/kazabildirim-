import os
from flask import Flask, request
import telebot
from telebot import types

API_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_URL = os.environ['RENDER_EXTERNAL_HOSTNAME'] + "/webhook"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# دکمه ها
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("🚨 Kaza Bildir")
    markup.add(btn)
    return markup

# استارت
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Hoş geldin! Kaza bildirimi için aşağıdaki butonu kullan.", reply_markup=main_menu())

# کزا دکمه‌س
@bot.message_handler(func=lambda message: message.text == "🚨 Kaza Bildir")
def accident_report(message):
    bot.send_message(message.chat.id, "🚨 Kaza bildiriminiz alındı. Yardım yolda!")

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True), bot)
    bot.process_new_updates([update])
    return 'ok', 200

# Webhook kurulum
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

