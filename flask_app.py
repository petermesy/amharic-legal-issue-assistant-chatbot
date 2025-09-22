from flask import Flask, render_template, request, session
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import torch
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session

# Use GPU if available
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
    query_vector = np.array(query_vector)
    similarities = np.dot(vectors, query_vector) / (
        np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector)
    )
    top_indices = np.argsort(similarities)[::-1][:limit]
    results = [
        {"text": payloads[i]["text"], "score": float(similarities[i])}
        for i in top_indices
    ]
    return results

def summarize_with_gemini(matches, query, temperature=2):
    combined_text = "\n".join([match["text"] for match in matches])
    prompt = f"""
    ከዚህ በታች የቀረቡት አንቀጾችን በመመስረት፣ '{query}' ላይ አንድ አንቀጽ ውስጥ ያጠቃልሉ፡፡
    አጭር አንድ አንቀጽ መልስ ብቻ ይስጡ።

    {combined_text}

    አንድ አንቀጽ መልስ፦
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY as an environment variable.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt,
        generation_config={"temperature": temperature}
    )
    return response.text.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    query = ""
    summary = ""
    if request.method == 'POST':
        query = request.form['query']
        session["chat_history"].append({"role": "user", "text": query})
        results = local_similarity_search(query, points, limit=15)
        summary = summarize_with_gemini(results, query)
        print("Bot answer:", summary)
        print("Session history:", session["chat_history"])
        session["chat_history"].append({"role": "bot", "text": summary})
        session.modified = True
    return render_template('index.html', chat_history=session.get("chat_history", []), query=query)

if __name__ == '__main__':
    app.run(debug=True)
