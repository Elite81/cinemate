from django.shortcuts import render
from .utils import *


# Create your views here.
def index(request):
    movies = get_popular_movies()
    return render(request, "movies/home.html", {'movies':movies})


def search(request):
    query = request.GET.get('q', '')
    results = search_movies(query) if query else []
    print(results)
    return render(request, 'movies/search_movies.html', {'movies':results, 'query':query})