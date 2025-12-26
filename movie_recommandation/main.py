#main.py
import streamlit as st
from movies_.main import movie_list
from recommend import recommend_movies, search_movies

st.set_page_config(page_title="MovieReco", page_icon="🎬")

st.title("🎬 MovieReco")

# --- Search input ---
query = st.text_input("Type a movie name to search:")

if query:
    st.subheader("Search Results:")
    results = search_movies(query, n=5)

    cols = st.columns(len(results))

    for i, (title, poster) in enumerate(results):
        with cols[i]:
            # FIX APPLIED HERE: Check if poster is a valid URL before displaying the image
            if poster and poster.strip():  # Check if poster is not None and not empty/whitespace
                st.image(poster, caption=title, width=120)
            else:
                # Display the title and a placeholder message if the poster is missing
                st.write(f"**{title}**")
                st.caption("Poster not available.")

# --- Dropdown for exact recommendation ---
selected_movie = st.selectbox("Or select a movie to get recommendations:", movie_list)

if st.button("Recommend"):
    st.subheader("Recommended Movies:")
    recommendations = recommend_movies(selected_movie)

    num_recommendations = len(recommendations)
    cols = st.columns(num_recommendations)

    for i, (title, poster) in enumerate(recommendations):
        with cols[i]:
            # FIX APPLIED HERE: Check if poster is a valid URL before displaying the image
            if poster and poster.strip():  # Check if poster is not None and not empty/whitespace
                st.image(poster, caption=title, width=120)
            else:
                # Display the title and a placeholder message if the poster is missing
                st.write(f"**{title}**")
                st.caption("Poster not available.")

