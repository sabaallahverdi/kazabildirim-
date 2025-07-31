import os
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# This dictionary will store report data for each user
user_reports = {}

# --- Your Bot Functions ---

# ✅ Ana Menü
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 Yeni bir kaza bildirimi başlatmak için butona tıklayın:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("🚨 Kaza Bildir")]],
            resize_keyboard=True
        )
    )
    user_reports.pop(update.effective_user.id, None)  # Reset user state

# ✅ /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# ✅ Kaza Bildir butonu
async def begin_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_reports[user_id] = {} # Start a new report for the user

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
    if user_id not in user_reports:
        user_reports[user_id] = {} # Ensure user entry exists
    user_reports[user_id]['location'] = location

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
        user_reports[user_id] = {} # Ensure user entry exists
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
        await begin_report(update, context) # Restart the process
        return

    loc = user_reports[user_id]['location']
    phone = user_reports[user_id]['phone']

    caption = (
        f"🚨 Kaza Bildirimi\n"
        f"👤 @{user.username or 'İsimsiz'}\n"
        f"🆔 ID: {user.id}\n"
        f"📞 Tel: {phone}\n"
        f"📌 Konum: https://www.google.com/maps?q={loc.latitude},{loc.longitude}"
    )
    
    # Send information to the admin
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo.file_id, caption=caption)
    
    # Thank the user and reset the bot for them
    await update.message.reply_text(
        "✅ Tüm bilgiler alındı. Doğrulama sonrası sizinle iletişime geçilecektir. Teşekkür ederiz!",
    )
    await show_main_menu(update, context)

# --- Main function to run the bot ---

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^🚨 Kaza Bildir$"), begin_report))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot until the user presses Ctrl-C
    print("✅ Bot is running... Polling for updates.")
    application.run_polling()

if __name__ == "__main__":
    main()
