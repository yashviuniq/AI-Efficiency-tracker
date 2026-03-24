import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    # Try old library as fallback (if needed) but preferentially use new one
    try:
        import google.generativeai as genai_old
        HAS_GENAI = "old"
    except ImportError:
        HAS_GENAI = False

def get_chatbot_response(stats_data, user_message):
    if not HAS_GENAI:
        return "The google-genai module is not installed. Please install it using 'pip install google-genai' to enable the AI."

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return (
            "No GEMINI_API_KEY environment variable found. "
            "Please set it to empower me to analyze your efficiency!"
        )
    
    stats_text = ""
    if not stats_data:
        stats_text = "The user has no activities logged this week yet."
    else:
        for stat in stats_data:
            cat = stat.get('category', 'Unknown')
            target = stat.get('target_hours_per_week', 0)
            actual = stat.get('Actual Hours', 0)
            eff = stat.get('Efficiency %', 0)
            stats_text += f"- {cat}: Target={target}h, Actual={actual}h, Efficiency={eff}%\n"

    system_instruction = (
        "You are an AI Productivity Coach integrated into an Efficiency Tracker dashboard. "
        "Your goal is to help the user reflect on their time management and provide actionable advice. "
        "Below is a summary of the user's logged categories for this week:\n"
        f"{stats_text}\n"
        "Keep your responses concise, encouraging, and data-driven based on these stats."
    )
    
    try:
        if HAS_GENAI == True:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text
        else:
            # Fallback to old SDK if someone only has that
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel('gemini-3-flash-preview', system_instruction=system_instruction)
            response = model.generate_content(user_message)
            return response.text
            
    except Exception as e:
        return f"Sorry, I encountered an error while analyzing your data: {e}"
