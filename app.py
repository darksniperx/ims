# app.py
from flask import Flask, request
from bot.bot import setup_bot
import asyncio
import os

app = Flask(__name__)
bot_app = None

# Webhook endpoint for Telegram updates
@app.route('/webhook', methods=['POST'])
async def webhook():
    global bot_app
    if bot_app is None:
        return {"error": "Bot not initialized"}, 500
    update = request.get_json()
    await bot_app.process_update(update)
    return {"status": "ok"}, 200

# Health check endpoint
@app.route('/')
def health():
    return {"status": "Bot is running"}, 200

async def run_bot():
    global bot_app
    bot_app = setup_bot()
    # Set webhook (adjust URL for your Render deployment)
    webhook_url = os.getenv('WEBHOOK_URL', 'https://your-render-app.onrender.com/webhook')
    await bot_app.bot.set_webhook(webhook_url)
    print(f"Webhook set to {webhook_url}")
    # Start the bot
    await bot_app.initialize()
    await bot_app.start()

if __name__ == '__main__':
    # Start the bot in a background task
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    # Run Flask with Gunicorn-compatible WSGI
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
