# real_time_transcription.py

import pyaudio
import json
from vosk import Model, KaldiRecognizer

class RealTimeTranscription:
    def __init__(self, model_path):
        """
        Initialize the Vosk model and audio stream for real-time transcription.
        """
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)  # 16kHz sample rate

    def start_transcription(self):
        """
        Start real-time audio capture from the microphone and transcribe in real-time.
        :return: Full transcription as a string.
        """
        # Initialize PyAudio and start capturing
        audio_interface = pyaudio.PyAudio()
        stream = audio_interface.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
        stream.start_stream()
        
        transcription = ""
        try:
            while True:
                data = stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    text = json.loads(result).get("text", "")
                    transcription += text + " "
                    print(f"Real-time Transcription: {text}")
        except KeyboardInterrupt:
            print("Stopping transcription...")

        stream.stop_stream()
        stream.close()
        audio_interface.terminate()
        
        return transcription
