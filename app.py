from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import random
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__) 
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key_change_in_production")

# -----------------------------
# Admin Credentials (hashed)
# -----------------------------
ADMIN_USERNAME = "prathima"
ADMIN_PASSWORD_HASH = generate_password_hash("prathima25")

# -----------------------------
# Load intents.json
# -----------------------------
def load_intents():
    try:
        intents_path = os.path.join(os.path.dirname(__file__), "intents.json")
        with open(intents_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: intents.json not found!")
        return {"intents": []}

intents = load_intents()

# -----------------------------
# Load learned data
# -----------------------------
def load_learned_data():
    learned_path = os.path.join(os.path.dirname(__file__), "learned.json")
    
    if not os.path.exists(learned_path):
        with open(learned_path, "w") as f:
            json.dump({"learned": [], "pending": []}, f)

    with open(learned_path, "r") as f:
        return json.load(f)

def save_learned_data(data):
    learned_path = os.path.join(os.path.dirname(__file__), "learned.json")
    with open(learned_path, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# Chatbot logic (User cannot teach)
# -----------------------------
def chatbot_response(user_input):
    user_input = user_input.lower()
    data = load_learned_data()

    # Check learned answers
    for item in data["learned"]:
        if item["question"].lower() in user_input:
            return item["answer"]

    # Check predefined intents
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])

    # Unknown question → store for admin
    if user_input not in [q.lower() for q in data["pending"]]:
        data["pending"].append(user_input)
        save_learned_data(data)

    return "Sorry, I don't know, we will provide the answer in a few days"

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = chatbot_response(user_message)
    return jsonify({"reply": response})

@app.route("/get", methods=["POST"])
def chatbot():
    user_message = request.json.get("message", "").lower()

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_message:
                return jsonify({"reply": random.choice(intent["responses"])})

    return jsonify({"reply": "Sorry, I didn't understand your question."})

# -----------------------------
# Admin Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# -----------------------------
# Admin Panel
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    data = load_learned_data()

    # Admin teaches new pending question
    if request.method == "POST":
        question = request.form.get("question", "")
        answer = request.form.get("answer", "")

        if question and answer:
            data["learned"].append({"question": question, "answer": answer})
            if question in data["pending"]:
                data["pending"].remove(question)

            save_learned_data(data)

    return render_template("admin.html", learned=data["learned"], pending=data["pending"])

# -----------------------------
# Edit Learned Answer
# -----------------------------
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    if not session.get("admin"):
        return redirect(url_for("login"))

    data = load_learned_data()

    if index >= len(data["learned"]):
        return redirect(url_for("admin"))

    if request.method == "POST":
        data["learned"][index]["question"] = request.form.get("question", "")
        data["learned"][index]["answer"] = request.form.get("answer", "")
        save_learned_data(data)
        return redirect(url_for("admin"))

    item = data["learned"][index]
    return render_template("edit.html", item=item, index=index)

# -----------------------------
# Delete Learned Answer
# -----------------------------
@app.route("/delete/<int:index>")
def delete(index):
    if not session.get("admin"):
        return redirect(url_for("login"))

    data = load_learned_data()
    if index < len(data["learned"]):
        data["learned"].pop(index)
        save_learned_data(data)
    return redirect(url_for("admin"))

# -----------------------------
# Health Check (for deployment)
# -----------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
