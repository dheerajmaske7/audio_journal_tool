# Import necessary libraries
from flask import Flask, request, render_template, flash, jsonify
from transcription.vosk_model import VoskTranscriptionModel  # Vosk model for audio transcription
from transcription.conversion import convert_to_wav  # Function to convert audio to WAV format
import os  # For handling file paths and directories
import subprocess

# Initialize the Flask application
# `Flask` is a micro web framework used to create web applications.
# This application will provide a web interface for uploading and transcribing audio files.
app = Flask(__name__)

# Configure upload folder for temporary storage of uploaded files.
# `UPLOAD_FOLDER` specifies the directory where files are temporarily stored.
# Without this, files would need to be manually managed, increasing complexity.
app.config['UPLOAD_FOLDER'] = './uploads'

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

# Route to handle audio transcription after file upload.
# `@app.route('/transcribe_audio', methods=['POST'])` binds the URL path '/transcribe_audio' to the `transcribe_audio` function.
# This route only accepts `POST` requests, which send data from the client to the server.
# Without this route, we could not process file uploads or provide transcription.
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


# New route for generating a blog
@app.route('/generate_blog', methods=['POST'])
def generate_blog():
    try:
        # Run llm_main.py, assuming it generates the blog and saves it to blog_output.txt
        subprocess.run(['python', 'llm_main.py'], check=True)

        # Read the content from blog_output.txt and return it as a response
        blog_file_path = 'blog_output.txt'
        with open(blog_file_path, 'r') as file:
            blog_content = file.read()

        return blog_content

    except Exception as e:
        print(f"Error during blog generation: {e}")
        return "Error generating blog", 500

# Main entry point to start the application.
# `if __name__ == '__main__':` ensures this code only runs when the script is executed directly.
# Without this, the app might not run if imported as a module.
if __name__ == '__main__':
    # Ensure the upload directory exists; create it if necessary.
    # `os.makedirs` prevents errors if the folder is missing.
    # Without this, attempts to save files would fail, breaking the upload process.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Start the Flask app in debug mode for development.
    # `debug=True` enables auto-reloading and provides detailed error messages.
    # Without this, the app would not auto-reload after code changes.
    app.run(debug=True)
