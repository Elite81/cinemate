import requests
from django.conf import settings
from .models import *


''' 
 Note: Logic and explanations in this file were refined with assistance from ChatGPT (OpenAI).
'''


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

from .models import Movie
from django.forms.models import model_to_dict

def get_movie_defaults(tmdb_id):
    # 1. Check Database first
    movie_instance = Movie.objects.filter(tmdb_id=tmdb_id).first()
    if movie_instance:
        # Returns the model data as a dictionary so the calling function stays consistent
        return model_to_dict(movie_instance)
    
    # 2. Fetch from API
    details = the_movie_detail(tmdb_id)
    
    # 3. Robustness Check: Ensure 'details' is a dictionary and not an error string
    if not details or not isinstance(details, dict):
        return None
    
    # 4. Return the cleaned dictionary
    return {
        "title": details.get("title"),
        "original_title": details.get("original_title"),
        "overview": details.get("overview"),
        "poster_path": details.get("poster_path"),
        "backdrop_path": details.get("backdrop_path"), # Fixed extra space
        "release_date": details.get("release_date"),
        "vote_average": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "popularity": details.get("popularity"),
        "original_language": details.get("original_language"),
        "adult": details.get("adult"),
        "video": details.get("video"),
        "genres": details.get("genres", []), # Default to empty list
        "origin_country": details.get("origin_country"),
        "spoken_languages": details.get("spoken_languages"),
        "homepage": details.get("homepage"),
        "runtime": details.get("runtime")
    }

    
def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code ==200:
        return response.json().get("genres", [])
    return []

def sync_genres():
    for genre in get_genres():
        print(genre)
        Genre.objects.update_or_create(tmbd_id=genre['id'], defaults={'name':genre['name']})
        print("genres Syncronized")


def get_movie_by_genres(genre_id, page=1):
    url = (
        f"https://api.themoviedb.org/3/discover/movie"
        f"?api_key={settings.TMDB_API_KEY}"
        f"&language=en-US"
        f"&sort_by=popularity.desc"
        f"&with_genres={genre_id}"
        f"&page={page}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    return []
    