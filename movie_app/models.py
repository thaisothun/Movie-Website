from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import os
from django.db.models.signals import post_save
from django.utils.text import slugify
 
class Genre(models.Model):
    genre_choice = models.CharField(max_length=50, unique=True, help_text='Please use lowercase')
    slug = models.SlugField(blank=True, null=True, editable=False)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['genre_choice']

    def __str__(self):
        return self.genre_choice
    
    def save(self, *args, **kwargs):
        data = (self.genre_choice).lower()
        slug = slugify(data)
        self.slug = slug
        super().save(*args, **kwargs)

class Studio(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='The official name of the studio.')
    slug = models.SlugField(blank=True, null=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        data = (self.name).lower()
        slug = slugify(data)
        self.slug = slug
        super().save(*args, **kwargs)
    
def actor_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{instance.first_name}-{instance.last_name}.{ext}'
    return f'actors/{instance.first_name}_{instance.last_name}/{new_filename}'

class Actor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(choices=[('Male','Male'),('Female','Female')])
    brith_day = models.DateField()
    profile_picture = models.ImageField(upload_to=actor_directory_path)
    slug = models.SlugField(blank=True, null=True, editable=False)
    tmdb_id = models.CharField(default="tmdb")
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['first_name', '-last_name']
        unique_together = [['first_name', 'last_name']]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self, *args, **kwargs):
        data = (f'{self.first_name} {self.last_name}').lower()
        slug = slugify(data)
        self.slug = slug
        super().save(*args, **kwargs)

class Director(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    class Meta:
        ordering = ['first_name', '-last_name']
        unique_together = [['first_name', 'last_name']]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class MovieType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return f'{self.type}'

class Country(models.Model):
    country = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return f'{self.country}'

def hls_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT for hls  
    return f'movies/{instance.title}/media/{filename}'

def poster_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{instance.slug}.{ext}' 
    return f'movies/{instance.title}/poster/{new_filename}'

def backdrop_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'backdrop.{ext}'
    return f'movies/{instance.title}/backdrop/{new_filename}'

class Movie(models.Model):
    title = models.CharField(max_length=255, help_text='Do not use < > : " / \ | ? * #, %, &, {, }, $, !, +, or emojis')
    type = models.ForeignKey(MovieType, on_delete=models.SET_NULL, null=True, related_name='movies', default='Movies')
    description = models.TextField()
    release_date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='movies', default=1)
    qulity = models.CharField(choices=[('HD','HD'),('CAM','CAM')], default='HD')
    poster = models.ImageField(upload_to=poster_directory_path)
    backdrop1 = models.ImageField(upload_to=backdrop_directory_path)
    backdrop2 = models.ImageField(upload_to=backdrop_directory_path)
    running_time = models.IntegerField(help_text='Running time in minutes')
    pg = models.CharField(choices=[('PG','PG'),('G','G'),('PG-13','PG-13'),('R','R'),('NC-17','NC-17')])
    # Many-to-many relationship with Genre model
    genres = models.ManyToManyField(Genre, related_name='movies')
    # Foreign Key to Director model (one-to-many relationship)
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, related_name='movies')
    actors = models.ManyToManyField(Actor, related_name='movies')
    studio = models.ManyToManyField(Studio, related_name='movies')
    # Optional field for storing an external API ID (e.g., TMDb ID)
    tmdb_id = models.CharField(max_length=50,unique=True)
    hls_playlist = models.CharField()
    bunny_embed_code = models.CharField(default='bunny embed url')
    trailer_url = models.CharField(blank=True,null=True,default='youtube url')
    views = models.IntegerField(default=0)
    like = models.ManyToManyField(User, related_name='movies', blank=True)
    slug = models.SlugField(blank=True, null=True, editable=False)
    updated = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        data = (self.title).lower()
        slug = slugify(data)
        self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def hls_url(self):
        # Returns the full URL to the m3u8 file
        return f'{settings.MEDIA_URL}{self.hls_playlist.name}'
    
def user_profile_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{instance.user}.{ext}'
    return f'profiles/{instance.user}/{new_filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='userprofile')
    short_message = models.CharField(max_length=100, blank=True, null=True)
    image_profile = models.ImageField(upload_to=user_profile_directory_path, blank=True, null=True)
    gender = models.CharField(choices=[('Male','Male'),('Femal','Femal')])
    date_of_brith = models.DateField(blank=True, null=True)
    membership = models.CharField(choices=[('normal','Normal'),('vip','VIP')], default='normal')
    phone_number = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return f'{self.user}'
   
def createProfile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        profile.save()

post_save.connect(createProfile, sender=User)

def subtitle_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT for poster 
    return f'movies/{instance.movie.title}/subtitles/{filename}'

class Language(models.Model):
    language_choice = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return f'{self.language_choice}'

class Subtitle(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='subtitle')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='subtitle')
    file_url =  models.FileField(upload_to=subtitle_directory_path)
    class Meta:
        ordering = ['movie']
        unique_together = ('movie', 'language')
    
    def __str__(self):
        return f'{self.movie.title} - {self.language}' 
    
class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='favorites', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.movie.title}' 