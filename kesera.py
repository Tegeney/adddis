import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STUDENT_REGISTRATION_NUMBER = os.getenv("STUDENT_REGISTRATION_NUMBER")
STUDENT_FIRST_NAME = os.getenv("STUDENT_FIRST_NAME")

# Check if environment variables are set
if not TELEGRAM_BOT_TOKEN or not STUDENT_REGISTRATION_NUMBER or not STUDENT_FIRST_NAME:
    print("Missing environment variables.")
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
        return None

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /student to fetch student data.")

# Command handler for /student
async def student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch student data
    student_data = fetch_student_data(STUDENT_REGISTRATION_NUMBER, STUDENT_FIRST_NAME)

    if student_data and "student" in student_data:
        student = student_data["student"]
        output = f"""
        <b>Student Information:</b>
        Name: {student.get("name", "N/A")}
        Age: {student.get("age", "N/A")}
        School: {student.get("school", "N/A")}
        Gender: {student.get("gender", "N/A")}
        Nationality: {student.get("nationality", "N/A")}
        Language: {student.get("language", "N/A")}
        Zone: {student.get("zone", "N/A")}
        Woreda: {student.get("woreda", "N/A")}
        """
        
        if "courses" in student_data:
            output += "\n\n<b>Courses:</b>"
            for course in student_data["courses"]:
                output += f"\n- {course.get('name', 'N/A')}"

        # Optionally download the photo
        if "photo" in student:
            photo_url = student["photo"]
            try:
                photo_response = requests.get(photo_url, headers=HEADERS)
                photo_response.raise_for_status()  # Raise error for bad response
                await update.message.reply_photo(photo_url, caption=output, parse_mode="HTML")
                return
            except requests.exceptions.RequestException as e:
                output += f"\n\nFailed to download the photo: {e}"
        
        await update.message.reply_text(output, parse_mode="HTML")
    else:
        await update.message.reply_text("No data found or an error occurred.")

# Main function to run the bot
def main():
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("student", student))

    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
