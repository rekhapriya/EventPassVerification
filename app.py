"""
app.py
------
Event Entry Pass Verification System - Streamlit application.

Run locally:
    streamlit run app.py

Deploy for free on Streamlit Community Cloud (see README.md).
"""

import os
import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
from pyzbar.pyzbar import decode as qr_decode

from data_store import load_participants, find_participant, mark_checked_in
from generate_qr import generate_all_passes, OUT_DIR

LOG_PATH = os.path.join(os.path.dirname(__file__), "checkin_log.csv")

st.set_page_config(page_title="Event Entry Verification", page_icon="🎫", layout="centered")

# ---------------------------------------------------------------------------
# Session state: the NumPy array + scan log live for the duration of the
# session (a real deployment would back this with a small database).
# ---------------------------------------------------------------------------
if "records" not in st.session_state:
    st.session_state.records: np.ndarray = load_participants()

if "log" not in st.session_state:
    if os.path.exists(LOG_PATH):
        st.session_state.log = pd.read_csv(LOG_PATH)
    else:
        st.session_state.log = pd.DataFrame(
            columns=["timestamp", "participant_id", "name", "result"]
        )


def log_attempt(participant_id: str, name: str, result: str):
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "participant_id": participant_id,
        "name": name,
        "result": result,
    }
    st.session_state.log = pd.concat(
        [st.session_state.log, pd.DataFrame([row])], ignore_index=True
    )
    st.session_state.log.to_csv(LOG_PATH, index=False)


def decode_qr_image(image: Image.Image) -> str | None:
    decoded = qr_decode(image)
    if not decoded:
        return None
    return decoded[0].data.decode("utf-8")


def verify(participant_id: str):
    """Core business logic: NumPy lookup -> grant / deny decision."""
    record = find_participant(st.session_state.records, participant_id)

    if record is None:
        log_attempt(participant_id, "-", "INVALID_ID")
        st.error(f"❌ Access Denied — ID '{participant_id}' not found in the event database.")
        return

    name = str(record["name"])
    ticket = str(record["ticket_type"])

    if not bool(record["registered"]):
        log_attempt(participant_id, name, "NOT_REGISTERED")
        st.error(f"❌ Access Denied — {name} ({participant_id}) has no confirmed registration.")
        return

    if bool(record["checked_in"]):
        log_attempt(participant_id, name, "DUPLICATE_ENTRY")
        st.warning(f"⚠️ Already Checked In — {name} ({participant_id}) was already scanned earlier.")
        return

    st.session_state.records = mark_checked_in(st.session_state.records, participant_id)
    log_attempt(participant_id, name, "ENTRY_GRANTED")
    st.success(f"✅ Entry Granted — Welcome {name}! ({ticket} pass, ID: {participant_id})")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("🎫 Event Entry Pass Verification System")
st.caption("NumPy-backed participant registry · QR code check-in · built for a real deployment demo")

tab_scan, tab_registry, tab_analytics = st.tabs(["Scan Entry", "Registry", "Analytics"])

# --- Scan tab --------------------------------------------------------------
with tab_scan:
    st.subheader("Scan a pass")
    method = st.radio("Scan method", ["Upload QR image", "Use camera", "Type ID manually"], horizontal=True)

    if method == "Upload QR image":
        uploaded = st.file_uploader("Upload the participant's QR pass (.png/.jpg)", type=["png", "jpg", "jpeg"])
        if uploaded:
            image = Image.open(uploaded)
            st.image(image, width=200)
            pid = decode_qr_image(image)
            if pid:
                verify(pid)
            else:
                st.error("Could not read a QR code in that image.")

    elif method == "Use camera":
        snap = st.camera_input("Point the camera at a QR pass")
        if snap:
            image = Image.open(snap)
            pid = decode_qr_image(image)
            if pid:
                verify(pid)
            else:
                st.error("No QR code detected in the frame — try again with better lighting/focus.")

    else:
        pid_input = st.text_input("Participant ID (e.g. EVT001)")
        if st.button("Verify") and pid_input:
            verify(pid_input)

# --- Registry tab ------------------------------------------------------------
with tab_registry:
    st.subheader("Participant registry (NumPy array)")
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)

    st.markdown("**Download entry passes**")
    if not os.path.isdir(OUT_DIR) or not os.listdir(OUT_DIR):
        generate_all_passes()
    for row in st.session_state.records:
        pid = str(row["participant_id"])
        path = os.path.join(OUT_DIR, f"{pid}.png")
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(
                    f"⬇ {pid} — {row['name']}", f, file_name=f"{pid}.png", key=f"dl_{pid}"
                )

# --- Analytics tab -----------------------------------------------------------
with tab_analytics:
    st.subheader("Check-in analytics")
    log = st.session_state.log

    if log.empty:
        st.info("No scans yet — try the Scan Entry tab first.")
    else:
        st.dataframe(log, use_container_width=True)

        counts = log["result"].value_counts()
        fig, ax = plt.subplots()
        ax.bar(counts.index, counts.values, color=["#2ecc71", "#e74c3c", "#f39c12", "#95a5a6"][: len(counts)])
        ax.set_ylabel("Number of scans")
        ax.set_title("Scan outcomes")
        plt.xticks(rotation=20)
        st.pyplot(fig)

        csv_bytes = log.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export full log as CSV", csv_bytes, file_name="checkin_log.csv", mime="text/csv")
