from flask import Flask, render_template, request, Response, redirect, url_for
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Store all conversations in memory
chat_sessions = []  # list of sessions, each session = list of messages
current_session = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=current_session)

@app.route("/stream", methods=["POST"])
def stream():
    global current_session, chat_sessions

    user_input = request.json.get("query")
    if not user_input:
        return Response("No input provided", status=400)

    # Save user message
    current_session.append({"role": "user", "text": user_input})

    # Create model with streaming enabled
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(user_input, stream=True)

    def event_stream():
        bot_reply = ""
        for chunk in response:
            if chunk.text:
                bot_reply += chunk.text
                yield f"data: {chunk.text}\n\n"

        # Save final bot reply
        current_session.append({"role": "bot", "text": bot_reply})

    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/new_chat", methods=["POST"])
def new_chat():
    global current_session, chat_sessions
    if current_session:
        chat_sessions.append(current_session)
    current_session = []
    return redirect(url_for("index"))

@app.route("/load_chat/<int:index>", methods=["GET"])
def load_chat(index):
    global current_session, chat_sessions
    if 0 <= index < len(chat_sessions):
        current_session = chat_sessions[index][:]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
