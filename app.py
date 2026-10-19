# import streamlit as st
# import pandas as pd
# import requests
# import pickle

# def fetch_poster(movie_id):
#   response =  requests.get('https://api.themoviedb.org/3/movie/{}?api_key=fd32aad783d62c3d5c0117639aaadaec'.format(movie_id))
#   data = response.json
#   return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# def recommend(movie):
#   movie_index = movies[movies['title'] == movie].index[0]
#   distances = similarity[movie_index]
#   movies_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]

#   recommended_movies = []
#   recommended_movies_posters = []
#   for i in movies_list:
#         movie_id = i[0]
#         recommended_movies.append(movies.iloc[i[0]].title)
#         recommended_movies_posters.append(fetch_poster(movie_id))
#   return recommended_movies,recommended_movies_posters


# movies_dict = pickle.load(open('movie_dict.pkl','rb'))

# similarity = pickle.load(open('similarity.pkl','rb'))

# movies = pd.DataFrame(movies_dict)


# st.title('Movie Recommender System')

# selected_movie_name = st.selectbox(
# 'How would you like to be contacted?',
# movies['title'].values
# )

# if st.button('Recommend'):
#     name,posters = recommend(selected_movie_name)

#     col1,col2,col3 = st.beta_columns(3)
#     with col1:
#         st.header("A cat")





import pickle
import streamlit as st
import requests
import pandas as pd

# -----------------------------------
# TMDB API configuration
# # -----------------------------------
# TMDB_API_KEY = "YOUR_TMDB_API_KEY"
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# -----------------------------------
# Fetch movie poster from TMDB
# -----------------------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    try:
        response = requests.get(
            url,
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US"
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"

        return None

    except requests.exceptions.HTTPError as e:
        st.warning(
            f"TMDB API error for movie ID {movie_id}: "
            f"{response.status_code}. Check your API key and request."
        )
        return None

    except requests.exceptions.RequestException as e:
        st.warning(
            f"Could not connect to TMDB for movie ID {movie_id}. "
            "Check your network connection."
        )
        return None

    except ValueError:
        st.warning("TMDB returned an invalid response.")
        return None


# -----------------------------------
# Recommend similar movies
# -----------------------------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]]["movie_id"]
        movie_name = movies.iloc[i[0]]["title"]

        poster_url = fetch_poster(movie_id)

        recommended_movie_names.append(movie_name)
        recommended_movie_posters.append(poster_url)

    return recommended_movie_names, recommended_movie_posters


# -----------------------------------
# Streamlit application
# -----------------------------------
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

st.header("Movie Recommender System")

# Load saved movie data and similarity matrix
try:
    with open("movie_dict.pkl", "rb") as file:
        movies_dict = pickle.load(file)

    with open("similarity.pkl", "rb") as file:
        similarity = pickle.load(file)

    movies = pd.DataFrame(movies_dict)

except FileNotFoundError:
    st.error(
        "Required files not found. Make sure movie_dict.pkl "
        "and similarity.pkl are in the same folder as app.py."
    )
    st.stop()

# Validate movie data
if "title" not in movies.columns or "movie_id" not in movies.columns:
    st.error("Movie data must contain 'title' and 'movie_id' columns.")
    st.stop()

if len(similarity) != len(movies):
    st.error(
        "The similarity matrix and movie dataset have different sizes."
    )
    st.stop()

movie_list = movies["title"].tolist()

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# -----------------------------------
# Display recommendations
# -----------------------------------
if st.button("Show Recommendation"):
    with st.spinner("Finding similar movies and fetching posters..."):
        recommended_movie_names, recommended_movie_posters = recommend(
            selected_movie
        )

    cols = st.columns(5)

    for col, name, poster in zip(
        cols,
        recommended_movie_names,
        recommended_movie_posters
    ):
        with col:
            st.write(name)

            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.write("Poster unavailable")
