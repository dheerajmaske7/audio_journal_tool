import os
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
load_dotenv()

# Directly set the API key (or use `os.getenv` if .env works properly)
api_key = "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"

def generate_documentation_blog(system_prompt_path, user_prompt_path, raw_transcript_path, output_path): 
    if not api_key:
        print("Error: CLAUDE_API_KEY not found in environment variables.")
        return
    
    # Initialize the Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Load system prompt from file
    with open(system_prompt_path, 'r', encoding='utf-8') as file:
        system_prompt = file.read()

    # Load user prompt template from file
    with open(user_prompt_path, 'r', encoding='utf-8') as file:
        user_prompt_template = file.read()

    # Verify and load transcript data
    if not os.path.isfile(raw_transcript_path):
        print(f"Error: Transcript file not found at {raw_transcript_path}")
        return
    with open(raw_transcript_path, 'r', encoding='utf-8') as file:
        read_data = file.read()
    print("Transcript data loaded successfully.")

    # Replace placeholder in user prompt template with transcript data
    user_prompt = user_prompt_template.replace("{{transcript_data}}", read_data)
    print("User prompt with replaced transcript data created successfully.")

    # Generate documentation using Claude Messages API
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Use a valid model name
            max_tokens=1024,  # Required
            system=system_prompt,  # Pass the system prompt here
            messages=[
                {"role": "user", "content": user_prompt}  # Only include "user" role here
            ]
        )
        # If response.content contains non-string elements, convert them to strings
        if isinstance(response.content, list):
            generated_text = "".join(str(item) for item in response.content)
        else:
            generated_text = str(response.content)
        
        print("Documentation generated successfully.")
    except Exception as e:
        print(f"Error during documentation generation: {e}")
        return

    # Save generated documentation to output path
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(generated_text)  # Ensure it's a single string
        print(f"Generated documentation saved successfully to: {output_path}")
    except Exception as e:
        print(f"Error saving generated documentation: {e}")

# Example usage:
system_prompt_path = r'D:\NYU codes\Audio journal\Prompts\System_prompt.txt'
user_prompt_path = r'D:\NYU codes\Audio journal\Prompts\User_prompt.txt'
raw_transcript_path = r'D:\NYU codes\Audio journal\raw_transcripts\temporary_transcript.txt'
output_path = r'D:\NYU codes\Audio journal\Blog_generated\content.txt'

generate_documentation_blog(system_prompt_path, user_prompt_path, raw_transcript_path, output_path)
