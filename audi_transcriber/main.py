import whisper

def transcribe_audio(audio_path):
    # Load the Whisper model (options: tiny, base, small, medium, large)
    model = whisper.load_model("small")

    print("Transcribing...")
    result = model.transcribe(audio_path)

    return result["text"]

if __name__ == "__main__":
    audio_file = "your_audio_file.mp3"  # replace with your file
    text = transcribe_audio(audio_file)
    print("\nTranscription:\n")
    print(text)
