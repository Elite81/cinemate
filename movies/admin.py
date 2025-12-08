from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Profile)
admin.site.register(Movie)
admin.site.register(FavoriteMovie)
admin.site.register(Ratings)
admin.site.register(Comment)
admin.site.register(Share)
admin.site.register(Genre)
