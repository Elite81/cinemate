from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.forms.models import model_to_dict
from django.db import transaction
from django.http import JsonResponse
from django.core.cache import cache
from .tasks import * 
from .timer import *
from django.http import HttpResponse
from .utils import *
from .models import *
from django.views.decorators.cache import cache_page

# Create your views here.
# @measure_time('Index View')  # Example usage of the timer decorator
# def index(request):
#     cache_key = 'popular_movies_list'
#     movies = cache.get(cache_key)
    
#     if movies is None:
#         # Trigger the task to run in the background
#         update_popular_movies_cache.delay()
#         # Return empty list so the page loads instantly while the task runs
#         movies = [] 
        
#     context = {
#         'movies': movies, 
#         'genre_name': "Popular Movies"
#     }
#     return render(request, "movies/home.html", context)
    # return HttpResponse("<html><body>Quick Test</body></html>")

@measure_time('Index View')
def index(request):
    # Only hit local Redis
    movies = cache.get('popular_movies_list')
    
    # If cache is empty, just return [] and let the worker fix it later
    if movies is None:
        update_popular_movies_cache.delay()
        movies = []
    
    return render(request, "movies/home.html", {
        'movies': movies, 
        'genre_name': "Popular Movies"
    })

# searching with keyword
@measure_time('Search: ')
def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return render(request, 'movies/search_movies.html', {'movies': [], 'query': query})

    cache_key = f'search_{query.replace(" ", "_")}'
    results = cache.get(cache_key)

    if results is None:
        results = search_movies(query)
        cache.set(cache_key, results, 600) # Cache search for 10 mins

    return render(request, 'movies/search_movies.html', {'movies': results, 'query': query})

@measure_time('Movie Details')
def movie_details(request, tmdb_id):
    movie_cache_key = f'movie_data_{tmdb_id}'
    movie = cache.get(movie_cache_key)

    # 1. Handle Movie Data Cache
    if movie == "NOT_FOUND":
        raise Http404("Movie not found")
        
    if movie is None:
        # DB Lookup
        movie_obj = Movie.objects.filter(tmdb_id=tmdb_id).first()
        if not movie_obj:
            cache.set(movie_cache_key, "NOT_FOUND", 3600) # Cache the 404
            raise Http404("Movie not found")

        # Convert to dict for fast serialization
        movie = {
            "id": movie_obj.id,
            "title": movie_obj.title,
            "overview": movie_obj.overview,
            "tmdb_id": movie_obj.tmdb_id,
        }
        cache.set(movie_cache_key, movie, 60 * 60 * 24) # 24 Hour Cache

    # 2. Handle Social Data Cache (Likes)
    likes_cache_key = f'likes_count_{tmdb_id}'
    likes_count = cache.get(likes_cache_key)

    if likes_count is None:
        # Use the ID from our dict
        m_id = movie["id"]
        likes_count = Like.objects.filter(movie_id=m_id, is_like=True).count()
        cache.set(likes_cache_key, likes_count, 60 * 10) # 10 Minute Cache

    return render(request, 'movies/movie_detail.html', {
        "movie": movie,
        "likes_count": likes_count
    })

@login_required
def movie_favorites(request):
    if request.method == 'POST':
        
        fav_movie = request.POST['movie_id']   # getting the movie id
        fav_movie = the_movie_detail(fav_movie) if fav_movie else [] # getting the details of the movie
        
        # If the movie does not exist in the database, create a movie database
        movie, created = Movie.objects.get_or_create(
            tmdb_id=fav_movie['id'],
            defaults={'title':fav_movie['original_title'],
                    'overview':fav_movie['overview'],
                    'poster_path':fav_movie['poster_path'],
                    'backdrop_path':fav_movie['backdrop_path'],
                    'release_date':fav_movie['release_date'],
                    'vote_average':fav_movie['vote_average'],
                    'vote_count':fav_movie['vote_count'],
                    'popularity':fav_movie['popularity'],
                    'original_language':fav_movie['original_language'], 
                    'adult':fav_movie['adult'],
                    'video':fav_movie['video'],
                    'origin_country':fav_movie['origin_country'],
                    'spoken_languages':fav_movie.get('spoken_languages', []),
                    'homepage':fav_movie['homepage'],
                    'runtime':fav_movie['runtime']
                    } )
            
        # if the genre does not exists (which is actually impossible), then create it 
        for genre in fav_movie['genres']:
            genre_name=genre['name']
            tmbd_id=genre['id']
            genre_instance, _ = Genre.objects.get_or_create(name=genre_name, tmbd_id=tmbd_id) 
            movie.genres.add(genre_instance)
                    
        
        # creating the FavoriteMovie object
        my_fav_movie, created = FavoriteMovie.objects.get_or_create(user=request.user, movie=movie)
        
        if created:
            messages.success(request, f"{my_fav_movie.movie.title} added to favorites")
        else:
            messages.info(request, f"{my_fav_movie.movie.title} is already in your favorites")
        
        return redirect("my_fav_movies")
    
    # Getting all the user favorite movies from the database
    # movies= FavoriteMovie.objects.filter(user=request.user).order_by('-added_at')
    all_fav_movie=[]
    # for movie in movies:
    #     all_fav_movie.append(movie.movie)
    
    favorites = FavoriteMovie.objects.filter(user=request.user).select_related('movie').order_by('-added_at')
    for fav in favorites:
        all_fav_movie.append(fav.movie)

    return render(request, "movies/favorite_movies.html", {'fav_movies':all_fav_movie})



