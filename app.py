from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import random
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback")


# -----------------------------
# Admin Credentials (hashed)
# -----------------------------
ADMIN_USERNAME = "prathima"
ADMIN_PASSWORD_HASH = generate_password_hash("prathima25")

# -----------------------------
# Load intents.json
# -----------------------------
with open("intents.json") as f:
    intents = json.load(f)

# -----------------------------
# Load learned data
# -----------------------------
def load_learned_data():
    if not os.path.exists("learned.json"):
        with open("learned.json", "w") as f:
            json.dump({"learned": [], "pending": []}, f)

    with open("learned.json") as f:
        return json.load(f)

# -----------------------------
# Chatbot logic (User cannot teach)
# -----------------------------

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
            if pattern.lower() == user_input:
                return random.choice(intent["responses"])

    # Unknown question → store for admin
    if user_input not in data["pending"]:
        data["pending"].append(user_input)
        with open("learned.json", "w") as f:
            json.dump(data, f, indent=2)

    return "Sorry,I don’t know,we provide the Answer in few days"


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
    user_message = request.json["message"]
    response = chatbot_response(user_message)
    return jsonify({"reply": response})

@app.route("/get", methods=["POST"])
def chatbot():

    user_message = request.json["message"].lower()

    for intent in intents ["intents"]:
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
        username = request.form["username"]
        password = request.form["password"]
        
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
        question = request.form["question"]
        answer = request.form["answer"]

        data["learned"].append({"question": question, "answer": answer})
        if question in data["pending"]:
            data["pending"].remove(question)

        with open("learned.json", "w") as f:
            json.dump(data, f, indent=2)

    return render_template("admin.html", learned=data["learned"], pending=data["pending"])

# -----------------------------
# Edit Learned Answer
# -----------------------------
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    if not session.get("admin"):
        return redirect(url_for("login"))

    data = load_learned_data()

    if request.method == "POST":
        data["learned"][index]["question"] = request.form["question"]
        data["learned"][index]["answer"] = request.form["answer"]

        with open("learned.json", "w") as f:
            json.dump(data, f, indent=2)

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
        with open("learned.json", "w") as f:
            json.dump(data, f, indent=2)
    return redirect(url_for("admin"))


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
