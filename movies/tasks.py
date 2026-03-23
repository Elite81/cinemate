from celery import shared_task
from django.core.cache import cache
from .utils import get_popular_movies # Assuming your helpers are in utils.py
from .models import Movie, Like , Comment, User
from django.db import transaction


@shared_task
def update_popular_movies_cache():
    """
    Fetches popular movies from TMDB and stores them in Redis.
    """
    movies = get_popular_movies()
    print(movies)
    if movies:
        # Store in Redis for 30 minutes (1800 seconds)
        cache.set('popular_movies_list', movies, 1800)

    return f"Updated {len(movies)} movies in cache."



@shared_task
def toggle_like_async(user_id, tmdb_id):
    try:
        with transaction.atomic():
            # Use filter().first() instead of .get() to avoid the crash
            movie = Movie.objects.select_for_update().filter(tmdb_id=tmdb_id).first()
            
            if not movie:
                # OPTION A: Log it and skip
                return f"Fail: Movie {tmdb_id} not found in DB. Seed it first!"
                
                # OPTION B: Or trigger the 'fetch_movie' logic here if you have it
            
            user = User.objects.get(id=user_id)
            # ... rest of your toggle logic ...
            
    except Exception as e:
        return f"Error processing like: {str(e)}"

@shared_task
def save_comment_async(user_id, tmdb_id, content):
    movie = Movie.objects.get(tmdb_id=tmdb_id)
    user = User.objects.get(id=user_id)
    Comment.objects.create(user=user, movie=movie, content=content)
    return f"Comment saved for movie {tmdb_id}"



# @shared_task
# def toggle_like_async(user_id, tmdb_id):
#     with transaction.atomic():
#         movie = Movie.objects.select_for_update().get(tmdb_id=tmdb_id)
#         user = User.objects.get(id=user_id)

#         like_obj, created = Like.objects.get_or_create(
#             user=user, 
#             movie=movie, 
#             defaults={'is_like': True}
#         )

#         if not created:
#             if like_obj.is_like:
#                 like_obj.is_like = False
#                 movie.count_like = max(0, movie.count_like - 1)
#             else:
#                 like_obj.is_like = True
#                 movie.count_like += 1
#             like_obj.save()
#         else:
#             movie.count_like += 1
#             movie.save()
#     return f"User {user_id} toggled like for movie {tmdb_id}"
