import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_chatbot_response(stats_data, user_message):
    if not HAS_GENAI:
        return "The google-generativeai module is not installed. Please install it using 'pip install google-generativeai' to enable the AI."

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return (
            "No GEMINI_API_KEY environment variable found. "
            "Please set it to empower me to analyze your efficiency!"
        )
    
    genai.configure(api_key=api_key)
    
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
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error while analyzing your data: {e}"
