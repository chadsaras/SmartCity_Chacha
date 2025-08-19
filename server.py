# main.py

import PIL.Image
import json
import os # <-- Add this import
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import our specialist agent functions
from specialist_agents import analyze_pothole, analyze_trash, analyze_graffiti

# --- LangChain Imports ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# --- Central Configuration for LangChain ---
# Get the API key, just like in the other file
from dotenv import load_dotenv

# --- Central Configuration ---
# Configure the API key once for all agents in this module.
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def calculate_cumulative_severity(results: dict) -> int:
    """Calculates a weighted cumulative severity score based on agent results."""
    
    # Define the weights based on priority. These must sum to 1.0.
    weights = {
        "pothole": 0.5,  # 50%
        "trash": 0.3,    # 30%
        "graffiti": 0.2  # 20%
    }

    # Get scores, defaulting to 0 if an agent failed or returned no score
    pothole_score = results.get("pothole", {}).get("severity_score", 0)
    trash_score = results.get("trash", {}).get("severity_score", 0)
    graffiti_score = results.get("graffiti", {}).get("severity_score", 0)

    # Calculate the weighted score
    cumulative_score = (
        (pothole_score * weights["pothole"]) +
        (trash_score * weights["trash"]) +
        (graffiti_score * weights["graffiti"])
    )
    
    # Return the score as a whole number
    return round(cumulative_score)


def orchestrate_analysis(image_path: str):
    """
    Orchestrates the parallel analysis, calculates a cumulative score,
    and generates a final summary using LangChain.
    """
    print(f"--- 🚀 Starting Orchestration for {image_path} ---")

    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return {"error": f"File not found at {image_path}"}

    # --- Parallel Execution of Specialist Agents ---
    agents = {
        "pothole": analyze_pothole,
        "trash": analyze_trash,
        "graffiti": analyze_graffiti,
    }
    
    all_results = {}

    with ThreadPoolExecutor(max_workers=len(agents)) as executor:
        future_to_agent = {executor.submit(agent_func, img): name for name, agent_func in agents.items()}
        
        for future in as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            try:
                result = future.result()
                all_results[agent_name] = result
            except Exception as exc:
                print(f"{agent_name} agent generated an exception: {exc}")
                all_results[agent_name] = {"error": str(exc)}

    print("\n--- ✅ All Agents Completed ---")

    # --- NEW: Calculate and add the cumulative score ---
    cumulative_score = calculate_cumulative_severity(all_results)
    all_results["cumulative_severity_score"] = cumulative_score
    # --- END NEW SECTION ---

    print("Aggregated JSON Report:")
    print(json.dumps(all_results, indent=2))

    # --- LangChain Summarization ---
    print("\n--- 🧠 Generating Final Summary with LangChain ---")

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=api_key)

    # --- UPDATED PROMPT ---
    # The prompt is updated to be aware of the new cumulative score.
    summary_prompt_template = """
    You are a city infrastructure and sanitation analyst. Based on the following JSON report from specialist AI agents,
    write a concise, one-paragraph executive summary for a city manager.
    
    Focus on the most severe issues found. If all severity scores are 0, state that the area is clear of issues.

    JSON Report:
    {json_report}

    Executive Summary:
    """
    prompt = ChatPromptTemplate.from_template(summary_prompt_template)

    summarization_chain = prompt | llm

    final_summary_message = summarization_chain.invoke({
        "json_report": json.dumps(all_results, indent=2)
    })

    all_results["executive_summary"] = final_summary_message.content
    return all_results




