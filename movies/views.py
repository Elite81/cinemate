from django.shortcuts import render
from .utils import *


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
    print(movie_id)
    result = the_movie_detail(movie_id) if movie_id else []
    print(result)
    return render(request, 'movies/movie_detail.html', {'movie':result})
    