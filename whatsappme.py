#!/usr/bin/env python3
import os, time, csv, pathlib, datetime, requests
import json, random,webbrowser, sys
from typing import Dict, List
from dotenv import load_dotenv
from daily_content import DAILY_DIGEST
from pathlib import path
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
PROFILE = r"C:\Users\kingdavid\selenium_profile"

command = f'"{CHROME}" --user-data-dir="{PROFILE}" %s'

class ChromeProfile(webbrowser.BackgroundBrowser):
    def __init__(self):
        super().__init__(command)
webbrowser.register("chrome_profile", ChromeProfile)
os.environ["BROWSER"]= "chrome_profile"
import pywhatkit as kit 
# with open("saved_numbers.json") as f:
#     SAVED_CONTACTS = json.load(f)
# leaving the saved messge functions for now as the selenium buils is taking quite a while
load_dotenv()

TOKEN = os.getenv("HUBSPOT_API_KEY")
API = "https://api.hubapi.com"
HEAD = {"Authorization": f"Bearer {TOKEN}", "Content-Type":"application/json"}

MAX_FREQ_DAYS = 0 # Maximum days between messages

LOG_FILE = pathlib.Path(__file__).parent / "log.csv"
BATCH_LIST = 100
# Keep track of contacts we already processed in this run
already_sent: set[str] = set()
#----------------------------------------------------------
SAVE_PROMPT = (
    "📲 Please save *24Brand* in your contacts so you "
    "never miss new drops, match updates and highlight, and pro tips! \n\n"
)

FALLBACK_NAMES = ["Champ"]
DEFAULT_PRODUCT = "our Latest Sports Gear"
GENERIC_FINETUNE = "🔥  Fresh arrival just dropped"
TEMPLATES: Dict[str, str] = {
    "New_lead->cold_lead":       "Hi {first} {last}, we miss you. Here's 10% off {product}: {link}",
    "New_lead->unconverted_lead": "Hey {first} {last}, your {product} is still waiting. Grab it now: {link}",

    "Interested": "Hey {first} {last}, still thinking about {product}? We’re here to help 👉 {link}",

    "Customer->primi_buyer":      "Hi {first} {last}, congrats on your first {product}! 🎉 Need help with the next pick?",
    "Customer->recent_buyer30D":  "Hi {first} {last}, thanks again for your {product} purchase! Let us know if you need more.",

    "Evangelist": "Hi {first} {last}! You’ve been amazing 🙌. Check out what’s new in {product}: {link}",
    "cooling_buyers": "Hey {first} {last}! Still loving your {product}? Here's something fresh:{link}",
    "Dormant->At-rik_churner":  "Hi {first} {last},we noticed you've been quiet. Want to reconnect over {product}? {link}",
    "Dormant->Dormant_customer": "Hey {first} {last}, we've got something special to bring you back: {link}",
}
PRODUCT_FINETUNE ={
    "Jersey" :"⚽️ New jersey drops are live—pick your favourite club!",
    "Football boot": "🔥 Ready to level‑up? Fresh boots await.",
    "Gym": "💪 Time to smash goals—grab the latest gym gear!",
}
DAILY_UPDATE = {

}
LIST_TO_STATUS = {
    # Cold / raw
    12: "New_lead->cold_lead",        # cold_lead
    11: "New_lead->unconverted_lead",        # unconverted_lead

    # Engaging but no deal
    6 : "Interested",      # Top Engager

    # First‑time customers
    5 : "Customer->primi_buyer",        # Primi‑Buyer
    2 : "Customer->recent_buyer30D",        # Recent Buyer 30D

    # Big spenders  ➜ Evangelist
    4 : "Evangelist",      # High Spenders / VIP

    # Inactive & churn risk  ➜ Dormant
    7 : "Dormant->At-rik_churner",         # At‑risk Churner
    10: "Dormant->dormant_customer",         # Dormant‑customer
}
SEGMENT_PRIORITY = [
    "Evangelist",
    "Customer->recent_buyer30D",
    "Customer->primi_buyer",
    "Interested",
    "Dormant->At-rik_churner",
    "Dormant->dormant_customer",
    "New_lead->cold_lead",
    "New_lead->unconverted_lead",
]

