import json
import requests
from dotenv import load_dotenv
import os
import pywhatkit
import time
from datetime import datetime, timedelta


# Load the message library
# def load_message_library():
#     return [
#         {
#             "category": "Football",
#             "lead_status": "New",
#             "customer_type": "prospect",
#             "text": "Hey {name}, check out our latest football collection! 🏈 Get 10% off on your first purchase.",
#             "image_url": "https://example.com/images/football.jpg",
#             "cta_link": "https://instagram.com/yourpage"
#         },
#         {
#             "category": "Football",
#             "lead_status": "Customer",
#             "customer_type": "existing",
#             "text": "Hey {name}, missing you! Here's 15% off on our new football gear just for our valued customers! ⚽",
#             "image_url": "https://example.com/images/football_premium.jpg",
#             "cta_link": "https://instagram.com/yourpage"
#         },
#         {
#             "category": "Random",
#             "lead_status": "New",
#             "customer_type": "prospect",
#             "text": "Hey {name}, discover our trending products! 🌟 Special offer for new customers.",
#             "image_url": "https://example.com/images/random.jpg",
#             "cta_link": "https://instagram.com/yourpage"
#         }
#     ]

# # Test the function
# if __name__ == "__main__":
#     messages = load_message_library()
#     for message in messages:
#         print("PASSED")


# Load environment variables from .env file
load_dotenv()

# HubSpot API configuration
API_KEY = os.getenv("HUBSPOT_API_KEY")
BASE_URL = "https://api.hubapi.com"

# Function to fetch contacts
def fetch_hubspot_contacts():
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "properties": "Custom_LSP",
        "limit": 100,  # Fetch up to 100 contacts per request
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        for contact in data['results']:
            custom_lsp = contact['properties'].get('custom_lsp')
            if custom_lsp:
                print(f"hs_object_id: {contact['id']}, custom_lsp: {custom_lsp}")
        response.raise_for_status()
        data = response.json()
        contacts = data.get("results", [])
        return contacts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contacts: {e}")
        return []
        # Iterate through the results and print only the custom_lsp values

print(fetch_hubspot_contacts())



