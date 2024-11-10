import subprocess
import os

def convert_to_wav(input_file, output_file):
    # Replace with the full path to the FFmpeg executable
    ffmpeg_path = r"C:\Users\Dheeraj\scoop\apps\ffmpeg\current\bin\ffmpeg.exe"

    if not os.path.exists(ffmpeg_path):
        print(f"FFmpeg not found at: {ffmpeg_path}")
        return

    command = [
        ffmpeg_path, "-i", input_file,
        "-ac", "1",  # mono audio
        "-ar", "16000",  # 16 kHz sample rate
        output_file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
    except FileNotFoundError as e:
        print(f"FFmpeg not found: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
