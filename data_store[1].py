"""
data_store.py
--------------
Core data layer for the Event Entry Pass Verification System.
Participant records are held in a NumPy STRUCTURED ARRAY (the assignment's
required data structure) rather than a list of dicts or a DataFrame.

Fields:
    participant_id : str   -> unique ID encoded in the QR code
    name           : str
    ticket_type    : str   -> 'VIP' / 'General' / 'Speaker'
    registered     : bool  -> was the ticket actually paid/confirmed
    checked_in     : bool  -> mutated at scan time (duplicate-entry guard)
"""

import numpy as np

# dtype for a structured NumPy array - this IS the "NumPy array" required
# by the assignment; every participant is a row/record in this array.
PARTICIPANT_DTYPE = np.dtype([
    ("participant_id", "U10"),
    ("name", "U40"),
    ("ticket_type", "U10"),
    ("registered", "bool"),
    ("checked_in", "bool"),
])

# Seed data - in a real deployment this would come from a registration
# form / CSV export, loaded straight into the same structured array.
_SEED_ROWS = [
    ("EVT001", "Rekha Priya",     "VIP",     True,  False),
    ("EVT002", "Arun Kumar",      "General", True,  False),
    ("EVT003", "Divya S",         "General", True,  False),
    ("EVT004", "Karthik R",       "Speaker", True,  False),
    ("EVT005", "Meena Loganathan","General", False, False),  # not registered
    ("EVT006", "Sathish V",       "VIP",     True,  False),
    ("EVT007", "Priyanka T",      "General", True,  False),
    ("EVT008", "Naveen G",        "Speaker", True,  False),
]


def load_participants() -> np.ndarray:
    """Return a fresh structured NumPy array of all participants."""
    return np.array(_SEED_ROWS, dtype=PARTICIPANT_DTYPE)


def find_participant(records: np.ndarray, participant_id: str):
    """
    Look up a participant by ID inside the NumPy array using boolean
    masking (vectorised NumPy lookup, not a Python loop).
    Returns the single matching record (np.void) or None if not found.
    """
    mask = records["participant_id"] == participant_id.strip().upper()
    matches = records[mask]
    if matches.size == 0:
        return None
    return matches[0]


def mark_checked_in(records: np.ndarray, participant_id: str) -> np.ndarray:
    """Set checked_in=True for a participant row in place and return the array."""
    mask = records["participant_id"] == participant_id.strip().upper()
    records["checked_in"][mask] = True
    return records
