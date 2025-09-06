import os
from flask import Flask, request
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, Bot
import pandas as pd
from pymongo import MongoClient
import logging

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
MONGO_URI = os.getenv("MONGO_URI")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 443))

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['bot_db']
fs = db['fs.files']  # GridFS for Excel files

# Load Excel data from MongoDB
def load_excel_data():
    try:
        file_data = fs.find_one({"filename": {"$regex": ".xlsx$"}})
        if file_data:
            with open("temp.xlsx", "wb") as f:
                f.write(file_data.read())
            df = pd.read_excel("temp.xlsx", sheet_name=None)
            return pd.concat(df, ignore_index=True)
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading Excel data: {e}")
        return pd.DataFrame()

df = load_excel_data()

# Health check endpoint
@app.route('/')
def health_check():
    return {"status": "Bot is running"}

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), bot)
    await application.process_update(update)
    return {"status": "ok"}

async def start(update: Update, context):
    await update.message.reply_text("Yo bro! 😎 Welcome to Danger's Bot! Use /search <query> to find data or /help for commands.")

async def help_command(update: Update, context):
    await update.message.reply_text("Commands:\n/search <query> - Search Excel data\n/listexcel - List Excel files\nDanger's Bot 😎")

async def search(update: Update, context):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Bro, give me something to search! 😛")
        return
    results = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().to_string(), axis=1)]
    if results.empty:
        await update.message.reply_text("No results found, bro! 😕")
    else:
        await update.message.reply_text(results.to_json(orient='records', lines=True))

async def list_excel(update: Update, context):
    files = fs.find({"filename": {"$regex": ".xlsx$"}})
    file_list = [f["filename"] for f in files]
    if file_list:
        await update.message.reply_text("Excel files:\n" + "\n".join(file_list))
    else:
        await update.message.reply_text("No Excel files found, bro! 😕")

async def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}")
    if update:
        await update.message.reply_text("Oops, something broke! 😵 Try again, bro.")

def main():
    global application, bot
    bot = Bot(BOT_TOKEN)
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("listexcel", list_excel))
    application.add_error_handler(error_handler)

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
