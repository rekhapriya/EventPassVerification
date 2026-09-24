"""
generate_qr.py
---------------
Generates one QR code image per participant (their event entry pass).
Run once to (re)populate the qrcodes/ folder:

    python generate_qr.py
"""

import os
import qrcode
from data_store import load_participants

OUT_DIR = os.path.join(os.path.dirname(__file__), "qrcodes")


def generate_all_passes():
    os.makedirs(OUT_DIR, exist_ok=True)
    records = load_participants()

    for row in records:
        pid = str(row["participant_id"])
        name = str(row["name"])
        # QR payload: just the participant_id. Keeping it minimal means the
        # NumPy array (not the QR code) stays the single source of truth.
        img = qrcode.make(pid)
        path = os.path.join(OUT_DIR, f"{pid}.png")
        img.save(path)
        print(f"Generated pass for {pid} ({name}) -> {path}")

    print(f"\nDone. {len(records)} passes written to '{OUT_DIR}/'.")


if __name__ == "__main__":
    generate_all_passes()
