from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv
import atexit
import signal
import sys


# Load env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")

EXTRACTOR_API_KEY = os.getenv("GEMINI_EXTRACTOR_API_KEY")
if not EXTRACTOR_API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")

MODEL = "gemini-2.5-flash"
SYSTEM_INSTRUCTION = (
    "You are an AI assistant for a financial services company. "
    "Your role is to answer user queries about finance, banking, and investments. "
    "Be polite, clear, and professional."
)
CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.3,
)

client = genai.Client(api_key=API_KEY)
extractor = genai.Client(api_key=EXTRACTOR_API_KEY)

chat = client.chats.create(model=MODEL, config=CONFIG)


# Handle Exit
def cleanup():
    global client
    global extractor

    client.close()
    extractor.close()
    print("Thank you. Goodbye!")


def handle_signal(sig, frame):
    sys.exit(0)


# Register cleanup for both normal exit and Ctrl+C
atexit.register(cleanup)
signal.signal(signal.SIGINT, handle_signal)


chat_history = []
user_db = {}


def history_append(role: str, text: str):
    global chat_history
    chat_history.append(
        types.Content(role=role, parts=[types.Part.from_text(text=text)])
    )


def give_prompt(text_prompt: str) -> str:
    global chat_history
    global chat

    history_append("user", text_prompt)

    response = chat.send_message(text_prompt)

    history_append("model", response.text)

    return response.text


def extract_details(text_prompt: str) -> dict:
    global extractor

    extraction_prompt = f"""
      Analyze the following text from a user. Extract any important personal
      details such as name, account number, specific financial goal, 
      or contact information. 
      
      Respond in JSON format with keys "name", "account_number", "goal", 
      "contact", or "other_details". If no information is found for a key, 
      use null.

      Text: "{text_prompt}"
      
      JSON:
      """

    try:
        response = extractor.models.generate_content(
            model=MODEL,
            contents=[extraction_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"[Detail Extraction Failed: {e}]")
        return None


def update_db(new_details):
    global user_db
    has_new_info = False

    if not new_details:
        return False

    for key, value in new_details.items():
        if value and user_db.get(key) != value:
            user_db[key] = value
            has_new_info = True

    return has_new_info


def main():
    print("Welcome to AI Financial Support. How can I help you today?")
    print("(Type 'exit' to quit)")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            sys.exit(0)
            break
        elif user_input.lower() == "":
            print("Please Type Something First...")
            continue

        try:
            response = give_prompt(user_input)
            print(f"AI Support: {response}")

            new_details = extract_details(user_input)
            if update_db(new_details):
                print("Details Modified")

        except Exception as e:
            print(f"Error: Could not get response from AI. {e}")


if __name__ == "__main__":
    main()
