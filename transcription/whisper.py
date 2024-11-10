import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import sounddevice as sd
import numpy as np
import warnings
import time

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Set device configuration
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Load the Whisper-medium model (you can switch to "openai/whisper-small" if needed)
model_id = "openai/whisper-medium"
print("Loading Whisper model...")
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True
)
model.to(device)
print("Model loaded successfully.")

# Disable forced_decoder_ids to prevent conflict warning
model.config.forced_decoder_ids = None

# Load processor
print("Loading processor...")
processor = AutoProcessor.from_pretrained(model_id)
print("Processor loaded successfully.")

# Set up the ASR pipeline
print("Setting up ASR pipeline...")
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)
print("ASR pipeline setup complete.")

# Define audio parameters
SAMPLE_RATE = 16000
DURATION = 30  # Set recording duration to 30 seconds

def record_audio(duration, sample_rate):
    print("Recording... (Please speak for 30 seconds)")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording complete. Audio captured.")
    return audio.flatten()

# Record and transcribe a single 30-second audio clip
audio_data = record_audio(DURATION, SAMPLE_RATE)
print("Audio data captured. Processing...")

# Convert audio to input features
input_features = processor(audio_data, sampling_rate=SAMPLE_RATE, return_tensors="pt").input_features
input_features = input_features.to(device)

# Generate transcription with language explicitly set to English
with torch.no_grad():
    print("Generating transcription...")
    result = pipe(audio_data, generate_kwargs={"language": "en"})

print(result["text"])
