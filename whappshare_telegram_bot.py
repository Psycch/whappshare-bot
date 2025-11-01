# whappshare_telegram_bot.py

"""
WhappShare Official Telegram Bot
---------------------------------
Features:
1️⃣ Register (asks DOB & country, then redirects)
2️⃣ Become Agent (asks DOB & redirects)
3️⃣ Exchange USDT (asks DOB, Mobile, UPI, then redirects)
4️⃣ Become Payment Partner (redirects)
5️⃣ Contact Support (redirects)

Setup & Run:
- pip install python-telegram-bot==20.5
- Run: python whappshare_telegram_bot.py
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import logging

# ✅ Your bot token here (keep it private)
TOKEN = "8127465132:AAEN2ElXPw4iqg8KpoWETPa_Vqyz3LGuMwA"

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Temporary user data storage
user_data = {}

# === Start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1️⃣ Register", callback_data="register")],
        [InlineKeyboardButton("2️⃣ Become Agent", callback_data="agent")],
        [InlineKeyboardButton("3️⃣ Exchange USDT", callback_data="exchange")],
        [InlineKeyboardButton("4️⃣ Become Payment Partner", callback_data="partner")],
        [InlineKeyboardButton("5️⃣ Contact Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome to *WhappShare Official Bot!*\nPlease choose an option below 👇", reply_markup=reply_markup, parse_mode="Markdown")


# === Handle button presses ===
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id

    if data == "register":
        await query.edit_message_text("📅 Please enter your *Date of Birth* (DD-MM-YYYY):", parse_mode="Markdown")
        user_data[chat_id] = {"step": "dob_register"}

    elif data == "agent":
        await query.edit_message_text("📅 Please enter your *Date of Birth*:", parse_mode="Markdown")
        user_data[chat_id] = {"step": "dob_agent"}

    elif data == "exchange":
        await query.edit_message_text("📅 Enter your *Date of Birth*:", parse_mode="Markdown")
        user_data[chat_id] = {"step": "dob_exchange"}

    elif data == "partner":
        await query.edit_message_text("🤝 Redirecting you to Payment Partner team...")
        await query.message.reply_text("👉 Contact us at @wsgcsaler")

    elif data == "support":
        await query.edit_message_text("📞 Redirecting to Support Team...")
        await query.message.reply_text("👉 Contact @wsgcsaler for help")


# === Handle text replies ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        await update.message.reply_text("Please use /start to begin.")
        return

    step = user_data[chat_id].get("step")

    # 1️⃣ Register flow
    if step == "dob_register":
        user_data[chat_id]["dob"] = text
        user_data[chat_id]["step"] = "country_register"
        await update.message.reply_text("🌍 Enter your *Country Name*:", parse_mode="Markdown")

    elif step == "country_register":
        user_data[chat_id]["country"] = text
        await update.message.reply_text(
            "✅ Registration Complete!\n🔗 Click below to continue:\nhttps://whappshare.com/?code=20KfAl7PS1k\n\n👉 You’ll be redirected to @wsgcsaler",
            parse_mode="Markdown",
        )
        await update.message.reply_text("Contact: @wsgcsaler")
        user_data.pop(chat_id)

    # 2️⃣ Agent flow
    elif step == "dob_agent":
        await update.message.reply_text(
            "✅ Thank you! You’ll now be redirected to our Agent team.\nContact 👉 @wsgcsaler",
            parse_mode="Markdown",
        )
        user_data.pop(chat_id)

    # 3️⃣ Exchange flow
    elif step == "dob_exchange":
        user_data[chat_id]["dob"] = text
        user_data[chat_id]["step"] = "mobile_exchange"
        await update.message.reply_text("📱 Please enter your *Mobile Number*:", parse_mode="Markdown")

    elif step == "mobile_exchange":
        user_data[chat_id]["mobile"] = text
        user_data[chat_id]["step"] = "upi_exchange"
        await update.message.reply_text("💳 Enter your *UPI ID*:", parse_mode="Markdown")

    elif step == "upi_exchange":
        user_data[chat_id]["upi"] = text
        await update.message.reply_text(
            "✅ Exchange request received!\nOur team will contact you shortly.\n👉 Contact @wsgcsaler",
            parse_mode="Markdown",
        )
        user_data.pop(chat_id)


# === Main function ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
