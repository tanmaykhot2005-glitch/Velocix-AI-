import os
import json

from groq import Groq
from dotenv import load_dotenv

from agent import TOOLS, search_cars

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are Velocix AI, the official AI assistant of the Velocix AI website.

Your job is to help users with sports cars available on this website.

Rules:

- Answer only sports car related questions.
- Use the search_cars tool whenever the user asks about specific cars,
  specs, or wants a recommendation — never guess numbers from memory.
- If multiple cars match, recommend the best ones and say why.
- Keep answers concise (3–8 lines unless more detail is requested).
- Be friendly and professional.

If someone asks anything unrelated, reply:

"I am Velocix AI. I only answer questions about sports cars and the Velocix AI website."
"""


def get_ai_response(user_message):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    first_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    response_message = first_response.choices[0].message
    tool_calls = response_message.tool_calls

    if not tool_calls:
        # No lookup needed — e.g. greetings or general chit-chat
        return response_message.content

    messages.append(response_message)

    for call in tool_calls:
        args = json.loads(call.function.arguments)
        matched_cars = search_cars(**args)

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": "search_cars",
            "content": json.dumps(matched_cars),
        })

    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )

    return final_response.choices[0].message.content