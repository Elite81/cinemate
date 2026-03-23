from django.core.cache import cache
from movies.models import Genre

# def movie_genres(request):
#     # Try to get genres from cache first
#     genres = cache.get('global_movie_genres')
    
#     if genres is None:
#         # If not in cache, fetch from DB and convert to list to 'force' execution
#         genres = list(Genre.objects.all())
#         # Store in cache for 24 hours (86400 seconds)
#         cache.set('global_movie_genres', genres, 86400)
    
#     return {"all_genres": genres}

def movie_genres(request):
    genres = cache.get('global_movie_genres')
    if genres is None:
        print("!!! CACHE MISS: HITTING NEON DB !!!") # <--- Add this
        genres = list(Genre.objects.all())
        cache.set('global_movie_genres', genres, 86400)
    return {"all_genres": genres}