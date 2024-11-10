import os
from transformers import AutoModelForCausalLM, AutoTokenizer

def generate_documentation_blog(system_prompt_path, user_prompt_path, raw_transcript_path, output_path):
    # Verify and load system prompt
    if not os.path.isfile(system_prompt_path):
        print(f"Error: System prompt file not found at {system_prompt_path}")
        return
    with open(system_prompt_path, 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    print("System prompt loaded successfully.")

    # Verify and load user prompt template
    if not os.path.isfile(user_prompt_path):
        print(f"Error: User prompt template file not found at {user_prompt_path}")
        return
    with open(user_prompt_path, 'r', encoding='utf-8') as file:
        user_prompt_template = file.read()
    print("User prompt template loaded successfully.")

    # Verify and load code snippet (transcript)
    if not os.path.isfile(raw_transcript_path):
        print(f"Error: Transcript file not found at {raw_transcript_path}")
        return
    with open(raw_transcript_path, 'r', encoding='utf-8') as file:
        read_data = file.read()
    print("Transcript data loaded successfully.")

    # Replace placeholder in user prompt template
    user_prompt = user_prompt_template.replace("{{transcript_data}}", read_data)
    print("User prompt with replaced transcript data created successfully.")

    # Initialize the model and tokenizer
    model_name = "bigcode/starcoder"  # Ensure this model is downloaded and accessible
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        print("Model and tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading model or tokenizer: {e}")
        return

    # Encode the input
    inputs = tokenizer(system_prompt + user_prompt, return_tensors="pt")

    # Generate the output
    try:
        outputs = model.generate(**inputs, max_length=1024, temperature=0.7)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Documentation generated successfully.")
    except Exception as e:
        print(f"Error during text generation: {e}")
        return

    # Save generated documentation to output file
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(generated_text)
        print(f"Generated documentation saved successfully to: {output_path}")
    except Exception as e:
        print(f"Error saving generated documentation: {e}")

# Example usage:
system_prompt_path = r'D:\NYU codes\Audio journal\Prompts\System_prompt.txt'
user_prompt_path = r'D:\NYU codes\Audio journal\Prompts\User_prompt.txt'
raw_transcript_path = r'D:\NYU codes\Audio journal\raw_transcripts\temporary_transcript.txt'
output_path = r'D:\NYU codes\Audio journal\Blog_generated\content.txt'

generate_documentation_blog(system_prompt_path, user_prompt_path, raw_transcript_path, output_path)
