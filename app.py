from flask import Flask, request, jsonify
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Flask app
app = Flask(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID', 764067662))

# Check if required environment variables are set
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")
user_reports = {}

# Initialize bot application
bot_app = Application.builder().token(BOT_TOKEN).build()

# ✅ Ana Menü
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 Yeni bir kaza bildirimi başlatmak için butona tıklayın:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("🚨 Kaza Bildir")]],
            resize_keyboard=True
        )
    )
    user_reports.pop(update.effective_user.id, None)  # reset user state

# ✅ /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# ✅ Kaza Bildir butonu
async def begin_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_reports[user_id] = {}

    await update.message.reply_text(
        "📍 Lütfen kaza yerinin konumunu gönderin.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Konumumu Gönder", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

# ✅ Konum alındı
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    location = update.message.location
    user_reports[user_id] = {'location': location}

    await update.message.reply_text(
        "📞 Şimdi lütfen aşağıdaki butonla telefon numaranızı paylaşın.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Numaramı Paylaş", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

# ✅ Telefon numarası alındı
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    contact = update.message.contact
    if user_id not in user_reports:
        user_reports[user_id] = {}
    user_reports[user_id]['phone'] = contact.phone_number

    await update.message.reply_text(
        "📷 Şimdi lütfen kazaya ait bir fotoğraf gönderin.",
        reply_markup=ReplyKeyboardRemove()
    )

# ✅ Fotoğraf geldi → admin'e gönderilir → bot sıfırlanır
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    photo = update.message.photo[-1]

    if user_id not in user_reports or 'location' not in user_reports[user_id] or 'phone' not in user_reports[user_id]:
        await update.message.reply_text("⚠️ Lütfen önce konum ve telefon numarası paylaşın.")
        return

    loc = user_reports[user_id]['location']
    phone = user_reports[user_id]['phone']

    # Admin'e bilgi
    caption = (
        f"🚨 Kaza Bildirimi\n"
        f"👤 @{user.username or 'İsimsiz'}\n"
        f"🆔 ID: {user.id}\n"
        f"📞 Tel: {phone}\n"
        f"📌 Konum: {loc.latitude}, {loc.longitude}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=caption)
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo.file_id, caption="📸 Fotoğraf")

    # Kullanıcıya teşekkür + tekrar başlat
    await update.message.reply_text(
        "✅ Tüm bilgiler alındı. Doğrulama sonrası sizinle iletişime geçilecektir. Teşekkür ederiz!",
    )
    await show_main_menu(update, context)  # reset + tekrar başlatma butonu

# Add handlers to bot
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.Regex("^🚨 Kaza Bildir$"), begin_report))
bot_app.add_handler(MessageHandler(filters.LOCATION, handle_location))
bot_app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# Flask routes
@app.route('/')
def home():
    return jsonify({
        "status": "Bot is running!",
        "message": "Kaza Bildirim Botu aktif"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    if request.method == 'POST':
        update = Update.de_json(request.get_json(), bot_app.bot)
        bot_app.process_update(update)
        return jsonify({"status": "ok"})

@app.route('/set_webhook')
def set_webhook():
    """Set webhook for Telegram bot"""
    webhook_url = os.environ.get('WEBHOOK_URL', 'https://your-app-name.onrender.com/webhook')
    bot_app.bot.set_webhook(url=webhook_url)
    return jsonify({"status": "webhook set", "url": webhook_url})

if __name__ == '__main__':
    # Start the bot
    bot_app.initialize()
    bot_app.start()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 