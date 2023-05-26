from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import requests

app = Flask(__name__)

def transcribe_audio(audio_data):
    # Load audio file using pydub
    audio = AudioSegment.from_file(audio_data)

    # Convert audio to PCM WAV format
    audio = audio.set_channels(1)  # Ensure single channel audio
    audio = audio.set_frame_rate(16000)  # Set sample rate to 16000 Hz
    audio.export("temp.wav", format="wav")

    # Perform transcription
    r = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        if not text:
            text = "Speech recognition could not transcribe the audio."
    except sr.UnknownValueError:
        text = "Speech recognition could not understand the audio."

    # Remove temporary WAV file
    os.remove("temp.wav")

    return text

def send_transcription(transcription):
    url = "http://localhost:8000/query"  # Replace with your target route
    headers = {"Content-Type": "text/plain"}

    response = requests.post(url, data=transcription, headers=headers)

    # Display the response content
    print(response.text)

    return response.text

@app.route("/")
def index():
    return render_template("index.html", response=[])

@app.route("/process_audio", methods=["POST"])
def process_audio():
    audio_data = request.files["audio"]
    transcription = transcribe_audio(audio_data)
    print(transcription)
    response_text = send_transcription(transcription)

    # Format the response data for table structure
    response_data = [['Transcription'], [response_text]]

    return jsonify(response_data)

if __name__ == "__main__":
    app.run()
