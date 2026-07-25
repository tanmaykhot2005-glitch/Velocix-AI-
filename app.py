from collections import Counter
from flask import Flask, render_template, request, jsonify
from chatbot import get_ai_response
import json

app = Flask(__name__)

def load_cars():
    with open("data/cars.json", "r", encoding="utf-8") as file:
        return json.load(file)

# ===========================
# HOME PAGE
# ===========================
@app.route("/")
def home():
    return render_template("index.html")


# ===========================
# BRANDS PAGE
# ===========================
@app.route("/brands")
def brands():

    cars = load_cars()

    brand_count = Counter(car["brand"] for car in cars)

    brands = []

    for brand, count in brand_count.items():

        brands.append({
            "name": brand,
            "models": count
        })

    brands = sorted(brands, key=lambda x: x["name"])

    return render_template("brands.html", brands=brands)
# ===========================
# CARS PAGE
# ===========================
@app.route("/cars")
def cars():

    cars = load_cars()

    brand = request.args.get("brand")

    if brand:
        cars = [
            car for car in cars
            if car["brand"].lower() == brand.lower()
        ]

    return render_template(
        "cars.html",
        cars=cars,
        selected_brand=brand
    )

# ===========================
# CAR DETAILS PAGE
# ===========================
@app.route("/car/<brand>/<model>")
def car_details(brand, model):

    cars = load_cars()

    selected_car = None

    for car in cars:

        if (
            car["brand"].lower() == brand.lower()
            and
            car["model"].replace(" ","-").lower() == model.lower()
            ):
            selected_car = car
            break 

    if selected_car is None:
        return "Car not found",404

    related_cars =[]

    for car in cars:

        if (
            car["brand"] == selected_car["brand"]
            and car["model"] != selected_car["model"]
        ):
            related_cars.append(car)
    return render_template(
        "car_details.html",
        car=selected_car,
        related_cars=related_cars
    )
        
# ===========================
# GALLERY PAGE
# ===========================
@app.route("/gallery")
def gallery():

    cars = load_cars()

    return render_template(
        "gallery.html",
        cars=cars
    )

# ===========================
# AI CHATBOT PAGE
# ===========================
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# ===========================
# CHAT API
# ===========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message", "")

    try:

        reply = get_ai_response(message)

    except Exception as e:

        reply = f"Error: {str(e)}"

    return jsonify({

        "reply": reply

    })
# ===========================
# AI AGENT PAGE
# ===========================

@app.route("/agent")
def agent():
    query = request.args.get("query", "")
    cars = load_cars()

    results = []

    if query:

        search_text = query.lower()

        for car in cars:

            if (
                search_text in car["brand"].lower()
                or search_text in car["model"].lower()
            ):
                results.append(car)

    return render_template(
        "agent.html",
        query=query,
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True)
