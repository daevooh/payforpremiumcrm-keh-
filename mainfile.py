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
# Function to fetch leads
# def fetch_hubspot_leads():
#     url = f"{BASE_URL}/crm/v3/objects/leads/batch/read"
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json",
#     }
#     # params = {
#     #     "properties": "hs_lead_status,hs_lifecyclestage",  # Specify the required fields
#     #     "limit": 100,  # Fetch up to 100 leads per request
#     # }
#     try:
#         response = requests.get(url, headers=headers)
#         print(f"Status Code: {response.status_code}")
#         if response.status_code == 200:
#             print("URL is reachable and returning 200 OK.")
#         else:
#             print(f"URL returned {response.status_code}: {response.reason}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error testing URL: {e}")

# if __name__ == "__main__":
#     fetch_hubspot_leads()

# # Function to print contactsls
# def print_contacts(contacts):
#     if contacts:
#         print("Fetched contacts successfully!")
#         for contact in contacts:
#             firstname = contact.get('properties', {}).get('firstname', 'N/A')
#             lastname = contact.get('properties', {}).get('lastname', 'N/A')
#             email = contact.get('properties', {}).get('email', 'N/A')
#             phone = contact.get('properties', {}).get('phone', 'N/A')
#             fav_product_type = contact.get('properties', {}).get('fav_product_type', 'N/A')

#             print(f"Name: {firstname} {lastname}")
#             print(f"Email: {email}")
#             print(f"Phone: {phone}")
#             print(f"Favorite Product: {fav_product_type}")
#             print("-" * 50)
#     else:
#         print("No contacts retrieved.")

# # Function to print leads
# def print_leads(leads):
    # if leads:
    #     print("Fetched leads successfully!")
    #     for lead in leads:
    #         # Check if lead status and lifecycle stage are available
    #         lead_status = lead.get('properties', {}).get('hs_lead_status', 'N/A')
    #         lifecycle_stage = lead.get('properties', {}).get('hs_lifecyclestage', 'N/A')

    #         # Print the lead details
    #         print(f"Lead Status: {lead_status}")
    #         print(f"Lifecycle Stage: {lifecycle_stage}")
    #         print("-" * 50)
    # else:
    #     print("No leads retrieved.")

# # Function to select appropriate message for a contact
# def select_message(contact, message_library):
#     fav_product = contact.get('properties', {}).get('fav_product_type', 'Random')
#     lead_status = contact.get('properties', {}).get('hs_lead_status', 'New')
    
#     # Find matching message
#     matching_messages = [
#         msg for msg in message_library 
#         if msg['category'] == fav_product and msg['lead_status'] == lead_status
#     ]
    
#     # Return first matching message or default to Random category
#     return matching_messages[0] if matching_messages else next(
#         (msg for msg in message_library if msg['category'] == 'Random'),
#         None
#     )

# # Function to send WhatsApp message
# def send_whatsapp_message(phone_number, message, image_url=None):
#     try:
#         # Format phone number (remove '+' and any spaces)
#         formatted_phone = ''.join(filter(str.isdigit, phone_number))
        
#         # Get current time + 2 minutes (to allow WhatsApp Web to load)
#         now = datetime.now() + timedelta(minutes=2)
        
#         # Send message
#         pywhatkit.sendwhatmsg(
#             phone_no=formatted_phone,
#             message=message,
#             time_hour=now.hour,
#             time_min=now.minute,
#             wait_time=20,  # Seconds to wait for WhatsApp Web to load
#             tab_close=True
#         )
        
#         # If there's an image, send it (Note: This would require additional setup)
#         if image_url:
#             # TODO: Implement image sending functionality
#             pass
            
#         return True
#     except Exception as e:
#         print(f"Error sending WhatsApp message: {e}")
#         return False

# # Function to process contacts and send messages
# def process_contacts_and_send_messages(contacts):
#     message_library = load_message_library()
#     results = []
    
#     for contact in contacts:
#         # Get contact details
#         firstname = contact.get('properties', {}).get('firstname', '')
#         phone = contact.get('properties', {}).get('phone', '')
        
#         if not phone:  # Skip if no phone number
#             continue
            
#         # Select appropriate message
#         message_template = select_message(contact, message_library)
#         if not message_template:
#             continue
            
#         # Personalize message
#         message = message_template['text'].format(name=firstname)
        
#         # Send message
#         success = send_whatsapp_message(
#             phone,
#             message,
#             message_template.get('image_url')
#         )
        
#         results.append({
#             'contact': f"{firstname} ({phone})",
#             'message': message,
#             'success': success
#         })
        
#         # Wait between messages to avoid flooding
#         time.sleep(10)
    
#     return results

# # Update main execution
# if __name__ == "__main__":
    # Fetch contacts
    # contacts = fetch_hubspot_contacts()
    
    # # Process and send messages
    # results = process_contacts_and_send_messages(contacts)
    
    # # Print results
    # for result in results:
    #     print(f"Sent to: {result['contact']}")
    #     print(f"Message: {result['message']}")
    #     print(f"Success: {'✓' if result['success'] else '✗'}")
    #     print("-" * 50)
