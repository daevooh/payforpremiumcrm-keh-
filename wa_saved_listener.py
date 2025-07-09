#!/usr/bin/env python3
import re, json, time, pathlib
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by   import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui  import WebDriverWait
from selenium.webdriver.support     import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── CONFIG ─────────────────────────────────────────────────────────────
PROFILE_DIR   = r"C:\Users\kingdavid\selenium_profile"  # folder you created
SAVE_KEYWORDS = re.compile(r"\b(saved|i\s*saved|done\s*saving)\b", re.I)
JSON_PATH     = pathlib.Path("saved_numbers.json")
ROW_XPATH     = '//*[@id="pane-side"]//div[@role="row"]'
MSG_XPATH     = ('//div[contains(@class,"message-in")]'
                 '//span[contains(@class,"selectable-text")]')
# ───────────────────────────────────────────────────────────────────────

def load_saved() -> dict:
    return json.loads(JSON_PATH.read_text()) if JSON_PATH.exists() else {}

def save_saved(d: dict):
    JSON_PATH.write_text(json.dumps(d, indent=2))

def extract_phone(url: str) -> str | None:
    q = parse_qs(urlparse(url).query).get("phone")
    return f"+{q[0]}" if q else None

def chat_contains_save(driver) -> bool:
    """Scroll upward through the open chat; return True if any incoming
       message matches SAVE_KEYWORDS."""
    panel = driver.find_element(By.XPATH,
        '//div[@data-testid="conversation-panel-messages"]')
    # quick check on visible messages
    if any(SAVE_KEYWORDS.search(m.text) for m in driver.find_elements(By.XPATH, MSG_XPATH)):
        return True
    prev_height = -1               # loop‑until top
    for _ in range(40):            # adjust if you need deeper history
        driver.execute_script("arguments[0].scrollTop = 0", panel)
        time.sleep(0.6)
        if any(SAVE_KEYWORDS.search(m.text) for m in driver.find_elements(By.XPATH, MSG_XPATH)):
            return True
        h = driver.execute_script("return arguments[0].scrollHeight", panel)
        if h == prev_height:       # reached earliest message
            break
        prev_height = h
    return False

# ── START CHROME ──────────────────────────────────────────────────────
opts = webdriver.ChromeOptions()
opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
opts.add_experimental_option("detach", True)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)
print("✅ Chrome started")

driver.get("https://web.whatsapp.com")
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="pane-side"]'))
)
print("✅ WhatsApp sidebar ready")

# ── MAIN DEEP‑SCAN ────────────────────────────────────────────────────
saved = load_saved()
sidebar       = driver.find_element(By.ID, "pane-side")
seen_rows     = set()
bottom        = False   

# driver.quit()         # uncomment if you want Selenium to close here
while not bottom:
    rows = sidebar.find_elements(By.XPATH, ROW_XPATH)

    
    for i, row in enumerate(rows):
        rid = row.get_attribute("data-id") or f"row-{i}"
        print("👀 Chat row found:", rid)
        if rid in seen_rows:
            continue
        seen_rows.add(rid)

        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
            driver.execute_script("arguments[0].click();", row)
            print(f"➡️ Clicked chat row: {rid}")
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠️ Could not click row {rid}: {e}")

        # 2️⃣ search visible + older messages
        panel = driver.find_element(
            By.XPATH, '//div[@data-testid="conversation-panel-messages"]')
        def has_saved():
            return any(
                SAVE_KEYWORDS.search(m.text) for m in
                driver.find_elements(By.XPATH, MSG_XPATH)
            )

        # check current view
        if not has_saved():
            prev = -1
            for _ in range(40):          # scroll up to 40 times
                driver.execute_script("arguments[0].scrollTop = 0", panel)
                time.sleep(0.6)
                if has_saved():
                    break
                h = driver.execute_script("return arguments[0].scrollHeight", panel)
                if h == prev:            # reached oldest msg
                    break
                prev = h

        # 3️⃣ if found, extract phone & save
        if has_saved():
            url   = driver.current_url
            phone = extract_phone(url)
            if not phone:                # fallback via sidebar
                driver.find_element(By.XPATH, '//header').click()
                time.sleep(0.8)
                phone = driver.find_element(
                    By.XPATH, '//span[@data-testid="copyable-text"]').text
                phone = "+" + re.sub(r"\D", "", phone)
                driver.find_element(By.XPATH, '//header').click()

            if phone and phone not in saved:
                saved[phone] = True
                saved_json(saved)
                print("✅ added", phone)

    # 4️⃣ scroll chat list down and loop
    prev_top = sidebar.get_property("scrollTop")
    sidebar.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.6)
    bottom = sidebar.get_property("scrollTop") == prev_top
print(f"📝 finished scan – {len(saved)} numbers recorded")