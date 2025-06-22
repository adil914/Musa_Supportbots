from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import threading
from flask import Flask
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuration ---
BOT_TOKEN = "7330865227:AAFerkaO5qDiQHU-99NgIhPwun4pC6xSpAI"
VIP_LINK = "https://t.me/tradingVerser"
SHEET_NAME = "MusaApprovedTraderIDs"  # Change if your sheet has a different name

# --- Connect to Google Sheets ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("Musa_Supportbots.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# --- Keep track of access ---
user_access = {}

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to TradingVerse Bot!\nPlease enter your Quotex Trader ID.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    trader_id = update.message.text.strip()

    if not trader_id.isdigit():
        await update.message.reply_text("❌ Invalid Trader ID. Please enter only digits.")
        return

    try:
        records = sheet.get_all_records()
        found = False
        for row in records:
            if str(row['Trader ID']) == trader_id and row['Deposit Verified'].strip().upper() == "YES":
                found = True
                break

        if found:
            expire_time = datetime.utcnow() + timedelta(hours=24)
            user_access[user_id] = expire_time
            await update.message.reply_text(
                f"✅ Verified!\n🎁 Here is your VIP group link:\n{VIP_LINK}\n\n"
                f"⚠️ This link will expire in 24 hours."
            )
        else:
            await update.message.reply_text("❌ Sorry, Trader ID not verified or no deposit found.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error checking Google Sheet: {e}")

# --- Keep-Alive Server for Hosting ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is running!"

def run():
    app_web.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()

# --- Start Telegram Bot ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
