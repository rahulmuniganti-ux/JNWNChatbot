from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage (you can later replace with DB)
pending_questions = ["What is AI?", "What is DBMS?"]
learned_data = [
    {"question": "Hi", "answer": "Hello!"},
    {"question": "Bye", "answer": "Goodbye!"}
]

# 🔹 Admin Panel Route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global pending_questions, learned_data

    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')

        if question and answer:
            # Remove from pending
            if question in pending_questions:
                pending_questions.remove(question)

            # Add to learned data
            learned_data.append({
                "question": question,
                "answer": answer
            })

    return render_template(
        'admin.html',
        pending=pending_questions,
        learned=learned_data
    )

# 🔹 Edit Route
@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if request.method == 'POST':
        new_q = request.form.get('question')
        new_a = request.form.get('answer')

        if new_q and new_a:
            learned_data[index] = {
                "question": new_q,
                "answer": new_a
            }

        return redirect(url_for('admin'))

    item = learned_data[index]
    return f"""
        <h2>Edit</h2>
        <form method="post">
            Question: <input type="text" name="question" value="{item['question']}"><br>
            Answer: <input type="text" name="answer" value="{item['answer']}"><br>
            <button type="submit">Update</button>
        </form>
    """

# 🔹 Delete Route
@app.route('/delete/<int:index>')
def delete(index):
    if 0 <= index < len(learned_data):
        learned_data.pop(index)

    return redirect(url_for('admin'))

# 🔹 Logout (simple redirect)
@app.route('/logout')
def logout():
    return redirect(url_for('admin'))

# 🔹 Home (optional)
@app.route('/')
def home():
    return '<h2>Chatbot Running... Go to /admin</h2>'

# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)
