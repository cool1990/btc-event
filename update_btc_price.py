#!/usr/bin/env python3
"""Incrementally update btc_price_data.json with new daily candles from Binance."""

import json
import time
import datetime
import urllib.request
from pathlib import Path

DATA_FILE = Path(__file__).parent / "btc_price_data.json"
API_URL = (
    "https://data-api.binance.vision/api/v3/klines"
    "?symbol=BTCUSDT&interval=1d&limit=5"
)


def fetch_klines():
    with urllib.request.urlopen(API_URL, timeout=10) as resp:
        return json.loads(resp.read())


def load_existing():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")


def main():
    existing = load_existing()
    existing_dates = {entry["time"] for entry in existing}

    raw = fetch_klines()
    now_ms = int(time.time() * 1000)

    new_entries = []
    for candle in raw:
        open_ms = int(candle[0])
        close_ms = int(candle[6])

        # Skip candle if it hasn't closed yet
        if close_ms > now_ms:
            continue

        date_str = datetime.datetime.utcfromtimestamp(open_ms / 1000).strftime(
            "%Y-%m-%d"
        )

        if date_str in existing_dates:
            continue

        new_entries.append(
            {
                "time": date_str,
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            }
        )

    if new_entries:
        combined = existing + new_entries
        combined.sort(key=lambda x: x["time"])
        save(combined)
        latest = new_entries[-1]["time"]
        print(f"Added {len(new_entries)} new record(s). Latest date: {latest}")
    else:
        print("No new records. Data is already up to date.")


if __name__ == "__main__":
    main()
