import os
import requests
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

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
        return None

# Define the route for the Flask app
@app.route('/')
def home():
    # Fetch student data
    student_data = fetch_student_data(registration_number, first_name)

    if student_data and "student" in student_data:
        student = student_data["student"]
        output = f"""
        <h1>Student Information:</h1>
        <p>Name: {student.get("name", "N/A")}</p>
        <p>Age: {student.get("age", "N/A")}</p>
        <p>School: {student.get("school", "N/A")}</p>
        <p>Gender: {student.get("gender", "N/A")}</p>
        <p>Nationality: {student.get("nationality", "N/A")}</p>
        <p>Language: {student.get("language", "N/A")}</p>
        <p>Zone: {student.get("zone", "N/A")}</p>
        <p>Woreda: {student.get("woreda", "N/A")}</p>
        """
        
        if "courses" in student_data:
            output += "<h2>Courses:</h2><ul>"
            for course in student_data["courses"]:
                output += f"<li>{course.get('name', 'N/A')}</li>"
            output += "</ul>"

        # Optionally download the photo
        if "photo" in student:
            photo_url = student["photo"]
            try:
                photo_response = requests.get(photo_url, headers=HEADERS)
                photo_response.raise_for_status()  # Raise error for bad response
                output += f"<p>Photo downloaded successfully: {photo_url}</p>"
            except requests.exceptions.RequestException as e:
                output += f"<p>Failed to download the photo: {e}</p>"
        return output
    else:
        return "No data found or an error occurred."

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
