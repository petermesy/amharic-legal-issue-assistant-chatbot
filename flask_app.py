from flask import Flask, render_template, request, Response, redirect, url_for, session
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import torch
import os
from dotenv import load_dotenv
from copy import deepcopy

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"

device = "cuda" if torch.cuda.is_available() else "cpu"

embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
POINTS_FILE = "amharic_sentences_points.pkl"

def load_points():
    with open(POINTS_FILE, "rb") as f:
        return pickle.load(f)

points = load_points()

def local_similarity_search(query, points, limit=15):
    query_vector = embedding_model.encode(query)
    vectors = np.array([point["vector"] for point in points])
    payloads = [point["payload"] for point in points]
    similarities = np.dot(vectors, query_vector) / (
        np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector)
    )
    top_indices = np.argsort(similarities)[::-1][:limit]
    return [{"text": payloads[i]["text"], "score": float(similarities[i])} for i in top_indices]

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("Gemini API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
genai.configure(api_key=api_key)

# Store multiple chat sessions
@app.before_request
def make_session_permanent():
    session.permanent = True
    if "chat_history" not in session:
        session["chat_history"] = []
    if "chat_sessions" not in session:
        session["chat_sessions"] = []

@app.route("/", methods=["GET"])
def index():
    chat_sessions = session.get("chat_sessions", [])
    chat_history = session.get("chat_history", [])

    # Build previews (first user + first bot message snippets)
    chat_previews = []
    for sess in chat_sessions:
        if sess:
            user_msg = next((m["text"] for m in sess if m["role"] == "user"), "")
            bot_msg = next((m["text"] for m in sess if m["role"] == "bot"), "")
            preview = f"👤 {user_msg[:15]} | 🤖 {bot_msg[:15]}" if bot_msg else f"👤 {user_msg[:30]}"
            chat_previews.append(preview)
        else:
            chat_previews.append("Empty chat")

    return render_template(
        "index.html",
        chat_history=chat_history,
        chat_sessions=chat_sessions,
        chat_previews=chat_previews,
    )

@app.route("/stream", methods=["POST"])
def stream():
    query = request.json.get("query")
    if not query:
        return Response("No input", status=400)

    session["chat_history"].append({"role": "user", "text": query})
    session.modified = True

    results = local_similarity_search(query, points, limit=15)
    combined_text = "\n".join([r["text"] for r in results])

    prompt = f"""
ከዚህ በታች የቀረቡት አንቀጾችን በመመስረት፣ '{query}' ላይ አንድ አንቀጽ ውስጥ ያጠቃልሉ፡፡
አጭር አንድ አንቀጽ መልስ ብቻ ይስጡ።

{combined_text}

አንድ አንቀጽ መልስ፦
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt, stream=True)

    def event_stream():
        bot_text = ""
        for chunk in response:
            if chunk.text:
                bot_text += chunk.text
                yield f"data: {chunk.text}\n\n"

        # Save bot reply *after* full response
        if bot_text.strip():
            session["chat_history"].append({"role": "bot", "text": bot_text})
            session.modified = True

    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/new_chat", methods=["POST"])
def new_chat():
    if session.get("chat_history"):
        # Store current chat into chat_sessions
        session["chat_sessions"].append(deepcopy(session["chat_history"]))
    session["chat_history"] = []
    session.modified = True
    return redirect(url_for("index"))

@app.route("/load_chat/<int:index>", methods=["GET"])
def load_chat(index):
    sessions = session.get("chat_sessions", [])
    if 0 <= index < len(sessions):
        session["chat_history"] = deepcopy(sessions[index])
        session.modified = True
        return {"chat_history": session["chat_history"]}
    return {"chat_history": []}, 404

@app.route("/clear_chats", methods=["POST"])
def clear_chats():
    session["chat_sessions"] = []
    session["chat_history"] = []
    session.modified = True
    return {"status": "success"}


if __name__ == "__main__":
    app.run(debug=True)