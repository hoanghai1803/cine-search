import pymongo
import nltk
import requests
from io import BytesIO
from PIL import Image
import certifi
import streamlit as st
from dotenv import load_dotenv
import os

from utils.cine import Cine

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

load_dotenv()
client = pymongo.MongoClient(os.getenv('DB_CONNECTION_STRING'), tlsCAFile=certifi.where())
db = client["movies_data"]
collection = db.movies
cine = Cine(collection)

results = []

first_query = False


def update_search_results(new_results):
    global results, first_query
    results = new_results
    first_query = True


def show_search_results():
    global results
    if len(results) > 0:
        st.markdown("<h2 style='text-align: center; color: #fff; font-style: italic'>Results</h2>",
                    unsafe_allow_html=True)
        for result in results:
            movie = collection.find_one({"movie_id": result})
            st.markdown(
                f"<h3 style='text-align: center; color: #fff; font-style: italic'>{movie.get('movie_name', '')}</h3>",
                unsafe_allow_html=True)
            movie_image_link = movie.get('movie_image', '')
            if movie_image_link:
                response = requests.get(movie_image_link)
                if response.status_code == 200:
                    col1, col2, col3 = st.columns([2, 3, 2])
                    with col1:
                        pass
                    with col3:
                        pass
                    with col2:
                        movie_image = Image.open(BytesIO(response.content))
                        st.image(movie_image, width=300)

            st.markdown(
                f"<p style='text-align: center; color: #fff; font-style: italic'>"
                f"{movie.get('movie_description', '')}</p>",
                unsafe_allow_html=True)
            st.markdown(
                f"<p style='text-align: center; color: #fff; font-style: italic'>"
                f"Rating star: {movie.get('rating_star', '')}</p>",
                unsafe_allow_html=True)
            st.markdown(
                f"<p style='text-align: center; color: #fff; font-style: italic'>"
                f"Vote count: {movie.get('vote_count', '').replace('(', '').replace(')', '')}</p>",
                unsafe_allow_html=True)

            st.markdown("<hr style='border-top: 1px solid #fff'>", unsafe_allow_html=True)
    else:
        if first_query:
            st.write("No results found.")


def app():
    st.snow()
    col1, col2, col3 = st.columns([1, 3, 1])
    image = Image.open('./assets/cine-search.png')
    with col1:
        pass
    with col2:
        st.image(image, width=400)
    with col3:
        pass

    st.markdown("<p style='text-align: center; color: #fff; font-style: italic'>CineSearch is your one-stop shop to "
                "find the perfect movie. Search by title or description and explore a world of "
                "cinematic possibilities.</p>",
                unsafe_allow_html=True)

    query = st.text_input("Search movies or tv shows:", key="query_input")

    if query:
        new_results = cine.cine_search(query)
        update_search_results(new_results)

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        pass
    with col2:
        pass
    with col3:
        pass
    with col5:
        pass
    with col6:
        pass
    with col7:
        pass
    with col4:
        if st.button("Search"):
            if query:
                new_results = cine.cine_search(query)
                update_search_results(new_results)
            else:
                update_search_results([])

    show_search_results()


if __name__ == '__main__':
    app()
