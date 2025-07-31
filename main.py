
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID"))

user_reports = {}

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 Yeni bir kaza bildirimi başlatmak için butona tıklayın:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("🚨 Kaza Bildir")]],
            resize_keyboard=True
        )
    )
    user_reports.pop(update.effective_user.id, None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

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

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    photo = update.message.photo[-1]
    if user_id not in user_reports or 'location' not in user_reports[user_id] or 'phone' not in user_reports[user_id]:
        await update.message.reply_text("⚠️ Lütfen önce konum ve telefon numarası paylaşın.")
        return
    loc = user_reports[user_id]['location']
    phone = user_reports[user_id]['phone']
    caption = (
        f"🚨 Kaza Bildirimi\n"
        f"👤 @{user.username or 'İsimsiz'}\n"
        f"🆔 ID: {user.id}\n"
        f"📞 Tel: {phone}\n"
        f"📌 Konum: {loc.latitude}, {loc.longitude}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=caption)
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo.file_id, caption="📸 Fotoğraf")
    await update.message.reply_text("✅ Tüm bilgiler alındı. Teşekkür ederiz!")
    await show_main_menu(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^🚨 Kaza Bildir$"), begin_report))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("✅ Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
