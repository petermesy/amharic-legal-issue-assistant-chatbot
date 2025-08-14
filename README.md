# 🇪🇹 Amharic QA System using Streamlit

This project is a simple Question Answering (QA) system built for Amharic-language documents. It uses sentence-transformer embeddings and a semantic search interface powered by Streamlit.

> ✅ Ask any question in Amharic and retrieve the most relevant passages from pre-embedded legal documents.

---

## 🚀 Live Demo

👉 [Launch the Streamlit App](https://share.streamlit.io/) 

---

## 📦 Features

- 🔍 **Multilingual Embedding** with `paraphrase-multilingual-mpnet-base-v2`
- 📚 **Amharic Legal Chunk Retrieval** from preprocessed `.jsonl` chunks
- ⚡ **Semantic Search** using cosine similarity on embedded vectors
- 🎈 **Fast & Lightweight UI** using Streamlit

---

## 📁 File Structure

# 🇪🇹 Amharic QA System using Streamlit

This project is a simple Question Answering (QA) system built for Amharic-language documents. It uses sentence-transformer embeddings and a semantic search interface powered by Streamlit.

> ✅ Ask any question in Amharic and retrieve the most relevant passages from pre-embedded legal documents.

---

## 🚀 Live Demo

👉 [Launch the Streamlit App](https://amharic-legal-question-answering.streamlit.app/) *(replace with your live URL once deployed)*

---

## 📦 Features

- 🔍 **Multilingual Embedding** with `paraphrase-multilingual-mpnet-base-v2`
- 📚 **Amharic Legal Chunk Retrieval** from preprocessed `.jsonl` chunks
- ⚡ **Semantic Search** using cosine similarity on embedded vectors
- 🎈 **Fast & Lightweight UI** using Streamlit

---

---

## 🧠 Model & Data

- **Embedding Model**: [`paraphrase-multilingual-mpnet-base-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2)
- **Chunked Dataset**: Legal document chunks from Amharic texts
  - `amharic-chunks-with-embeddings.jsonl` – Google Drive hosted
  - `amharic-sentences-points.pkl` – precomputed sentence embeddings

Files are auto-downloaded in the app via [`gdown`](https://pypi.org/project/gdown/).

---

## 🛠️ Installation (Local)

```bash
git clone https://github.com/ProfessorAbraham/amharic-streamlit-qa.git
cd amharic-streamlit-qa
pip install -r requirements.txt
streamlit run app.py

