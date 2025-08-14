import streamlit as st
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import torch
import os

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load embedding model (no need to manually assign to device anymore)
embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

# Path to the .pkl file
POINTS_FILE = "amharic_sentences_points.pkl"

# Load precomputed sentence embeddings
@st.cache_resource
def load_points():
    with open(POINTS_FILE, "rb") as f:
        return pickle.load(f)

points = load_points()

# Local similarity search using cosine similarity
def local_similarity_search(query, points, limit=5):
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

# Summarize using Gemini
def summarize_with_gemini(matches, query, temperature=0.2):
    combined_text = "\n".join([match["text"] for match in matches])
    prompt = f"""
    ከዚህ በታች የቀረቡት አንቀጾችን በመመስረት፣
    '{query}' ላይ አጭር አማርኛ መልስ አዘጋጅ፡፡

    {combined_text}

    አጭር መልስ፦
    """
    genai.configure(api_key=st.secrets["AIzaSyA0a3ld-hCKxrsnTCYZA_aU8JJdENqhHSg"])
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt,
        generation_config={"temperature": temperature}
    )
    return response.text.strip()

# Streamlit UI
st.title("Amharic QA System")

query = st.text_input("የጥያቄዎትን ጽሑፍ ያስገቡ (Enter your Amharic question):")

if query:
    results = local_similarity_search(query, points, limit=5)
    st.subheader("🔎 Top 5 Matches")
    for r in results:
        st.write(f"**Score:** {r['score']:.3f}")
        st.write(r['text'])
        st.markdown("---")

    if st.button("Summarize with Gemini"):
        summary = summarize_with_gemini(results, query)
        st.subheader("📝 አጭር መጠቃለያ")
        st.write(summary)
