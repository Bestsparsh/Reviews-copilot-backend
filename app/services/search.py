from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_top_k_similar(query, reviews, k=5):
    texts = [r.text for r in reviews]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(texts + [query])

    sims = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()

    top_idx = sims.argsort()[-k:][::-1]

    return [reviews[i] for i in top_idx]
