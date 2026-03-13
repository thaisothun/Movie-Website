from django.urls import path
from .import views
from django.contrib.sitemaps.views import sitemap, index
from movie_app.sitemaps import MovieSitemap, ActorSitemap, GenreSitemap, StudioSitemap

sitemaps = {
    'movies': MovieSitemap,
    'actors' : ActorSitemap,
    'genre' : GenreSitemap,
    'studio' : StudioSitemap,
    # Add other sitemaps for different sections here
}

urlpatterns = [
    path('', views.home, name='home'),
    path('movie-detail/<str:pk>/<str:title>/', views.movie_detail, name='movie'),
    path('playing/<str:pk>/<str:title>/', views.playing, name='playing'),
    path('genre/<str:slug>/', views.genre, name='genre'),
    path('actor/<str:tmdb_id>/<str:slug>', views.actor, name='actor'),
    path('movies/', views.movies, name='movies'),
    path('tv-shows/', views.tv_shows, name='tv_shows'),
    path('search/', views.search, name='search'),
    path('browse-fliter/', views.browse_fliter, name='browse_fliter'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("like-movie/<str:pk>/<str:title>/", views.like_movie, name='like-movie'),
    path("add-watchlist/<str:pk>/<str:title>/", views.add_watchlist, name='add-watchlist'),
    path("profile/", views.profile, name='profile'),
    path("change-password/", views.change_password, name='change-password'),
    path("studio/<str:slug>", views.studio, name='studio'),
    path("watchlist/", views.watchlist, name='watchlist'),
    path("popular-movies/", views.popular, name='popular'),
    path("trending-movies/", views.trending, name='trending'),
    path("upcoming-movies-review/<str:tmdb_id>/<str:title>/", views.upcoming_review, name='upcoming_review'),
    path("upcoming-movies/", views.upcoming_movie, name='upcoming_movie'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
]