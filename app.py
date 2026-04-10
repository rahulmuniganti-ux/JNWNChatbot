from flask import Flask, request, jsonify, render_template
import json
import random
import os

app = Flask(__name__)

# Load intents
with open("intents.json") as file:
    intents = json.load(file)

# Load learned data
def load_learned_data():
    try:
        with open("learned.json") as file:
            return json.load(file)
    except:
        return {"learned": [], "pending": []}

# Chatbot logic
def chatbot_response(user_input):
    user_input = user_input.lower()
    data = load_learned_data()

    # Check learned answers
    for item in data["learned"]:
        if item["question"] in user_input:
            return item["answer"]

    # Check predefined intents
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])

    # Unknown question → store for admin
    if user_input not in data["pending"]:
        data["pending"].append(user_input)
        with open("learned.json", "w") as f:
            json.dump(data, f, indent=2)

    return "Sorry, I don’t know. We will provide the answer soon."

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    response = chatbot_response(user_message)
    return jsonify({"reply": response})

# Run app (VERY IMPORTANT for Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))