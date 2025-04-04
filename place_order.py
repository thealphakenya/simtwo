import json
import requests

# Define the API endpoint
api_url = "http://127.0.0.1:5000/api/place_order"

# Request Data
request_data = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.1
}

# Save Request Data to File
with open('request_data.json', 'w') as file:
    json.dump(request_data, file, indent=4)

# Send POST request
headers = {'Content-Type': 'application/json'}
try:
    response = requests.post(api_url, json=request_data, headers=headers)
    
    # Check if the response is successful
    if response.status_code == 200:
        response_data = response.json()
        with open('response.json', 'w') as file:
            json.dump(response_data, file, indent=4)
        print("Response saved successfully.")
    else:
        print(f"Error: {response.status_code}, {response.text}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
