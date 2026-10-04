import os
import whisper

# ============================================================
# WHISPER CONFIGURATION
# ============================================================
# base is considerably faster than small on a CPU-only laptop,
# while still supporting English, Hindi and Marathi.
MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")

print(f"Loading Whisper model: {MODEL_SIZE}")
model = whisper.load_model(MODEL_SIZE)
print("Whisper model loaded successfully.")

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
}


def transcribe_complaint(audio_path):
    """
    Transcribe the complainant's original speech.

    IMPORTANT:
    - One Whisper pass is used for speed.
    - Whisper automatically detects the language.
    - The original speech is NOT rewritten or corrected.
    - English, Hindi and Marathi are the supported application languages.
    """

    if not audio_path:
        raise ValueError("Audio path is required.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Do NOT call detect_language() separately. That would require an
    # additional model pass and makes transcription noticeably slower.
    result = model.transcribe(
        audio_path,
        task="transcribe",
        language=None,              # automatic language detection
        fp16=False,                 # Windows CPU
        temperature=0,
        beam_size=1,
        best_of=1,
        condition_on_previous_text=False,
        without_timestamps=True,
        verbose=False,
    )

    text = (result.get("text") or "").strip()
    detected_language = (result.get("language") or "").lower()

    if not text:
        raise ValueError("No speech could be detected in the recording.")

    # Keep the detected language visible even if Whisper returns a language
    # outside the three languages supported by the UI.
    language_name = SUPPORTED_LANGUAGES.get(
        detected_language,
        detected_language or "Unknown"
    )

    return {
        "text": text,
        "language": detected_language,
        "language_name": language_name,
    }
