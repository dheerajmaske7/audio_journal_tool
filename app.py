# Import necessary libraries
from flask import Flask, request, render_template, flash, jsonify
from transcription.vosk_model import VoskTranscriptionModel  # Vosk model for audio transcription
from transcription.conversion import convert_to_wav
from transcription.real_time_transcription import transcribe_stream
  # Function to convert audio to WAV format
import os  # For handling file paths and directories
import subprocess
import threading  # Required for stop_event and background threading

# Global variables
is_listening = False  # Tracks whether real-time transcription is active
transcription_result = ""  # Stores the transcription result
stop_event = threading.Event()  # Event to signal stopping transcription



# Initialize the Flask application
# `Flask` is a micro web framework used to create web applications.
# This application will provide a web interface for uploading and transcribing audio files.
app = Flask(__name__)

# Configure upload folder for temporary storage of uploaded files.
# `UPLOAD_FOLDER` specifies the directory where files are temporarily stored.
# Without this, files would need to be manually managed, increasing complexity.
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['RAW_TRANSCRIPTS_FOLDER'] = './raw_transcripts'  # Correctly define the folder path here

# A secret key is required for flashing messages, which are temporary notifications.
# If `secret_key` is not set, the application will be unable to display feedback messages.
app.secret_key = 'supersecretkey'  # Needed to flash messages

# Route for the main page to render the upload and transcription interface.
# `@app.route('/')` binds the URL path '/' to the `index` function, which loads the main page.
# Without this route, the application would have no homepage to load.
@app.route('/')
def index():
    # Renders `index.html`, which contains the file upload form and displays results.
    # Without `render_template`, we would need to manually create HTML content in Python.
    return render_template('index.html')  # Render the main page with the upload form


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    try:
        # Retrieve the uploaded audio file from the request.
        # `request.files.get('file')` attempts to get the file from the request payload.
        # If no file is provided, display a flash message and reload the main page.
        audio_file = request.files.get('file')
        if not audio_file or audio_file.filename == '':
            # Flash message for cases when no file is selected by the user.
            # Flashing provides user feedback, allowing them to correct their actions.
            flash("No selected file")
            return render_template('index.html', transcription="")

        # Save the uploaded file temporarily in the configured upload folder.
        # This saves the file on the server so it can be processed.
        # Without saving, we cannot access the file contents for transcription.
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
        audio_file.save(file_path)

        # Initialize the Vosk transcription model for processing.
        # `VoskTranscriptionModel` provides a method to convert audio to text.
        # Without this, transcription would not be possible.
        transcription_model = VoskTranscriptionModel()

        # Check if the uploaded file format is compatible with Vosk.
        # The `is_valid_format` method ensures the file meets Vosk's requirements (e.g., 16kHz mono WAV).
        # If the format is incorrect, convert it to the required format.
        if not transcription_model.is_valid_format(file_path):
            # Convert the file to the required WAV format if needed.
            # `convert_to_wav` uses FFmpeg to adjust the format. Without conversion, incompatible files would fail.
            converted_path = os.path.join(app.config['UPLOAD_FOLDER'], "converted_audio.wav")
            convert_to_wav(file_path, converted_path)
            file_path = converted_path  # Update file_path to point to the converted file

        # Transcribe the audio file using Vosk.
        # `transcribe` returns the recognized text from the audio file.
        # Without this step, we would not get any transcription.
        transcription = transcription_model.transcribe(file_path)
        
        # Display a success or failure message based on the transcription result.
        # Flashing indicates the success of the transcription process, improving user experience.
        flash("Transcription successful" if transcription else "Transcription failed")
        
        # Render the result on the main page.
        # This renders the `index.html` template and passes the transcription text for display.
        # Without rendering, the transcription would not be visible to the user.
        return render_template('index.html', transcription=transcription)

    except Exception as e:
        # Error handling in case of issues during transcription.
        # Printing the error helps in debugging, and flashing indicates an issue to the user.
        print(f"Error during transcription: {e}")
        flash("Transcription failed")
        return render_template('index.html', transcription="")


