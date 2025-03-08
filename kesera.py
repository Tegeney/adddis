import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch student registration number and first name from environment variables
registration_number = os.getenv("STUDENT_REGISTRATION_NUMBER")
first_name = os.getenv("STUDENT_FIRST_NAME")

# Check if environment variables are set
if not registration_number or not first_name:
    print("Missing environment variables for student data.")
    exit(1)

# Updated Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://sw.ministry.et/",
    "Origin": "https://sw.ministry.et",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

# Function to create a session (for handling cookies)
def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Visit the main page to establish a session
    try:
        session.get("https://sw.ministry.et/", timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Failed to establish session: {e}")
        return None
    return session

# Function to fetch student data
def fetch_student_data(session, registration_number, first_name):
    url = f"https://sw.ministry.et/student-result/{registration_number}?first_name={first_name}&qr="
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Raise error for HTTP failures
        
        # Check if response is JSON
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()  
        else:
            print("Unexpected response format:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Create a session
session = create_session()
if not session:
    print("Failed to initialize session.")
    exit(1)

# Fetch student data
student_data = fetch_student_data(session, registration_number, first_name)

# Display student data if available
if student_data and "student" in student_data:
    student = student_data["student"]
    
    print("\nStudent Information:")
    print("Name:", student.get("name", "N/A"))
    print("Age:", student.get("age", "N/A"))
    print("School:", student.get("school", "N/A"))
    print("Gender:", student.get("gender", "N/A"))
    print("Nationality:", student.get("nationality", "N/A"))
    print("Language:", student.get("language", "N/A"))
    print("Zone:", student.get("zone", "N/A"))
    print("Woreda:", student.get("woreda", "N/A"))

    # Display courses if available
    if "courses" in student_data:
        print("\nCourses:")
        for course in student_data["courses"]:
            print("-", course.get("name", "N/A"))

    # Download student photo if available
    if "photo" in student:
        photo_url = student["photo"]
        try:
            photo_response = session.get(photo_url, timeout=10)
            photo_response.raise_for_status()
            with open(f"{first_name}_photo.jpeg", "wb") as f:
                f.write(photo_response.content)
            print("\nPhoto downloaded successfully.")
        except requests.exceptions.RequestException as e:
            print("\nFailed to download the photo:", e)
else:
    print("No data found or an error occurred.")
