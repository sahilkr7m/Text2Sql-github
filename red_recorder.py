import sounddevice as sd
import tkinter as tk
from threading import Thread
from scipy.io import wavfile
import numpy as np
import whisper
import spacy
import requests
url = "http://localhost:8000/query"

nlp = spacy.load("en_core_web_sm")

def Post_to_backend(text):
    text_data = text

    # Make the POST request
    response = requests.post(url, data=text_data)

    # Check the response
    if response.status_code == 200:
        print("Request successful!")
        print("Response:", response.text)
    else:
        print("Request failed with status code:", response.status_code)



def audio_to_text(audiofile):
    model = whisper.load_model("base")
    result = model.transcribe(audiofile)
    print(result["text"])

    sentence = result["text"]
    # doc = nlp(sentence)
    Post_to_backend(sentence)
    

class AudioRecorder:
    def __init__(self, sample_rate, channels):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_frames = []

    def start_recording(self):
        self.recording = True
        self.audio_frames = []
        self.recording_thread = Thread(target=self.record_audio) #run process in background
        self.recording_thread.start()

    def stop_recording(self):
        self.recording = False

    def record_audio(self):
        duration = 0.1  # Duration of each audio frame in seconds

        def callback(indata, frames, time, status):
            if status:
                print('Error:', status)
            self.audio_frames.append(indata.copy())

        stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback)
        stream.start()

        while self.recording:
            sd.sleep(int(duration * 1000))

        stream.stop()
        stream.close()

    def save_recording(self, filename):
        audio_data = []
        for frame in self.audio_frames:
            audio_data.append(frame)

        audio_data = np.concatenate(audio_data)
        wavfile.write(filename, self.sample_rate, audio_data)


class App:
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.recorder = AudioRecorder(self.sample_rate, self.channels)

        self.root = tk.Tk()
        self.root.title("RED Recorder")

        self.record_button = tk.Button(self.root, text="Record", command=self.start_recording)
        self.record_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
                
        window_width = 300
        window_height = 200

        # Set the window size and position
        self.root.geometry(f"{window_width}x{window_height}+100+100")

        self.root.mainloop()

    def start_recording(self):
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.recorder.start_recording()

    def stop_recording(self):
        self.recorder.stop_recording()

        filename = "recorded_audio.wav"
        self.recorder.save_recording(filename)

        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


        print(f"Recording saved to {filename}.")
        print("converting the recoring into text......")
        audio_to_text(filename)

if __name__ == "__main__":
    app = App()