@login_required
def remove_from_favorites(request):
    # Deleting the movie from the database
    if request.method == 'POST':
        fav_movie = request.POST.get('movie_id') # getting the movie id

        # selecting the movie form the FavoriteMovie table
        movie_to_remove=get_object_or_404(FavoriteMovie, user=request.user, movie=fav_movie) 
        movie_title = movie_to_remove.movie.title # getting the title of the the movie for notification
        movie_to_remove.delete()
        messages.success(request, f"{movie_title} was removed from favorite")
        return redirect('my_fav_movies')


@login_required
def rate_movie(request, tmdb_id):
    # User rate a movie
    if request.method != "POST":
        return redirect("movie_detail", tmdb_id=tmdb_id)
    
    score = int(request.POST.get('score', 0)) # getting the score of the movie
    if score < 1 or score > 10:
        messages.error(request, "score must be between 1 and 10")
        return redirect("movie_detail", tmdb_id=tmdb_id)

    movie = Movie.objects.filter(tmdb_id=tmdb_id).first() # getting the movie

    # if the movie does not exist in the table we create it
    if not movie:
        defaults = get_movie_defaults(tmdb_id) 
        if not defaults:
            messages.error(request, "Unable to load movie details")
            return redirect('index')

        # creating a movie object
        movie = Movie.objects.create(
            tmdb_id=tmdb_id,
            **{k: v for k, v in defaults.items() if k != 'genres'}
        )

        # Getting the genre, if the genre does not exists (which is actually impossible), then create it 
        for genre in defaults['genres']:
            genre_name=genre['name']
            tmbd_id=genre['id']
            genre_instance, _ = Genre.objects.get_or_create(name=genre_name, tmbd_id=tmbd_id) 
            movie.genres.add(genre_instance)

    # Creating the rating object
    Ratings.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={"score":score}
    )
    
    messages.success(request, "Rating saved successfully")
    return redirect("movie_detail", tmdb_id=movie.tmdb_id)



def comments(request, tmdb_id):
    if request.method == 'POST':
        # getting the movie from the database, if the movie object does not exists create.
        movie = Movie.objects.filter(tmdb_id=tmdb_id).first() 
        if not movie:
            defaults = get_movie_defaults(tmdb_id)
            if not defaults:
                raise Http404("Movie not found")
            movie = Movie.objects.create(tmdb_id=tmdb_id, **defaults)

        content = request.POST.get("content", "").strip() # getting the striped comment submitted by the user
        
        # if there is a comment then then create a comment object
        if content:
            Comment.objects.create(user=request.user, movie=movie, content=content)
        return redirect("movie_detail", tmdb_id=tmdb_id)
    return redirect("movie_detail", tmdb_id=tmdb_id)


# Getting movie by genres
def genres_movie(request, genre_name):
    genre = get_object_or_404(Genre, name=genre_name)
    movies = get_movie_by_genres(genre_id=genre.tmbd_id)
    
    return render(request, "movies/home.html", {'movies':movies, "genre_name":genre_name})

@login_required
def toggle_like(request, tmdb_id):
    # the function does not actually accept a get request 
    if request.method != 'POST':
        return JsonResponse({'error':'Invalid request'}, status=400)
    
    user_id = request.user.id

    #1. Trigger Celery to handle the heavy DB work (Neon)
    toggle_like_async.delay(user_id, tmdb_id)

    # 2. Optimistically update Redis cache so the UI looks updated immediately
    # (Optional: Increment/Decrement a local Redis counter here if needed)
    cache.delete(f'likes_count_{tmdb_id}')

    return redirect('movie_detail', tmdb_id=tmdb_id)

    # # lock the  selected row in the database for the duration of the transaction, for efficiency
    # movie = Movie.objects.select_for_update().get(tmdb_id=tmdb_id)  
    
    # like_obj, created = Like.objects.get_or_create(user=user, movie=movie, defaults={'is_like':True})
    
    # # Handling the like and like_count
    # if not created: # If the user has already liked or interred with the movie
        
    #     # if liked currently, then unlike it and decrement count
    #     if like_obj.is_like:
    #         like_obj.is_like = False
    #         movie.count_like = max(0, movie.count_like -1)

    #     # If unlike currently, then liked it and increment count
    #     else:
    #         like_obj.is_like = True
    #         movie.count_like += 1
    
    #     like_obj.save()
    #     movie.save()

    # else:
    #     # first time like and increment count
    #     movie.count_like += 1
    #     movie.save()
    
    # return redirect('movie_detail', tmdb_id=tmdb_id)


# Fetching all liked movies
@login_required
def liked_movies(request):
    liked_relations = Like.objects.filter(user=request.user, is_like=True).select_related('movie')
    movies = [rel.movie for rel in liked_relations]
    return render(request, 'movies/all_liked_movies.html', {'movies': movies})
         


@login_required
def add_comment(request, tmdb_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Send to Celery instantly!
            save_comment_async.delay(request.user.id, tmdb_id, content)
            
    return redirect('movie_detail', tmdb_id=tmdb_id)

         
