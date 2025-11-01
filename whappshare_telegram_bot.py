# ======================================================
#   WHAPPSHARE TELEGRAM BOT WITH CSV DATA STORAGE
#   Collects DOB, Country, Mobile, UPI and saves to CSV
#   /getcsv command lets admin download the data
# ======================================================

import os
import csv
from datetime import datetime
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================================================
#   CONFIGURATION
# ======================================================
TOKEN = "8127465132:AAEN2ElXPw4iqg8KpoWETPa_Vqyz3LGuMwA"  # Your Bot Token
ADMIN_ID = 8256734015  # Replace with your Telegram numeric ID (from @userinfobot)
CSV_FILE = "whappshare_users.csv"

# ======================================================
#   CSV HELPER FUNCTION
# ======================================================
def save_user_data(reg_type, user_id, username, name, dob=None, country=None, mobile=None, upi=None):
    """Append user data to CSV file."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Reg Type", "User ID", "Username", "Name",
                "DOB", "Country", "Mobile", "UPI", "Timestamp"
            ])
        writer.writerow([
            reg_type, user_id, username or "", name or "",
            dob or "", country or "", mobile or "",
            upi or "", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ])

# ======================================================
#   BOT HANDLERS
# ======================================================
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1️⃣ Register", callback_data="register")],
        [InlineKeyboardButton("2️⃣ Become an Agent", callback_data="agent")],
        [InlineKeyboardButton("3️⃣ Exchange USDT", callback_data="exchange")],
        [InlineKeyboardButton("4️⃣ Become a Payment Partner", callback_data="partner")],
        [InlineKeyboardButton("5️⃣ Contact Support Team", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to *WhappShare Official Bot!*\n\nChoose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    chat_id = query.message.chat_id

    user_data[chat_id] = {"step": choice}
    if choice == "register":
        await query.message.reply_text("📅 Enter your Date of Birth (DD-MM-YYYY):")
    elif choice == "agent":
        await query.message.reply_text("📅 Enter your DOB to become an Agent:")
    elif choice == "exchange":
        await query.message.reply_text("📅 Enter your DOB to Exchange USDT:")
    elif choice == "partner":
        await query.message.reply_text("📅 Enter your DOB to become a Payment Partner:")
    elif choice == "support":
        await query.message.reply_text("💬 Contact our Support Team at 👉 @wsgcsaler")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    step_info = user_data.get(chat_id)
    if not step_info:
        return

    step = step_info.get("step")
    user = update.effective_user

    # --- Registration Flow ---
    if step == "register":
        user_data[chat_id]["dob"] = text
        user_data[chat_id]["step"] = "country_register"
        await update.message.reply_text("🌍 Enter your Country Name:")

    elif step == "country_register":
        user_data[chat_id]["country"] = text
        # Save data to CSV
        save_user_data(
            "register",
            user.id,
            user.username,
            user.full_name,
            dob=user_data[chat_id].get("dob"),
            country=user_data[chat_id].get("country"),
        )
        await update.message.reply_text(
            "✅ Registration Complete!\n🔗 Click below to continue:\nhttps://whappshare.com/?code=20KfAl7PS1k\n\n👉 You’ll be redirected to @wsgcsaler"
        )
        await update.message.reply_text("Contact: @wsgcsaler")
        user_data.pop(chat_id)

    # --- Exchange Flow ---
    elif step == "exchange":
        user_data[chat_id]["dob"] = text
        user_data[chat_id]["step"] = "mobile_exchange"
        await update.message.reply_text("📱 Enter your Mobile Number:")

    elif step == "mobile_exchange":
        user_data[chat_id]["mobile"] = text
        user_data[chat_id]["step"] = "upi_exchange"
        await update.message.reply_text("💰 Enter your UPI ID:")

    elif step == "upi_exchange":
        user_data[chat_id]["upi"] = text
        save_user_data(
            "exchange",
            user.id,
            user.username,
            user.full_name,
            dob=user_data[chat_id].get("dob"),
            mobile=user_data[chat_id].get("mobile"),
            upi=user_data[chat_id].get("upi"),
        )
        await update.message.reply_text(
            "✅ Exchange Request Received!\nOur team will contact you shortly.\n👉 Contact @wsgcsaler"
        )
        user_data.pop(chat_id)

    # --- Agent / Partner ---
    elif step in ["agent", "partner"]:
        user_data[chat_id]["dob"] = text
        save_user_data(
            step,
            user.id,
            user.username,
            user.full_name,
            dob=user_data[chat_id].get("dob"),
        )
        await update.message.reply_text(
            f"✅ {step.title()} details received!\nOur team will reach out soon.\n👉 Contact @wsgcsaler"
        )
        user_data.pop(chat_id)

# ======================================================
#   /GETCSV COMMAND
# ======================================================
async def get_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Access Denied. Admins only.")
        return

    if os.path.exists(CSV_FILE):
        await update.message.reply_document(
            document=open(CSV_FILE, "rb"),
            caption=f"📊 WhappShare User Data — {datetime.now().strftime('%d %b %Y, %H:%M')}"
        )
    else:
        await update.message.reply_text("⚠️ No data found yet!")

# ======================================================
#   MAIN FUNCTION
# ======================================================
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getcsv", get_csv))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 WhappShare Bot started successfully...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
