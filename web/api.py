import requests
import os
from dotenv import load_dotenv

class MyTravels:
    def __init__(self):
        """Initialize API URL from environment variables"""
        load_dotenv()
        

    def book_ticket(self, name, phone, source, destination, date):
        """Send a booking request to the API"""
        self.booking_url = os.getenv("BOOKING_API_URL")
        payload = {
            "name": name,
            "phone": phone,
            "from": source,
            "to": destination,
            "date": date
        }

        response = requests.post(self.booking_url, json=payload)

        if response.status_code == 200:
            try:
                return {"status": "success", "response": response.json()}
            except requests.exceptions.JSONDecodeError:
                return {"status": "error", "message": "Empty response from server"}
        else:
            return {"status": "error", "code": response.status_code, "message": response.text}


