import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Fetch student registration number and first name from environment variables
registration_number = os.getenv("STUDENT_REGISTRATION_NUMBER")
first_name = os.getenv("STUDENT_FIRST_NAME")

# Check if environment variables are set
if not registration_number or not first_name:
    print("Missing environment variables for student data.")
    exit(1)

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://sw.ministry.et/",
    "Origin": "https://sw.ministry.et"
}

# Function to fetch student data
def fetch_student_data(registration_number, first_name):
    url = f"https://sw.ministry.et/student-result/{registration_number}?first_name={first_name}&qr="
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for HTTP errors
        return response.json()  # Parse and return JSON data
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if response is not None:
            print("Response Text:", response.text)  # Debugging info
        return None

# Command handler for /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send a registration number and first name.")

# Handle incoming text messages
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.split(" ")
    if len(text) == 2:
        registration_number, first_name = text
        student_data = fetch_student_data(registration_number, first_name)

        if student_data and "student" in student_data:
            student = student_data["student"]

            response = f"""
            Student Information:
            Name: {student.get("name", "N/A")}
            Age: {student.get("age", "N/A")}
            School: {student.get("school", "N/A")}
            Gender: {student.get("gender", "N/A")}
            Nationality: {student.get("nationality", "N/A")}
            Language: {student.get("language", "N/A")}
            Zone: {student.get("zone", "N/A")}
            Woreda: {student.get("woreda", "N/A")}

            Courses:
            """
            for course in student_data.get("courses", []):
                response += f"- {course.get('name', 'N/A')}\n"

            update.message.reply_text(response)

            # Optionally download the student's photo
            if "photo" in student:
                photo_url = student["photo"]
                try:
                    photo_response = requests.get(photo_url, headers=HEADERS)
                    photo_response.raise_for_status()  # Raise error for bad response
                    with open(f"{first_name}_photo.jpeg", "wb") as f:
                        f.write(photo_response.content)
                    update.message.reply_text("\nPhoto downloaded successfully.")
                except requests.exceptions.RequestException as e:
                    update.message.reply_text("\nFailed to download the photo:", e)
        else:
            update.message.reply_text("No student data found.")
    else:
        update.message.reply_text("Invalid format! Send: `<registration_number> <first_name>`")

# Main function to start the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()  # Use polling instead of webhook
    updater.idle()

# Home route to test Flask app
@app.route('/')
def hello_world():
    return 'Hello, World! Your Flask app is running.'

# Run the Flask app with Gunicorn for production
if __name__ == "__main__":
    main()
