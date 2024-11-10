# Import necessary libraries
import os
import wave  # For handling WAV audio files
import json  # For parsing JSON data
from vosk import Model, KaldiRecognizer  # Vosk libraries for speech recognition

# This class handles transcription of an audio file using the Vosk speech recognition model.
class VoskTranscriptionModel:
    def __init__(self):
        """
        Initialize the VoskTranscriptionModel.
        
        - Loads the Vosk speech recognition model from the specified path.
        - The model contains the language data required for transcribing speech to text.
        """
        # Path to the Vosk model directory; adjust this to your model location
        self.model = Model(r"D:\NYU codes\vosk-model-small-en-us-0.15")

    def transcribe(self, audio_file_path):
        """
        Transcribes an audio file to text using the Vosk model.
        
        Parameters:
        - audio_file_path (str): Path to the audio file to be transcribed.

        Returns:
        - str: The transcribed text from the audio file.
        """
        try:
            # Open the specified audio file
            wf = wave.open(audio_file_path, "rb")
            print(f"Opened audio file {audio_file_path}")

            # Initialize the recognizer with the model and the audio file's sample rate
            recognizer = KaldiRecognizer(self.model, wf.getframerate())

            # Initialize an empty string to store the transcription
            transcription = ""

            # Process the audio file in chunks for transcription
            while True:
                # Read a chunk of audio data (4000 frames) from the file
                data = wf.readframes(4000)
                
                # Stop reading if there's no more data
                if len(data) == 0:
                    break

                # If a complete phrase is recognized, add it to the transcription
                if recognizer.AcceptWaveform(data):
                    # Retrieve the result as a JSON-formatted string
                    result = recognizer.Result()
                    # Extract the recognized text and add it to the transcription string
                    transcription += json.loads(result).get("text", "") + " "
                else:
                    # If a phrase is partially recognized, log the partial result (optional)
                    partial_result = recognizer.PartialResult()
                    print(f"Vosk partial result: {partial_result}")

            # Append any final recognized text after processing all chunks
            final_result = recognizer.FinalResult()
            transcription += json.loads(final_result).get("text", "")

            # Close the audio file
            wf.close()

            # Save the transcription to a text file in a folder named 'raw_transcripts'
            output_folder = "raw_transcripts"
            os.makedirs(output_folder, exist_ok=True)
            
            # Derive the output file path
            audio_file_name = os.path.basename(audio_file_path)
            output_file_path = os.path.join(output_folder, f"temporary_transcript.txt")
            with open(output_file_path, "w") as file:
                file.write(transcription.strip())


            # Return the final transcription with extra spaces removed
            return transcription.strip()

        except Exception as e:
            # Handle any errors that occur during transcription
            print(f"Error during transcription: {e}")
            return ""  # Return an empty string if an error occurs

    @staticmethod
    def is_valid_format(file_path):
        """
        Validates if the audio file is in the correct format for Vosk processing.
        
        Parameters:
        - file_path (str): Path to the audio file to be checked.
        
        Returns:
        - bool: True if the audio file has 1 channel, 16-bit sample width, and 16 kHz sample rate.
        """
        try:
            # Open the audio file for reading
            with wave.open(file_path, "rb") as wf:
                # Check if the file is mono (1 channel), 16-bit, and has a 16 kHz sample rate
                return wf.getnchannels() == 1 and wf.getsampwidth() == 2 and wf.getframerate() == 16000
        except Exception as e:
            # Log any error that occurs when checking the file format
            print(f"Error checking file format: {e}")
            return False  # Return False if an error occurs
