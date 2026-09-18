"""Turn clinical record text into a plain-language explanation using Gemini."""

from google.genai import types

SYSTEM_PROMPT = """You are a calm, clear medical communicator helping a patient \
or caregiver understand their own clinical record. You are not diagnosing or \
giving medical advice — you are translating existing clinical language into \
plain, everyday English.

Guidelines:
- Explain what the terms, results, and findings mean in plain language.
- Organize the explanation with short headers if the record covers multiple \
topics (e.g. "What the visit was about", "Test results", "What happens next").
- Define any medical abbreviations or jargon the first time they appear.
- Note anything in the record that looks like a follow-up action, and call it \
out clearly (e.g. "Your doctor wants you to schedule a follow-up in 2 weeks").
- Do not invent information that is not in the record.
- End with a short, gentle reminder that this is an explanation of the \
record, not medical advice, and that they should ask their care team about \
anything unclear.
- Keep the tone warm, respectful, and non-alarming, even when the record \
contains serious findings.
"""


def translate_to_plain_language(
    client,
    record_text: str = "",
    *,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
) -> str:
    """
    Call the Gemini API to translate a clinical record into plain language.

    Args:
        client: an initialized google.genai.Client
        record_text: the raw clinical record text, if available
        image_bytes: image data for a scanned or photographed record
        image_mime_type: MIME type for image_bytes, such as image/jpeg

    Returns:
        A plain-language explanation as a string.
    """
    contents = [
        "Here is a clinical record. Please explain it in plain language "
        "for the patient:",
    ]
    if record_text:
        contents.append(record_text)
    if image_bytes is not None:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type)
        )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=1200,
        ),
    )

    return (response.text or "").strip()
