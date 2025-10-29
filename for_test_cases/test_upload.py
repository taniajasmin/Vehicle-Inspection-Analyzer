import requests

url = "http://localhost:8000/analyze"
file_path = r"C:\Users\user\Pictures\Vehicle\Vehicle-Inspection-Report-Template.jpg"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(f"Status: {response.status_code}")
print(response.json())