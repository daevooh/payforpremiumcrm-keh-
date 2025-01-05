import json
import requests
from dotenv import load_dotenv
import os


# Load the message library
def load_message_library():
    return [
        {
            "category": "Football",
            "lead_status": "New",
            "text": "Hey {name}, check out our latest football collection!",
            "image_url": "https://example.com/images/football.jpg",
            "cta_link": "https://instagram.com/yourpage"
        },
        {
            "category": "Random",
            "lead_status": "New",
            "text": "Hey {name}, discover something new today!",
            "image_url": "https://example.com/images/random.jpg",
            "cta_link": "https://instagram.com/yourpage"
        }
    ]

# Test the function
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
        "properties": "firstname,lastname,email,phone,fav_product_type",
        "limit": 100,  # Fetch up to 100 contacts per request
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        contacts = data.get("results", [])
        return contacts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contacts: {e}")
        return []

# Function to fetch leads
def fetch_hubspot_leads():
    url = f"{BASE_URL}/crm/v3/objects/leads"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "properties": "hs_lead_status,hs_lifecyclestage",  # Specify the required fields
        "limit": 100,  # Fetch up to 100 leads per request
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        leads = data.get("results", [])
        return leads
    except requests.exceptions.RequestException as e:
        print(f"Error fetching leads: {e}")
        return []

# Function to print contacts
def print_contacts(contacts):
    if contacts:
        print("Fetched contacts successfully!")
        for contact in contacts:
            firstname = contact.get('properties', {}).get('firstname', 'N/A')
            lastname = contact.get('properties', {}).get('lastname', 'N/A')
            email = contact.get('properties', {}).get('email', 'N/A')
            phone = contact.get('properties', {}).get('phone', 'N/A')
            fav_product_type = contact.get('properties', {}).get('fav_product_type', 'N/A')

            print(f"Name: {firstname} {lastname}")
            print(f"Email: {email}")
            print(f"Phone: {phone}")
            print(f"Favorite Product: {fav_product_type}")
            print("-" * 50)
    else:
        print("No contacts retrieved.")

# Function to print leads
def print_leads(leads):
    if leads:
        print("Fetched leads successfully!")
        for lead in leads:
            # Check if lead status and lifecycle stage are available
            lead_status = lead.get('properties', {}).get('hs_lead_status', 'N/A')
            lifecycle_stage = lead.get('properties', {}).get('hs_lifecyclestage', 'N/A')

            # Print the lead details
            print(f"Lead Status: {lead_status}")
            print(f"Lifecycle Stage: {lifecycle_stage}")
            print("-" * 50)
    else:
        print("No leads retrieved.")

# Example usage
if __name__ == "__main__":
    # Fetch and print contacts
    contacts = fetch_hubspot_contacts()
    print_contacts(contacts)

    # Fetch and print leads
    leads = fetch_hubspot_leads()
    print_leads(leads)