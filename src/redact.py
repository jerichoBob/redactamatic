import os
import json
import re
import requests
import uuid

# Function to interact with the local Ollama model
def query_ollama(prompt, model="mistral-nemo"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    print(response)
    return response.json()['response']

# Function to redact PII/PHI and create mapping
def redact_pii_phi(text):
    prompt = f"""
Analyze the following text and identify any Protected Health Information (PHI) or Personally Identifiable Information (PII). 
For each piece of information, specify the type (e.g., Name, SSN, Date, Address, etc.) and the text it corresponds to.
Present the results in a JSON format.

Text:
{text}

JSON format example:
{{
    "entities": [
        {{"type": "Name", "text": "John Doe"}},
        {{"type": "SSN", "text": "123-45-6789"}},
        {{"type": "Date", "text": "01/15/2023"}}
    ]
}}
    """
    
    response = query_ollama(prompt)
    print(f"response: {response}")
    
    # Parse the JSON response
    pii_phi_instances = json.loads(response)['entities']
    
    redacted_text = text
    pii_phi_mapping = {}
    
    for instance in pii_phi_instances:
        print(f"instance: {instance}")
        pii_type = instance['type']
        value = instance['text']
        unique_id = str(uuid.uuid4())
        
        # Replace the value with the unique ID in the text
        redacted_text = redacted_text.replace(value, f"[{unique_id}]")
        
        # Store the mapping
        pii_phi_mapping[unique_id] = {
            "type": pii_type,
            "value": value
        }
    
    return redacted_text, pii_phi_mapping

# Main function to process the file
def process_file(input_file, output_file, mapping_file):
    with open(input_file, 'r') as f:
        original_text = f.read()
    
    redacted_text, pii_phi_mapping = redact_pii_phi(original_text)
    
    # Write the redacted text to a new file
    with open(output_file, 'w') as f:
        f.write(redacted_text)
    
    # Write the PII/PHI mapping to a JSON file
    with open(mapping_file, 'w') as f:
        json.dump(pii_phi_mapping, f, indent=2)


def get_versioned_filename(filename):
    base, ext = os.path.splitext(filename)
    version = 1
    new_filename = f"{base}-v{version:02d}{ext}"
    print(f"new_filename: {new_filename}")
    while os.path.exists(new_filename):
        version += 1
        new_filename = f"{base}-v{version:02d}{ext}"
    return new_filename
# Example usage
if __name__ == "__main__":
    input_file = "../data/PII-sample-1.txt"


    output_file = "../data/redacted-PII-sample-1.txt"
    mapping_file = "../data/pii_phi_mapping.json"

    if os.path.exists(output_file):
        output_file = get_versioned_filename(output_file)
    if os.path.exists(mapping_file):
        mapping_file = get_versioned_filename(mapping_file)
    
    process_file(input_file, output_file, mapping_file)
    print(f"Redacted file saved as {output_file}")
    print(f"PII/PHI mapping saved as {mapping_file}")