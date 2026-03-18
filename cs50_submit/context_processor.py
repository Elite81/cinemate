from movies.models import Genre

def movie_genres(request):
    return {"all_genres":Genre.objects.all()}