from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .utils import *
from .models import *


# Create your views here.
def index(request):
    movies = get_popular_movies()
    return render(request, "movies/home.html", {'movies':movies})


def search(request):
    query = request.GET.get('q', '')
    results = search_movies(query) if query else []
    return render(request, 'movies/search_movies.html', {'movies':results, 'query':query})


def movie_detail(request, tmdb_id):
    movie = Movie.objects.filter(
        tmdb_id=tmdb_id,
    ).first()
    
    if not movie:
        defaults = get_movie_defaults(tmdb_id)
        if not defaults:
            raise Http404("movie not found")
        movie = Movie.objects.create(
            tmdb_id=tmdb_id,
            **defaults
        )

    user_rating = None
    
    if request.user.is_authenticated:
        user_rating = Ratings.objects.filter(user=request.user, movie=movie).first()
    
    comments = Comment.objects.filter(movie=movie).order_by('-commented_at')
    
    context = {
        "movie":movie,
        "user_rating":user_rating, 
        "rating_range":range(10, 0,-1),
        "comments":comments
        }
    
    return render(request, 'movies/movie_detail.html', context)


@login_required
def movie_favourite(request):
    if request.method == 'POST':
        fav_movie = request.POST['movie_id']   
        fav_movie = the_movie_detail(fav_movie) if fav_movie else []
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
                'adult':fav_movie['adult']} )
        my_fav_movie, created = FavoriteMovie.objects.get_or_create(user=request.user, movie=movie)
        if created:
            messages.success(request, f"{my_fav_movie.movie.title} added to favourites")
        else:
            messages.info(request, f"{my_fav_movie.movie.title} is already in your favourites")
        
        return redirect("my_fav_movies")
       
    movies= FavoriteMovie.objects.filter(user=request.user).order_by('-added_at')
    all_fav_movie=[]
    for movie in movies:
        all_fav_movie.append(movie.movie)
    return render(request, "movies/favourite_movies.html", {'fav_movies':all_fav_movie})

@login_required
def remove_from_favourite(request):
    if request.method == 'POST':
        fav_movie = request.POST.get('movie_id')
        movie_to_remove=get_object_or_404(FavoriteMovie, user=request.user, movie=fav_movie)
        movie_title = movie_to_remove.movie.title
        movie_to_remove.delete()
        messages.success(request, f"{movie_title} was removed from favourite")
        return redirect('my_fav_movies')


@login_required
def rate_movie(request, tmdb_id):
    if request.method != "POST":
        return redirect("movie_detail", tmdb_id=tmdb_id)
    
    score = int(request.POST.get('score', 0))
    if score < 1 or score > 10:
        messages.error(request, "score must be betw3een 1 and 10")
        return redirect("movie_detail", tmdb_id=tmdb_id)

    movie = Movie.objects.filter(tmdb_id=tmdb_id).first()

    if not movie:
        defaults = get_movie_defaults(tmdb_id)
        if not defaults:
            messages.error(request, "Unable to load movie details")
            return redirect('index')

        movie = Movie.objects.create(
            tmdb_id=tmdb_id,
            **defaults
        )
    # movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
        
    Ratings.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={"score":score}
    )
    
    messages.success(request, "Rating saved successfully")
    return redirect("movie_detail", tmdb_id=movie.tmdb_id)



def comments(request, tmdb_id):
    if request.method == 'POST':
        movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
        if not movie:
            defaults = get_movie_defaults(tmdb_id)
            if not defaults:
                raise Http404("Movie not found")
            movie = Movie.objects.create(tmdb_id=tmdb_id, **defaults)

        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(user=request.user, movie=movie, content=content)
        return redirect("movie_detail", tmdb_id=tmdb_id)
    return redirect("movie_detail", tmdb_id=tmdb_id)


def genres_movie(request, genre_name):
    genre = get_object_or_404(Genre, name=genre_name)
    movies = get_movie_by_genres(genre_id=genre.tmbd_id)
    return render(request, "movies/home.html", {'movies':movies, "genre_name":genre_name})
