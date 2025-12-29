from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import *
from .models import *


# Create your views here.
def index(request):
    movies = get_popular_movies()
    return render(request, "movies/home.html", {'movies':movies})


def search(request):
    query = request.GET.get('q', '')
    results = search_movies(query) if query else []
    print(results[0])
    return render(request, 'movies/search_movies.html', {'movies':results, 'query':query})


def movie_detail(request, movie_id):
    result = the_movie_detail(movie_id) if movie_id else []
    return render(request, 'movies/movie_detail.html', {'movie':result})


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