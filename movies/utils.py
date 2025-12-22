import requests
from django.conf import settings




# Generated from chatGPT
# Fetch popular movies
def get_popular_movies(page=1):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={settings.TMDB_API_KEY}&language=en-US&page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    return []

# Search movies by name
def search_movies(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    return []


def the_movie_detail(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&query=append_to_response=cretid,videos"
    response = requests.get(url)
    if response.status_code == 200:
        movie = response.json()
    else:
        movie="No result matches your query"
    return movie