from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile'"


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    vote_average = models.FloatField(blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)
    original_language = models.CharField(max_length=10, blank=True, null=True)
    adult = models.BooleanField(default=False)
    video = models.BooleanField(default=False)


    def get_absolute_url(self):
        return reverse("movie_detail", args=[str(self.id)])
    
    def __str__(self):
        return f'{self.movie.title}'
    

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
    
    def __str__(self):
        return f'{self.user.username} sets {self.movie.title} as favourite'


class Ratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.IntegerField(default=1)
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} rated {self.movie.title}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    content = models.TextField()
    comented_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
    
    def __str__(self):
        return f'{self.user.username} comented on {self.movie.title}'



class Share(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    plateform = models.CharField(max_length=64)
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
    
    def __str__(self):
        return f'{self.movie.title} shared on {self.plateform}'


class Genre(models.Model):
    tmbd_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=256)
    movies= models.ManyToManyField(Movie, related_name='genres')

    def __str__(self):
        return self.name