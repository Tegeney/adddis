import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REGISTRATION_NUMBER = os.getenv("REGISTRATION_NUMBER")
FIRST_NAME = os.getenv("FIRST_NAME")

# Debugging: Print environment variables
print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
print("REGISTRATION_NUMBER:", REGISTRATION_NUMBER)
print("FIRST_NAME:", FIRST_NAME)

# Check if environment variables are set
if not TELEGRAM_BOT_TOKEN or not REGISTRATION_NUMBER or not FIRST_NAME:
    print("Missing environment variables.")
    exit(1)

# Define conversation states
REGISTRATION_NUMBER_STATE, FIRST_NAME_STATE = range(2)

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://sw.ministry.et/",
    "Origin": "https://sw.ministry.et",
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
    await update.message.reply_text(
        "Welcome! To fetch student data, please provide your registration number."
    )
    return REGISTRATION_NUMBER_STATE  # Move to the next state

# Handler for registration number input
async def get_registration_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save the registration number
    context.user_data["registration_number"] = update.message.text
    await update.message.reply_text("Thank you! Now, please provide your first name.")
    return FIRST_NAME_STATE  # Move to the next state

# Handler for first name input
async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save the first name
    context.user_data["first_name"] = update.message.text

    # Fetch student data
    registration_number = context.user_data["registration_number"]
    first_name = context.user_data["first_name"]
    student_data = fetch_student_data(registration_number, first_name)

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
                return ConversationHandler.END  # End the conversation
            except requests.exceptions.RequestException as e:
                output += f"\n\nFailed to download the photo: {e}"

        await update.message.reply_text(output, parse_mode="HTML")
    else:
        await update.message.reply_text("No data found or an error occurred.")

    return ConversationHandler.END  # End the conversation

# Handler to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function to run the bot
def main():
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTRATION_NUMBER_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_registration_number)
            ],
            FIRST_NAME_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_first_name)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
