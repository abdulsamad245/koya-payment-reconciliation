#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

from datetime import datetime
from decimal import Decimal
from pathlib import Path

base = Path(__file__).resolve().parent
latest = {}

with (base / "payments.jsonl").open() as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue
        txn_id = event["txn_id"]
        timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        if txn_id not in latest or timestamp > latest[txn_id][0]:
            latest[txn_id] = (timestamp, event)

successful = [event for _, event in latest.values() if event["status"] == "success"]
count = len(successful)
total = sum((Decimal(str(event["amount"]).replace(",", ""))
             for event in successful), Decimal("0"))

with (base / "expected.txt").open() as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
