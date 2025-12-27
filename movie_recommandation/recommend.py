import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import requests

# --- Configuration for OMDb API ---
OMDB_API_KEY = "c365b9cc"  # Your OMDb API Key
OMDB_BASE_URL = "http://www.omdbapi.com/"
# -----------------------------------

# 1. SETUP PATHS (Works on Windows and Streamlit Cloud)
# This finds the folder where this script is living
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Point to movies.csv in your GitHub repo
movies_path = os.path.join(BASE_DIR, "movies.csv")

# 2. LOAD DATASET
if os.path.exists(movies_path):
    df = pd.read_csv(movies_path)
else:
    # Fallback for local testing if file is missing
    raise FileNotFoundError(f"Could not find movies.csv at {movies_path}")

# 3. MANAGE SIMILARITY MATRIX
# Save/Load similarity.csv in the same folder
similarity_file_path = os.path.join(BASE_DIR, "similarity.csv")

if not os.path.exists(similarity_file_path):
    # Use 'overview' column for text features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['overview'].fillna(""))

    # Compute cosine similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Save it to CSV for faster loading next time
    pd.DataFrame(similarity_matrix).to_csv(similarity_file_path, index=False, header=False)

# Load the similarity matrix into memory
similarity = pd.read_csv(similarity_file_path, header=None).values


# --- Movie poster URL function (OMDb API) ---
def get_movie_poster(movie_title):
    """
    Fetches the movie poster URL from the OMDb API using the title.
    """
    params = {
        'apikey': OMDB_API_KEY,
        't': movie_title,
        'r': 'json'
    }

    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
            return data['Poster']

        return None

    except requests.exceptions.RequestException:
        return None


def recommend_movies(title, n=5):
    # Find closest match
    matches = df[df['title'].str.lower() == title.lower()]
    
    if matches.empty:
        # If no exact match, return search suggestions
        return search_movies(title)

    idx = matches.index[0]
    scores = list(enumerate(similarity[idx]))
    
    # Exclude the movie itself and take the top n
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n + 1]

    recommendations = [
        (df.iloc[i[0]]['title'], get_movie_poster(df.iloc[i[0]]['title'])) 
        for i in scores
    ]
    return recommendations


def search_movies(query, n=5):
    """
    Returns top n movies matching the query using simple substring match.
    """
    query = query.lower()
    matches = df[df['title'].str.lower().str.contains(query)].head(n)

    results = [
        (row['title'], get_movie_poster(row['title']))
        for _, row in matches.iterrows()
    ]

    if not results:
        results = [("No movies found.", None)]

    return results
