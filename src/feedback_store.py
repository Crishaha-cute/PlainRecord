"""
Very lightweight feedback storage for the MVP.

This is intentionally simple: it appends each piece of feedback to a local
CSV file. For a pilot, this is enough to review qualitative feedback by hand
(the metric chosen for this MVP: user feedback and ease of understanding).

For anything beyond a pilot, swap this out for a real database.
"""

import csv
import os

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "..", "feedback_log.csv")


def save_feedback(timestamp: str, rating: str, comment: str) -> None:
    file_exists = os.path.isfile(FEEDBACK_FILE)

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "rating", "comment"])
        writer.writerow([timestamp, rating, comment])
