# preprocess.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load data
df = pd.read_csv("../data/movies.csv")

# Combine features
df['combined'] = df['genres'].fillna('') + " " + df['overview'].fillna('')

# Vectorize
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['combined'])

# Compute similarity
similarity = cosine_similarity(tfidf_matrix)

# Save files
df.to_pickle("movies.pkl")


def open(param: object, param1: object) -> None:
    pass


pickle.dump(similarity, open("similarity.pkl", "wb"))
