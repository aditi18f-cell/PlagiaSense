import os
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")


def preprocess(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return " ".join(re.findall(r'\w+', text))


def kmp_search(pattern, text):
    return pattern in text


def rabin_karp(pattern, text):
    return pattern in text


def calculate_similarity(a, b):
    if not a.strip() or not b.strip():
        return 0
    matrix = TfidfVectorizer().fit_transform([a, b])
    return cosine_similarity(matrix[0:1], matrix[1:2])[0][0]


def highlight_matches(user_text, doc_text):
    doc_clean = preprocess(doc_text)
    matches = []

    for sentence in re.split(r'[.!?]+', user_text):
        sentence = sentence.strip()
        if len(sentence) < 8:
            continue

        words = preprocess(sentence).split()
        if not words:
            continue

        overlap = sum(1 for w in words if w in doc_clean) / len(words)
        if overlap >= 0.6:
            matches.append(sentence)

    return matches


def check_plagiarism(user_text):
    if not os.path.exists(DATASET_PATH):
        print("Couldn't find dataset at:", DATASET_PATH)
        return {"results": [], "top_file": "Dataset missing", "top_similarity": 0, "status": "Error"}

    clean_input = preprocess(user_text)
    results = []

    for filename in os.listdir(DATASET_PATH):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(DATASET_PATH, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                doc = f.read()
        except Exception as e:
            print(f"Skipping {filename}: {e}")
            continue

        similarity = calculate_similarity(clean_input, preprocess(doc))
        matched = highlight_matches(user_text, doc)

        results.append({
            "document": filename,
            "similarity": round(similarity * 100, 2),
            "kmp_match": kmp_search(clean_input, preprocess(doc)),
            "rabin_karp_match": rabin_karp(clean_input, preprocess(doc)),
            "matched_sentences": matched
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)

    top = results[0] if results else None
    top_file = top["document"] if top else "No files found"
    top_similarity = top["similarity"] if top else 0

    if top_similarity <= 20:
        status = "Low Plagiarism"
    elif top_similarity <= 50:
        status = "Medium Plagiarism"
    else:
        status = "High Plagiarism"

    return {"results": results, "top_file": top_file, "top_similarity": top_similarity, "status": status}