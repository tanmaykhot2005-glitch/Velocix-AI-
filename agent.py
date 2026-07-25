import os
import re
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_cars():
    with open("data/cars.json", "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================================
# HELPERS — your JSON stores numbers as formatted strings
# ("$608,000", "340 km/h", "0-100 km/h in 2.5 sec"), so the
# agent needs these to filter/sort on real numeric values.
# ==========================================================

def parse_price(price_str):
    digits = re.sub(r"[^\d]", "", price_str)
    return int(digits) if digits else None


def parse_top_speed(top_speed_str):
    match = re.search(r"(\d+)", top_speed_str)
    return int(match.group(1)) if match else None


def parse_acceleration(acc_str):
    match = re.search(r"(\d+\.?\d*)\s*sec", acc_str)
    return float(match.group(1)) if match else None


# ==========================================================
# THE ACTUAL TOOL — this is the function the LLM is allowed
# to call. It runs real filtering logic on your database.
# ==========================================================

def search_cars(brand=None, category=None, min_horsepower=None,
                 max_price=None, max_acceleration=None, min_top_speed=None):
    cars = load_cars()
    results = []

    for car in cars:
        if brand and brand.lower() not in car["brand"].lower():
            continue
        if category and category.lower() != car["category"].lower():
            continue
        if min_horsepower and car["horsepower"] < min_horsepower:
            continue

        price = parse_price(car["price"])
        if max_price and price and price > max_price:
            continue

        accel = parse_acceleration(car["acceleration"])
        if max_acceleration and accel and accel > max_acceleration:
            continue

        top_speed = parse_top_speed(car["top_speed"])
        if min_top_speed and top_speed and top_speed < min_top_speed:
            continue

        results.append(car)

    # Rank by horsepower so the strongest matches surface first
    results.sort(key=lambda c: c["horsepower"], reverse=True)
    return results[:5]


# JSON schema describing the tool to the LLM — this is what
# lets the model decide *when* and *how* to call search_cars.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_cars",
            "description": "Search the sports car database using any combination of filters. Use this whenever the user describes what kind of car they want.",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand": {"type": "string", "description": "Car brand, e.g. Ferrari, BMW"},
                    "category": {"type": "string", "description": "e.g. Hypercar, Supercar, Sports Car"},
                    "min_horsepower": {"type": "number", "description": "Minimum horsepower required"},
                    "max_price": {"type": "number", "description": "Maximum price in USD"},
                    "max_acceleration": {"type": "number", "description": "Maximum 0-100 km/h time in seconds"},
                    "min_top_speed": {"type": "number", "description": "Minimum top speed in km/h"},
                },
                "required": [],
            },
        },
    }
]

AGENT_SYSTEM_PROMPT = """
You are the Velocix AI search agent. Users describe what car they want in
plain language. Call the search_cars tool with the right filters extracted
from their message, then look at the returned cars and recommend the best
1-3 matches with a short reason for each. If nothing matches, say so and
suggest loosening a filter.
"""


def run_agent(user_query):
    """
    The agentic loop:
    1. Send the user's free-text query + available tools to the LLM
    2. LLM decides whether/how to call search_cars (decision)
    3. We execute the tool call for real, on the actual database (action)
    4. LLM sees the results and writes a reasoned recommendation (reasoning)
    """
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
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
        # Model didn't think a search was needed (e.g. small talk)
        return response_message.content, []

    # Only one tool exists right now, but loop in case of multiple calls
    messages.append(response_message)
    matched_cars = []

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

    return final_response.choices[0].message.content, matched_cars;