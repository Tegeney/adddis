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

# Fetch student data
student_data = fetch_student_data(registration_number, first_name)

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

    if "courses" in student_data:
        print("\nCourses:")
        for course in student_data["courses"]:
            print("-", course.get("name", "N/A"))

    # Download photo if available
    if "photo" in student:
        photo_url = student["photo"]
        try:
            photo_response = requests.get(photo_url, headers=HEADERS)
            photo_response.raise_for_status()  # Raise error for bad response
            with open(f"{first_name}_photo.jpeg", "wb") as f:
                f.write(photo_response.content)
            print("\nPhoto downloaded successfully.")
        except requests.exceptions.RequestException as e:
            print("\nFailed to download the photo:", e)
else:
    print("No data found or an error occurred.")
