import requests
import os
from dotenv import load_dotenv


load_dotenv()
ACCESS_TOKEN = os.getenv("HUBSPOT_API_KEY")

def fetch_and_sort_list():
    url = f'https://api.hubapi.com/contacts/v1/lists'
    headers = {
        'Authorization' : f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        lists = response.json().get('lists',[])
        sorted_lists = sorted(lists, key=lambda x: x['name'])
        return sorted_lists
    else:
        print("failed to fetch lists:", response.text)
        return []
    
def main():
    lists = fetch_and_sort_list()
    if lists:
        print("\nAvailable Hubspot Lists (sorted by name):")
        sorted_lists = sorted(lists, key=lambda l: l.get("name", ""))
        for lst in sorted_lists:
            print(f"List ID: {lst['listId']}, Name: {lst['name']}")
    else:
        print("No lists found.")
if __name__ == "__main__":
    main()

