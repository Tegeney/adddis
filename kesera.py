import os
import requests
from PIL import Image
from io import BytesIO

def fetch_student_data(registration_number, first_name):
    # Construct the URL for fetching student data
    url = f"https://sw.ministry.et/student-result/{registration_number}?first_name={first_name}&qr="
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sw.ministry.et/",
        "Origin": "https://sw.ministry.et",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # Make the GET request to fetch data
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (403, 404, etc.)
        
        data = response.json()  # Parse JSON data
        return data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Text: {response.text}")  # Print server's response for debugging
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print("Failed to parse JSON response.")
        return None

def display_photo(photo_url):
    try:
        # Download the image
        response = requests.get(photo_url)
        response.raise_for_status()  # Check if the image download was successful
        image = Image.open(BytesIO(response.content))
        image.show()  # Display the image
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the photo: {e}")
    except IOError:
        print("Failed to open the image file.")

# Fetch student registration number and first name from environment variables
registration_number = os.getenv("STUDENT_REGISTRATION_NUMBER")
first_name = os.getenv("STUDENT_FIRST_NAME")

# Check if environment variables are set
if not registration_number or not first_name:
    print("Missing environment variables for student data.")
    exit(1)

# Fetch and display student data
student_data = fetch_student_data(registration_number, first_name)

if student_data:
    # Check if 'student' data exists
    if "student" in student_data:
        student = student_data["student"]
        # Display the student's photo if available
        if "photo" in student:
            display_photo(student["photo"])
        
        # Display student details
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
        else:
            print("\nNo courses found.")
    else:
        print("No student data found.")
else:
    print("No data found or an error occurred.")
