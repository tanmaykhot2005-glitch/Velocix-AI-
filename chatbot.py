import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# 🔥 Load cars database
def load_cars():
    with open("data/cars.json", "r", encoding="utf-8") as file:
        return json.load(file)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are Velocix AI, the official AI assistant of the Velocix AI website.

Your job is to help users with sports cars available on this website.

Rules:

- Answer only sports car related questions.
- Prefer information from the website database.
- If multiple cars match, recommend the best ones.
- Keep answers concise (3–8 lines unless more detail is requested).
- Be friendly and professional.

If someone asks anything unrelated, reply:

"I am Velocix AI. I only answer questions about sports cars and the Velocix AI website."
"""

def get_ai_response(user_message):

    # 🔥 Load cars from JSON
    cars = load_cars()

    # Convert to text for AI
    car_data = json.dumps(cars, indent=2)

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content":
                SYSTEM_PROMPT +
                "\n\nWebsite Car Database:\n" +
                car_data
            },

            {
                "role": "user",
                "content": user_message
            }

        ]

    )

    return completion.choices[0].message.content