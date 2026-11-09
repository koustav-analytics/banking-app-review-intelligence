 import os
   os.makedirs("data/raw", exist_ok=True)

from google_play_scraper import reviews, Sort
import pandas as pd
import time
from datetime import datetime

CUTOFF = datetime(2026, 7, 1)
MAX_PER_BANK = 12000   # safety limit

apps = {
    "SBI YONO": "com.sbi.lotusintouch",
    "HDFC": "com.hdfcbank.android.now",
    "ICICI": "com.csam.icici.bank.imobile",
    "Kotak": "com.kotak.bank.mobile",
    "Federal": "com.fedmobile",
}

all_rows = []
for bank, pkg in apps.items():
    token = None
    bank_rows = []
    while True:
        batch, token = reviews(
            pkg,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=token,
        )
        if not batch:
            break
        bank_rows.extend(batch)
        oldest = min(r["at"] for r in batch)
        print(bank, len(bank_rows), "oldest so far:", oldest.date())
        if oldest < CUTOFF or len(bank_rows) >= MAX_PER_BANK or token is None:
            break
        time.sleep(1)

    bank_rows = [r for r in bank_rows if r["at"] >= CUTOFF]
    for r in bank_rows:
        r["bank"] = bank
    all_rows.extend(bank_rows)
    print("==>", bank, "kept", len(bank_rows))

df = pd.DataFrame(all_rows)
df = df.drop(columns=["userName", "userImage"], errors="ignore")
df.to_csv("data/raw/reviews_raw.csv", index=False)
print("Saved", len(df), "reviews") 
