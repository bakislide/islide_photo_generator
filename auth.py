# auth.py
from flask import request, jsonify

# Your API key from Google Cloud
API_KEY = 'AIzaSyDZRrBDuzanhs8POcx4SIfQwkyk4nSDTD0'

def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.args.get('key')
        print(f"Received API key: {key}")  # Debugging statement
        if key and key == API_KEY:
            return func(*args, **kwargs)
        else:
            print("Invalid or missing API key")  # Debugging statement
            response = jsonify({'error': 'Invalid or missing API key'})
            response.status_code = 403
            return response
    return wrapper
