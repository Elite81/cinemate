from django.urls import path
from .views import *

urlpatterns = [ 
    path("", index, name='home'),
    path("search/", search, name='search'),
    path('movie/<int:tmdb_id>', movie_details, name="movie_detail"),
    path('favourites/', movie_favourites, name="my_fav_movies"),
    path('remove_from_favourite/', remove_from_favourites, name="rm_from_favourite"),
    path('rating/<int:tmdb_id>', rate_movie, name='rate_movie'),
    path('comment/<int:tmdb_id>', comments, name="add_comment"),
    path('genre/<str:genre_name>', genres_movie, name="genres_movie")
]
