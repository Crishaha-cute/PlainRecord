# PlainRecord

A Streamlit MVP that translates clinical records into plain language for
patients and caregivers.

## The problem
Patient portals (MyChart, etc.) give people access to their records, but not
understanding — notes are full of clinical jargon and abbreviations with no
translation layer.

## Who it's for
Patients and caregivers who want to understand their own medical records
without having to Google every term or wait for a rushed clarification during
a short appointment.

## MVP scope

**Must-have (this build):**
- Paste or upload a record (.pdf, .txt, or image such as .jpg/.jpeg/.png)
- GenAI-powered plain-language explanation
- Qualitative feedback capture (thumbs up/down + comment)
- Download explanation as text

**Nice-to-have (next iteration):**
- Support for multiple records / a running history
- Highlighting of follow-up actions as checklist items
- Multi-language explanations

**Next version:**
- Direct portal integration (e.g. pull records from MyChart via API)
- Caregiver sharing / multi-user accounts
- Structured before/after comprehension check

## Success metric for this pilot
Qualitative: user feedback on whether the explanation was helpful and easy to
understand, collected via the in-app thumbs up/down + comment box after each
explanation. Feedback is logged to `feedback_log.csv` for manual review during
the pilot.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Create a local `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your-key-here
   ```
3. Launch the app:
   ```
   streamlit run app.py
   ```

## Project structure
```
plainrecord/
├── app.py                  # Streamlit UI and app flow
├── src/
│   ├── record_reader.py    # Extracts text from uploaded PDF/txt files
│   ├── translator.py       # Calls Gemini to generate plain-language explanations
│   └── feedback_store.py   # Logs qualitative feedback to CSV
├── requirements.txt
└── README.md
```

## Important note
This tool explains what a record says — it does not diagnose, interpret
severity, or replace a conversation with a clinician. Every explanation ends
with a reminder to follow up with the care team on anything unclear.