@app.route('/generate_blog', methods=['POST'])
def generate_blog():
    try:
        # Run llm_main_claude.py script to generate the blog
        subprocess.run(['python', r'D:\NYU codes\Audio journal\transcription\llm_main_claude.py'], check=True)

        # Read the raw content from blog_output.txt
        blog_file_path = r'D:\NYU codes\Audio journal\Blog_generated\content.txt'
        if not os.path.exists(blog_file_path):
            print(f"Error: Blog content file not found at {blog_file_path}")
            return jsonify({'error': 'Blog content file not found.'}), 500

        with open(blog_file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()

        # Extract title and content from the raw content
        if "TextBlock" in raw_content:
            # Extract using regex
            import re
            match = re.search(r"TextBlock\(text='Title: (.*?)\\n\\n(.*)', type='text'\)", raw_content, re.DOTALL)
            if match:
                title = match.group(1).strip()
                content = match.group(2).replace("\\n", "\n").replace("\\'", "'").strip()
            else:
                return jsonify({'error': 'Failed to parse blog content.'}), 500
        else:
            return jsonify({'error': 'Invalid content format.'}), 500

        # Write title and content to separate files for Medium integration
        title_file_path = r'D:\NYU codes\Audio journal\Blog_generated\title.txt'
        formatted_content_path = r'D:\NYU codes\Audio journal\Blog_generated\formatted_content.txt'

        with open(title_file_path, 'w', encoding='utf-8') as title_file:
            title_file.write(title)

        with open(formatted_content_path, 'w', encoding='utf-8') as content_file:
            content_file.write(f"Title: {title}\n\nContent:\n{content}")

        # Return the blog content for display in the text area
        return jsonify({'title': title, 'blog_content': content}), 200

    except subprocess.CalledProcessError as e:
        # Handle errors from the subprocess
        print(f"Subprocess error: {e.stderr}")
        return jsonify({'error': 'Failed to generate blog.'}), 500

    except Exception as e:
        # Handle unexpected errors
        import traceback
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Unexpected server error.'}), 500



@app.route('/start_real_time_capture', methods=['POST'])
def start_real_time_capture():
    """Start real-time transcription."""
    global is_listening, transcription_result, stop_event

    if is_listening:
        return "Already listening!", 400

    is_listening = True
    transcription_result = ""
    stop_event.clear()

    # Run real-time transcription in a background thread
    threading.Thread(target=run_real_time_transcription).start()
    return "Listening started", 200


@app.route('/stop_real_time_capture', methods=['POST'])
def stop_real_time_capture():
    """Stop real-time transcription and return the result."""
    global is_listening, transcription_result, stop_event

    print("Stopping real-time capture...")  # Debugging step

    if not is_listening:
        print("Not currently listening.")
        return "Not currently listening", 400

    stop_event.set()  # Signal the transcription thread to stop
    while is_listening:  # Wait for the transcription thread to stop
        pass

    print("Transcription stopped.")  # Debugging step

    # Save the transcription to a file
    try:
        os.makedirs(app.config['raw_transcripts'], exist_ok=True)
        transcription_file_path = os.path.join(app.config['raw_transcripts'], 'temporary_transcript.txt')
        with open(transcription_file_path, 'w', encoding='utf-8') as file:
            file.write(transcription_result)
        print(f"Transcription saved at {transcription_file_path}")  # Debugging step
    except Exception as e:
        print(f"Error saving transcription: {e}")
        return "Error saving transcription", 500

    return transcription_result or "No transcription available.", 200


def run_real_time_transcription():
    """Real-time transcription with stop control."""
    from google.cloud import speech

    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    with MicrophoneStream(16000, 1600) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        transcription = ""
        try:
            for response in responses:
                if stop_event.is_set():  # Check if stop signal is triggered
                    print("Stop event triggered. Ending transcription.")  # Debugging step
                    break

                for result in response.results:
                    if result.is_final:
                        transcription += result.alternatives[0].transcript + "\n"
                        print(f"Final transcript: {result.alternatives[0].transcript}")  # Debugging step

        except Exception as e:
            print(f"Error during transcription: {e}")  # Debugging step
        return transcription





@app.route('/post_on_medium', methods=['POST'])
def post_on_medium():
    try:
        # Correct path to the Medium_platform_posting.py script
        script_path = os.path.join(os.getcwd(), 'Medium_platform_posting.py')
        
        # Execute the script
        result = subprocess.run(['python', script_path], capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({'message': 'Successfully posted on Medium!'}), 200
        else:
            return jsonify({'error': result.stderr}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Ensure the upload directory exists; create it if necessary.
    # `os.makedirs` prevents errors if the folder is missing.
    # Without this, attempts to save files would fail, breaking the upload process.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Start the Flask app in debug mode for development.
    # `debug=True` enables auto-reloading and provides detailed error messages.
    # Without this, the app would not auto-reload after code changes.
    app.run(debug=True)
