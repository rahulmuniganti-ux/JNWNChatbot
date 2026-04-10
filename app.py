from flask import Flask, request, jsonify, render_template
import json
import random
import os

app = Flask(__name__)

# Load intents
with open("intents.json") as file:
    intents = json.load(file)

# Load learned data safely
def load_learned_data():
    if not os.path.exists("learned.json"):
        return {"learned": [], "pending": []}
    with open("learned.json") as file:
        return json.load(file)

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

    # Store unknown questions
    if user_input not in data["pending"]:
        data["pending"].append(user_input)
        with open("learned.json", "w") as f:
            json.dump(data, f, indent=2)

    return "Sorry, I don’t know. We will provide the answer soon."

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Admin page
@app.route("/admin")
def admin():
    return render_template("admin.html")

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json["message"]
        response = chatbot_response(user_message)
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"reply": "Server error occurred"}), 500

# Run app (for Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
