#recommend.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import requests  # <-- ADDED: Need this for API calls

# --- Configuration for OMDb API ---
OMDB_API_KEY = "c365b9cc"  # Your OMDb API Key
OMDB_BASE_URL = "http://www.omdbapi.com/"
# -----------------------------------

# Load your dataset
df = pd.read_csv(r"C:\Users\HP\OneDrive\Desktop\movies.csv")

# Create similarity matrix only if it doesn't already exist
similarity_file_path = "data/similarity.csv"

# --- TF-IDF and Cosine Similarity Matrix Generation (Keep this logic) ---
if not os.path.exists(similarity_file_path):
    # Use 'overview' column for text features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['overview'].fillna(""))

    # Compute cosine similarity matrix
    #
    similarity = cosine_similarity(tfidf_matrix)

    # Save it to CSV
    os.makedirs("data", exist_ok=True)
    pd.DataFrame(similarity).to_csv(similarity_file_path, index=False, header=False)

# Load similarity matrix
similarity = pd.read_csv(similarity_file_path, header=None).values


# --- Movie poster URL function (UPDATED to use OMDb) ---
def get_movie_poster(movie_title):
    """
    Fetches the movie poster URL from the OMDb API using the title.
    """
    params = {
        'apikey': OMDB_API_KEY,
        't': movie_title,  # Search by title
        'r': 'json'
    }

    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # OMDb returns 'Response': 'True' on success and the URL in 'Poster'
        if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
            return data['Poster']  # This is the direct URL

        # If movie found but poster is 'N/A' or response is 'False'
        return None

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        # print(f"API Request failed for {movie_title}: {e}") # You can uncomment this for debugging
        return None


def recommend_movies(title, n=5):
    # Find closest match
    matches = df[df['title'].str.lower() == title.lower()]
    if matches.empty:
        # If no exact match, return search suggestions
        return search_movies(title)

    idx = matches.index[0]
    scores = list(enumerate(similarity[idx]))
    # Exclude the movie itself (score[0]) and take the top n
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n + 1]

    recommendations = [
        # Fetch the real poster URL for the recommended movies
        (df.iloc[i[0]]['title'], get_movie_poster(df.iloc[i[0]]['title'])) for i in scores
    ]
    return recommendations


def search_movies(query, n=5):
    """
    Returns top n movies matching the query using simple substring match.
    """
    query = query.lower()
    # Filter movies that contain the query
    matches = df[df['title'].str.lower().str.contains(query)].head(n)

    # Return top n results with posters
    results = [
        # Fetch the real poster URL for the search results
        (row['title'], get_movie_poster(row['title']))
        for _, row in matches.iterrows()
    ]

    if not results:
        results = [("No movies found.", None)]

    return results