#----- helper functions -----------
def contacts_in_list(list_id: int) -> List[str]:
    """ Return all the cotacts IDs in the list (v1 list API)."""
    ids, offset = [], 0
    url = f"{API}/contacts/v1/lists/{list_id}/contacts/all"
    while True:
        params = {"count": BATCH_LIST, **({"vidOffset": offset} if offset else {})}
        r = requests.get(url, headers=HEAD, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        ids.extend(str(c["vid"]) for c in data.get("contacts", []))
        print(f"   ↳ pulled {len(ids)} contacts from list {list_id}")
        if not data.get("has-more"):
            break
        offset = data["vid-offset"]
        time.sleep(0.2)
    return ids
def get_contact_prop(cid: str) -> Dict[str, str]:
    url = f"{API}/crm/v3/objects/contacts/{cid}"
    r = requests.get(
        url, headers=HEAD,
        params={"properties":"firstname,lastname,phone,product_type,last_wa_sent"},
        timeout=15
    )
    r.raise_for_status()
    p = r.json()["properties"]
    return {
        "first": p.get("firstname") or "",
        "last": p.get("lastname") or "",
        "phone": p.get("phone") or "",
        "product": p.get("product_type") or "Your Sport Gear",
        "last_wa": p.get("last_wa_sent") or "",
    }
def human_name(first: str, last: str) -> str:
    if first:
        return f"{first} {last}".strip()
    return random.choice(FALLBACK_NAMES)

def build_msg(segment: str, props: Dict[str, str]) -> str:
    # needs_prompt = not SAVED_CONTACTS.get(props["phone"], False)
    name = human_name(props.get("first", ""), props.get("last", ""))
    product = props.get("product",) or DEFAULT_PRODUCT
    props["product"] = product
    template = TEMPLATES[segment]
    body = template.format(name=name, **props)
    finetune = PRODUCT_FINETUNE.get(product, GENERIC_FINETUNE)
    body = body.replace("{link}", f"{finetune} {props['link']}")

    # if needs_prompt:
    #     return SAVE_PROMPT.format(first=props["first"], last=props["last"]) + base_line
    return body
# ------------------------- build daily message -------------------
def grab_one(lst):
    return random.choice(lst) if lst else ""
def build_daily_message(contact: dict) -> str:
    """ 
    contact = {
        "first": .....,"last": ...., "fav_product": "football", "link": catalogue_link
        }
    """
    name = human_name(contact["first"], contact["last"])
    main = contact.get("fav_product", "football").lower()
    parts = []
    # generic greeting
    parts.append(f"Good Morning, {name}! Here's today's sports pulse:\n")
    core = DAILY_DIGEST.get(main,{})
    if core:
        parts.append(f"*{main.title()} Highlights* 🎞️")
        parts.extend(grab_one(core.get("highlights", [])) for _ in range(1))
        parts.append(f"*{main.title()} memes* 😂 {grab_one(core.get('meme', []))}")
        if core.get("fixtures"):
            parts.append("*Today's Fixtures* 📅")
            for f in core["fixtures"][:3]:
                parts.append(f"• {f['title']} – {f['stream']}")
        parts.append("")
    for sport in ("basketball", "gym"):
        if sport == main:
            continue
        mini = DAILY_DIGEST.get(sport, {})
        if not mini:
            continue
        if sport == "gym":
            parts.append(f"🧵 *Gym Tip:* {grab_one(mini.get('tips', []))}")
        else:
            parts.append(f"🏀 Quick {sport.title()}: {grab_one(mini.get('highlights', []))}")
    quote = grab_one(DAILY_DIGEST["motivation"]["quotes"])
    parts.append(f"\n{quote}")

    parts.append(f"\nNeed new {contact.get('product', 'gear')}? Tap -> {contact['link']}")
    return "\n".join([p for p in parts if p])
# --------------------------- end-of-daily message-build -------------------
def send_whatsapp(phone: str, text: str) -> bool:
    try:
        kit.sendwhatmsg_instantly(
            phone_no=phone,
            message=text,
            wait_time=20,
            tab_close=True,
            close_time=8
        )
        return True
    except Exception as e:
        print("WhatsApp error:", e)
        return False
    
def mark_last_sent(cid: str):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    url = f"{API}/crm/v3/objects/contacts/{cid}"
    requests.patch(url, headers=HEAD, json={"properties": {"last_wa_sent": today}}, timeout=15)

def log_row(cid: str, phone: str, seg: str, ok: bool, error=""):
    LOG_FILE.exists() or LOG_FILE.write_text("timestamp,cid,phone,segment,sucsess,error\n")
    with LOG_FILE.open("a", newline="") as f:
        csv.writer(f).writerow([
            datetime.datetime.utcnow().isoformat(),
            cid, phone, seg, int(ok)
        ])

def recently_sent(last_wa: str) -> bool:
    if not last_wa:
        return False
    last = datetime.datetime.fromisoformat(last_wa[:10])
    return datetime.datetime.utcnow() - last < datetime.timedelta(days=MAX_FREQ_DAYS)

def process_list(list_id: int, segment: str):
    contacts = contacts_in_list(list_id)
    print(f"   ↳ will inspect {len(contacts)} contacts for '{segment}'")
    for cid in contacts:
        props = get_contact_prop(cid)
        phone = props["phone"]
        print(f"      CID {cid} | phone={phone or '--none--'} | last_wa={props['last_wa']}")
        if cid in already_sent:
            continue
        already_sent.add(cid)
        if not phone:
            print("         ⤷ skipped (no phone)")
            continue
        if recently_sent(props["last_wa"]):
            print("         ⤷ skipped (sent recently)")
            continue

        body = build_msg(segment, props)
        ok = send_whatsapp(phone, body)
        print(f"         ⤷ send_whatsapp ok={ok}")

        log_row(cid, phone, segment, ok, "" if ok else "send_fail")
        if ok:
            mark_last_sent(cid)
        time.sleep(5)

def main():
    for lid, seg in sorted(
        LIST_TO_STATUS.items(),
        key=lambda kv: SEGMENT_PRIORITY.index(kv[1])
    ):
        print(f"Segment {seg} | List {lid}")
        process_list(lid, seg)
if __name__ == "__main__":
    main()

