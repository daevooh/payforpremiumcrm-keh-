import os, time, requests
from dotenv import load_dotenv

load_dotenv()  # reads .env into os.environ

TOKEN = os.getenv("HUBSPOT_API_KEY")
API   = "https://api.hubapi.com"
HEAD  = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
PROP  = "custom_lsp"        # or "hs_lead_status"
BATCH = 50

LIST_TO_STATUS = {
    # Cold / raw
    12: "New_lead",        # cold_lead
    11: "New_lead",        # unconverted_lead

    # Engaging but no deal
    6 : "Interested",      # Top Engager

    # First‑time customers
    5 : "Customer",        # Primi‑Buyer
    2 : "Customer",        # Recent Buyer 30D

    # Big spenders  ➜ Evangelist
    4 : "Evangelist",      # High Spenders / VIP

    # Inactive & churn risk  ➜ Dormant
    7 : "Dormant",         # At‑risk Churner
    10: "Dormant",         # Dormant‑customer
}


def contacts_in_list(list_id):
    """Return all contact IDs in the list (v1 list API)."""
    ids, offset = [], 0
    url = f"{API}/contacts/v1/lists/{list_id}/contacts/all"
    while True:
        params = {"count": 100, **({"vidOffset": offset} if offset else {})}
        resp = requests.get(url, headers=HEAD, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        ids.extend(str(c["vid"]) for c in data.get("contacts", []))
        if not data.get("has-more"):
            break
        offset = data["vid-offset"]
        time.sleep(0.2)
    return ids

def patch_contacts(cids, status):
    """Update ≤BATCH contacts to given status value."""
    url = f"{API}/crm/v3/objects/contacts/batch/update"
    payload = {
        "inputs": [
            {"id": cid, "properties": {PROP: status}}
            for cid in cids
        ]
    }
    resp = requests.post(url, headers=HEAD, json=payload, timeout=15)
    resp.raise_for_status()

def main():
    for list_id, status in LIST_TO_STATUS.items():
        ids = contacts_in_list(list_id)
        print(f"{status}: {len(ids)} contact(s)")
        for i in range(0, len(ids), BATCH):
            patch_contacts(ids[i:i+BATCH], status)
        print(f"✔ Updated to {status}")

if __name__ == "__main__":
    main()
