import whisper


print("Loading Whisper model...")

model = whisper.load_model("base")

print("Whisper model loaded successfully.")


def transcribe_audio(audio_path):

    result = model.transcribe(
        audio_path,
        language="en"
    )

    return result["text"].strip()