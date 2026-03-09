from django.contrib.sitemaps import Sitemap
from .models import Movie, Actor, Genre, Studio

class MovieSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    # Optional: set protocol to 'https' for production
    # protocol = 'https'

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Movie.objects.all()
    
    def location(self, obj):
        return f"/movie-detail/{obj.id}/{obj.slug}" # Explicitly define the URL path
    
class ActorSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Actor.objects.all()
    
    def location(self, obj):
        return f"/actor/{obj.first_name}-{obj.last_name}" # Explicitly define the URL path

class GenreSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Genre.objects.all()
    
    def location(self, obj):
        return f"/genre/{obj.genre_choice}" # Explicitly define the URL path
    
class StudioSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Studio.objects.all()
    
    def location(self, obj):
        return f"/studio/{obj.name}" # Explicitly define the URL path