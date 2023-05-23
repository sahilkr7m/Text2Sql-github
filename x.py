import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

def record_audio(duration, sample_rate, file_path):
    # Initialize an empty list to store the recorded audio data
    audio_data = []

    def callback(indata, frames, time, status):
        # This is the callback function that will be called for each audio block
        # 'indata' contains the audio data from the input device

        # Append the audio data to the list
        audio_data.append(indata.copy())

    # Start capturing audio
    print("Recording started...")
    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()

    # Wait for the desired duration
    sd.sleep(int(duration * 1000))

    # Stop capturing audio
    stream.stop()
    stream.close()
    print("Recording finished.")

    # Concatenate the recorded audio data into a single numpy array
    audio_array = np.concatenate(audio_data)

    # Save the audio data as a WAV file
    wav.write(file_path, sample_rate, audio_array)

# Set the desired sample rate, duration, and file path
sample_rate = 44100  # Example sample rate
duration = 5  # Example duration in seconds
file_path = "recorded_audio.wav"

# Call the function to record audio and save it as a WAV file
record_audio(duration, sample_rate, file_path)
