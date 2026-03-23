from django.contrib.sitemaps import Sitemap
from .models import Movie, Actor, Genre, Studio

class MovieSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    # Optional: set protocol to 'https' for production
    # protocol = 'https'

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Movie.objects.all()
    
    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return f"/movie-detail/{obj.id}/{obj.slug}" # Explicitly define the URL path
    
class ActorSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Actor.objects.all()
    
    def lastmod(self, obj):
        return obj.updated
    
    def location(self, obj):
        return f"/actor/{obj.tmdb_id}/{obj.slug}" # Explicitly define the URL path

class GenreSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Genre.objects.all()
    
    def lastmod(self, obj):
        return obj.updated
    
    def location(self, obj):
        return f"/genre/{obj.slug}" # Explicitly define the URL path
    
class StudioSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Return a QuerySet of objects to be included in the sitemap
        return Studio.objects.all()
    
    def lastmod(self, obj):
        return obj.updated
    
    def location(self, obj):
        return f"/studio/{obj.slug}" # Explicitly define the URL path