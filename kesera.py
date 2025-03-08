import os
import requests
from flask import Flask

app = Flask(__name__)

# Function to fetch student data
def fetch_student_data(registration_number, first_name):
    url = f"https://sw.ministry.et/student-result/{registration_number}?first_name={first_name}&qr="
    
    # Headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }

    # Make the request
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

@app.route('/')
def home():
    return "Welcome to the Flask Student Info API!"

@app.route('/student/<registration_number>/<first_name>')
def get_student_info(registration_number, first_name):
    student_data = fetch_student_data(registration_number, first_name)
    
    if student_data and "student" in student_data:
        student = student_data["student"]
        return f"""
        <h1>Student Information</h1>
        <p>Name: {student.get('name', 'N/A')}</p>
        <p>Age: {student.get('age', 'N/A')}</p>
        <p>School: {student.get('school', 'N/A')}</p>
        <p>Gender: {student.get('gender', 'N/A')}</p>
        <p>Nationality: {student.get('nationality', 'N/A')}</p>
        <p>Language: {student.get('language', 'N/A')}</p>
        <p>Zone: {student.get('zone', 'N/A')}</p>
        <p>Woreda: {student.get('woreda', 'N/A')}</p>
        """
    else:
        return "No data found or an error occurred."

if __name__ == '__main__':
    # Get the PORT environment variable, default to 5000 if not set
    port = int(os.environ.get("PORT", 5000))
    # Make Flask listen on all available interfaces and the dynamic port
    app.run(host="0.0.0.0", port=port)
