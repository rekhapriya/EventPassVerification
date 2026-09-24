# 🎫 Event Entry Pass Verification System

## Project Description
A real-world mini application that manages event check-in using **NumPy
structured arrays** as the core data store, **QR codes** as digital entry
passes, and a **Streamlit** web interface for staff to scan and verify
attendees at the door.

Each participant's registration record (ID, name, ticket type, registration
status, check-in status) lives as a row in a NumPy structured array. A QR
code encoding the participant's ID acts as their pass. When scanned, the
app decodes the QR code, looks the ID up in the NumPy array, and grants or
denies entry based on registration and duplicate-scan checks.

## Features
- NumPy structured array as the single source of truth for participant data
- QR code generation for every participant (`generate_qr.py`)
- QR decoding via three input methods: upload an image, live camera capture,
  or manual ID entry
- Grant / deny logic:
  - ✅ Valid, registered, first scan → **Entry Granted**
  - ⚠️ Already scanned → **Duplicate Entry** warning
  - ❌ Registration not confirmed → **Access Denied**
  - ❌ ID not found in the array → **Invalid ID**
- Every scan attempt is logged with a timestamp and exportable as CSV
  (Pandas)
- Live analytics chart of scan outcomes (Matplotlib)
- Downloadable pass images for every participant from the app itself

## Technologies / Libraries Used
- Python, NumPy (structured arrays)
- `qrcode` + Pillow — QR code generation
- `pyzbar` — QR code decoding
- Streamlit — web UI and deployment
- Pandas — scan log + CSV export
- Matplotlib — analytics chart

## Project Structure
```
event_entry_system/
├── app.py              # Streamlit application (entry point)
├── data_store.py        # NumPy structured array + lookup logic
├── generate_qr.py        # Generates QR pass images
├── qrcodes/              # Generated QR pass images (auto-created)
├── checkin_log.csv       # Scan log (auto-created at runtime)
├── requirements.txt
├── packages.txt          # system dependency (libzbar0) for Streamlit Cloud
└── README.md
```

## How to Run Locally
```bash
git clone <your-repo-url>
cd event_entry_system
pip install -r requirements.txt
python generate_qr.py      # creates sample QR passes in qrcodes/
streamlit run app.py
```
Open the local URL Streamlit prints (usually http://localhost:8501).

To test: open the **Scan Entry** tab, choose **Upload QR image**, and upload
one of the generated files from `qrcodes/` (e.g. `EVT001.png`).

## Deployment (Streamlit Community Cloud — free)
1. Push this folder to a public GitHub repository.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, select the repo, branch `main`, and set the main file
   to `app.py`.
4. Streamlit Cloud automatically installs `requirements.txt` and
   `packages.txt` (needed for the `pyzbar`/`libzbar0` dependency).
5. Deploy — you'll get a live `https://<app-name>.streamlit.app` link.

## Sample Participant IDs (for testing)
| ID | Name | Ticket | Registered |
|----|------|--------|------------|
| EVT001 | Rekha Priya | VIP | ✅ |
| EVT002 | Arun Kumar | General | ✅ |
| EVT005 | Meena Loganathan | General | ❌ (tests Access Denied) |
| EVT999 | — | — | Not in database (tests Invalid ID) |

## Links
- 🔗 Google Colab Notebook: *add your link here*
- 🔗 Deployed Application: *add your Streamlit Cloud link here*
- 🔗 GitHub Repository: *add your repo link here*

## Author
Rekha Priya Balachandar — AI & ML course project
