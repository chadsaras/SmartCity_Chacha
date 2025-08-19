# specialist_agents.py

import google.generativeai as genai
import PIL.Image
import json
import os
from dotenv import load_dotenv

# --- Central Configuration ---
# Configure the API key once for all agents in this module.
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# --- Common Analysis Function ---
def _analyze_image_with_prompt(image: PIL.Image.Image, prompt: str, agent_name: str) -> dict:
    """A generic function to send an image and a specific prompt to Gemini."""
    print(f"🔬 Running {agent_name} Agent...")
    
    # Use the fast and multimodal Gemini 1.5 Flash model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
    
    # The request includes the specific agent's prompt and the image
    response = model.generate_content([prompt, image])
    
    try:
        # Clean the response to ensure it's valid JSON
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned_json_string)
        return result
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error decoding JSON from {agent_name}: {e}")
        print(f"Raw response from {agent_name}: {response.text}")
        return {"error": f"Failed to parse output from {agent_name}"}

# --- Specialist Agent Definitions ---

def analyze_pothole(image: PIL.Image.Image) -> dict:
    """Analyzes an image for potholes."""
    pothole_prompt = """
    You are an expert pothole detection system. Analyze the provided image.
    Your task is to determine ONLY if a pothole exists.
    - If you find one or more potholes, provide a brief, description and a severity score from 1 to 100 based on its size and potential hazard.
    - If there are NO potholes, you MUST return a severity score of 0 and a null description.
    Respond ONLY with a valid JSON object with the keys "description" and "severity_score".
    """
    return _analyze_image_with_prompt(image, pothole_prompt, "Pothole")

def analyze_trash(image: PIL.Image.Image) -> dict:
    """Analyzes an image for trash or litter."""
    trash_prompt = """
    You are an expert trash detection system. Analyze the provided image.
    Your task is to determine ONLY if trash, litter, or illegal dumping exists.
    - If you find trash, provide a brief, description of the debris and a severity score from 1 to 100 based on its volume and environmental impact.
    - If there is NO trash, you MUST return a severity score of 0 and a null description.
    Respond ONLY with a valid JSON object with the keys "description" and "severity_score".
    """
    return _analyze_image_with_prompt(image, trash_prompt, "Trash")

def analyze_graffiti(image: PIL.Image.Image) -> dict:
    """Analyzes an image for graffiti."""
    graffiti_prompt = """
    You are an expert graffiti detection system. Analyze the provided image.
    Your task is to determine ONLY if graffiti or vandalism exists.
    - If you find graffiti, provide a brief, description of the vandalism and a severity score from 1 to 100 based on its size and public visibility.
    - If there is NO graffiti, you MUST return a severity score of 0 and a null description.
    Respond ONLY with a valid JSON object with the keys "description" and "severity_score".
    """
    return _analyze_image_with_prompt(image, graffiti_prompt, "Graffiti")