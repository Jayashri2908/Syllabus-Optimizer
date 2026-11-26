import json
import requests
import time

url = "http://localhost:8000/api/generate"
payload = {
    "course_title": "Machine Learning",
    "course_code": "CS401",
    "credits": "3-1-0",
    "program_outcomes": ["PO1", "PO2"],
    "keywords": ["neural networks", "linear regression", "logistic regression", "decision trees", "random forest", "cnn in machine learning"],
    "domain": "engineering",
    "use_chained_generation": True
}
headers = {
    "Content-Type": "application/json"
}

print("Starting generation...")
start_time = time.time()
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        with open("d:/Syllabus Optimizer/test_result.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Success! Result saved to test_result.json")
    else:
        print("Error:", response.text)
except requests.exceptions.ConnectionError:
    print("Backend is not running on port 8000. Please start the backend.")
print(f"Elapsed: {time.time() - start_time:.2f}s")
