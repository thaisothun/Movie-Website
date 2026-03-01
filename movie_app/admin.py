from django.contrib import admin
from .models import Movie, Genre, Actor, Studio, Director, UserProfile, Country, MovieType, Subtitle, Language, Favorite

# Register your models here.

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Studio)
admin.site.register(Director)
admin.site.register(Country)
admin.site.register(MovieType)
admin.site.register(UserProfile)
admin.site.register(Subtitle)
admin.site.register(Language)
admin.site.register(Favorite)

