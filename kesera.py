import os
import requests
import logging
from flask import Flask, request
from dotenv import load_dotenv
import telebot

# Load environment variables from .env file
load_dotenv()

# Get Telegram Bot Token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Error: Missing Telegram BOT_TOKEN in environment variables.")
    exit(1)

# Initialize the Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize Flask App for Webhook
app = Flask(__name__)

# Headers for the student data request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://sw.ministry.et/",
    "Origin": "https://sw.ministry.et",
    "Accept-Language": "en-US,en;q=0.9"
}

# Function to fetch student data
def fetch_student_data(registration_number, first_name):
    url = f"https://sw.ministry.et/student-result/{registration_number}?first_name={first_name}&qr="
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

# Telegram command to start bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me your Registration Number and First Name in this format:\n`1234567 John`")

# Handle student result query
@bot.message_handler(func=lambda message: True)
def get_student_result(message):
    try:
        data = message.text.split()
        if len(data) != 2:
            bot.reply_to(message, "Invalid format! Please send: `1234567 John`")
            return
        
        registration_number, first_name = data
        student_data = fetch_student_data(registration_number, first_name)

        if student_data and "student" in student_data:
            student = student_data["student"]
            response_text = (
                f"📚 *Student Information:*\n"
                f"👤 Name: {student.get('name', 'N/A')}\n"
                f"🎓 School: {student.get('school', 'N/A')}\n"
                f"📌 Zone: {student.get('zone', 'N/A')}\n"
                f"🏫 Woreda: {student.get('woreda', 'N/A')}\n"
            )

            # Send student data
            bot.reply_to(message, response_text, parse_mode="Markdown")

            # Send student photo if available
            if "photo" in student:
                photo_url = student["photo"]
                bot.send_photo(message.chat.id, photo_url)
        else:
            bot.reply_to(message, "No student data found.")
    except Exception as e:
        logging.error(f"Error: {e}")
        bot.reply_to(message, "An error occurred while fetching student data.")

# Flask route for webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return "OK", 200

# Start the bot in polling mode
if __name__ == "__main__":
    logging.info("Starting bot...")
    app.run(host="0.0.0.0", port=5000, debug=True)
