from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name='home'),
    path("search/", search, name='search'),
    path('movie/<int:movie_id>', movie_detail, name="movie_detail")
]
