from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, MovieType, Genre, Country, Actor, MovieType, Subtitle, Favorite, User, UserProfile, Studio 
from datetime import date
from .forms import loginForm, registationForm, profileUpdateForm1, profileUpdateForm2, CustomPasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout  
from django.urls import reverse 
from django.contrib import messages
import requests
import json

# Create your views here.

def index(request):
    return redirect('home')

def browse():
    types = MovieType.objects.all()
    current_year = date.today().year +1
    year_list = []
    for i in range(5):
        current_year-=1
        item = {'year': current_year}
        year_list.append(item)
    genres = Genre.objects.all()
    countries = Country.objects.all() 
    
    return types, year_list, genres, countries
    
def get_profile(request):
    if request.user.is_authenticated:
        user = request.user
        current_user = get_object_or_404(User,username=user)
        user_profile = current_user.userprofile
    else:
        user_profile = None

    return user_profile

def get_rating(pk):
    movie = Movie.objects.get(id=pk)
    tmdb_id = movie.tmdb_id
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9' 
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}'  
    rating_data = requests.get(url).json()
    rating = round(rating_data['vote_average'], 1)
    return rating

def get_popular_movie():
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9'
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    popular_movie_data = requests.get(url).json()
    movie_fliter = []
    for data in popular_movie_data['results']:
        movie_fliter.append(data['id']) 
    popular_movie = Movie.objects.filter(tmdb_id__in = movie_fliter)

    return popular_movie

def get_trending_movie():
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9'
    url = f'https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}'
    trending_movie_data = requests.get(url).json()
    movie_fliter = []
    for data in trending_movie_data['results']:
        movie_fliter.append(data['id']) 
        
    trending_movie = Movie.objects.filter(tmdb_id__in = movie_fliter)

    return trending_movie

def home(request):
    types, year_list, genres, countries = browse()
    movies = Movie.objects.all().prefetch_related('genres').order_by('-views')[:5]
    user_profile = get_profile(request)
    type_movie = MovieType.objects.get(type= 'Movies')
    movie_type = Movie.objects.filter(type=type_movie).order_by('-id')[:5]
    type_tv_show = MovieType.objects.get(type= 'TV Shows')
    movie_tv_show = Movie.objects.filter(type=type_tv_show).order_by('-id')[:5]
    popular_movie = get_popular_movie()
    trending_movie =get_trending_movie()
    ratings = []
    for movie in movies:
        rating = get_rating(movie.pk)
        ratings.append(rating)
    
    packed = zip(movies,ratings)
    context = {
        'packed':packed,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,
        'movie_type' : movie_type,
        'movie_tv_show' : movie_tv_show,
        'popular_movie' : popular_movie,
        'trending_movie' : trending_movie,
        
        }
    
    return render(request, 'home.html',context)

def movie_detail(request,title,pk):
    movies = Movie.objects.filter(id=pk).prefetch_related('genres')
    watchlist_movie = Movie.objects.get(id=pk)
    types, year_list, genres, countries = browse()
    rating = get_rating(pk)
    user_profile = get_profile(request)
    user = request.user
    if request.user.is_authenticated:
        user_status = True
        user_like = Movie.objects.get(id=pk).like.filter(id=user.id).exists()
        watchlist = Favorite.objects.filter(user=user, movie = watchlist_movie.pk).exists()
    else:
        user_like = None
        watchlist = None
        user_status = False
    
    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_like' : user_like,
        'watchlist' : watchlist,
        'user_status' : user_status,
        'user_profile' : user_profile,
        'rating' : rating,
    }

    return render(request, 'movie_detail.html',context)

def playing(request, pk, title):
    movie = Movie.objects.get(id=pk)
    movie.views +=1
    movie.save()
    subtitles = Subtitle.objects.filter(movie=pk)
    user_profile = get_profile(request)

    context = {
        'movie': movie,
        'subtitles' : subtitles,
        'user_profile' : user_profile,
    }
    
    return render(request, 'playing.html', context)

def genre(request, movie_genre1,pk):
    types, year_list, genres, countries = browse()
    a = Genre.objects.get( genre_choice=movie_genre1)
    movies= Movie.objects.filter(genres=a)
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'movie_genre1': movie_genre1,
        'user_profile' : user_profile,
    }

    return render(request, 'genre.html', context)

def actor(request, actor_first_name, actor_last_name,pk):
    types, year_list, genres, countries = browse()
    a = Actor.objects.get(first_name=actor_first_name, last_name=actor_last_name)
    movies = Movie.objects.filter(actors=a)
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'actor_first_name': actor_first_name,
        'actor_last_name' : actor_last_name,
        'user_profile' : user_profile,
    }
    
    return render(request, 'actor_filter.html', context)

def studio(request, name):
    types, year_list, genres, countries = browse()
    a = Studio.objects.get(name=name)
    movies = Movie.objects.filter(studio=a)
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,
        'studio' : name,
    }

    return render(request, 'studio.html', context)

def movies(request):
    types, year_list, genres, countries = browse()
    type_movie = MovieType.objects.get(type= 'Movies')
    movies = Movie.objects.filter(type=type_movie).order_by('-id')
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,
    }
    
    return render(request, 'movies.html', context)

def watchlist(request):
    types, year_list, genres, countries = browse()
    movies = Favorite.objects.filter(user= request.user)      
    print(movies)
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,
    }

    return render(request, 'watchlist.html', context)    

def tv_shows(request):
    types, year_list, genres, countries = browse()
    type_tv_show = MovieType.objects.get(type= 'TV Shows')
    movies = Movie.objects.filter(type=type_tv_show).order_by('-id')
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,        
    }
    
    return render(request, 'tv_shows.html', context)

def search(request):
    types, year_list, genres, countries = browse()
    search1 = request.GET.get('search')
    
    if search1 == None and request.user.is_authenticated:
       search1 = request.session.get('temporary_data') 
       movies = Movie.objects.filter(title__icontains=search1)        
    
    else:    
        movies = Movie.objects.filter(title__icontains=search1)
        request.session['temporary_data'] = request.GET['search']         
    
    user_profile = get_profile(request)
    
    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'search1' : search1,
        'user_profile' : user_profile,
    }

    return render(request, 'search.html', context)

def popular(request):
    movies = get_popular_movie()
    types, year_list, genres, countries = browse()
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,        
    }

    return render(request, 'popular.html', context)

def trending(request):
    movies = get_trending_movie()
    types, year_list, genres, countries = browse()
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,        
    }

    return render(request, 'trending.html', context)

def browse_fliter(request):

    types, year_list, genres, countries = browse()
    movie_type = request.POST.get('movie-type')
    movie_quality = request.POST.get('quality')
    movie_year = request.POST.get('year')
    movie_genre = request.POST.getlist('genre')
    movie_country = request.POST.getlist('country')
    if (movie_type !='All' and movie_quality !='All' and movie_year !='All'):
        choice_movie_type = MovieType.objects.get(type=movie_type)
        movies_all = Movie.objects.filter(type=choice_movie_type, qulity=movie_quality, release_date__year =  movie_year)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all
            
    if (movie_type =='All' and movie_quality == 'All' and movie_year =='All'):
        movies_all = Movie.objects.all()
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all
        
    if (movie_type !='All' and movie_quality == 'All' and movie_year =='All'):
        choice_movie_type = MovieType.objects.get(type=movie_type)
        movies_all = Movie.objects.filter(type=choice_movie_type)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all
    
    if (movie_type !='All' and movie_quality != 'All' and movie_year =='All'):
        choice_movie_type = MovieType.objects.get(type=movie_type)
        movies_all = Movie.objects.filter(type=choice_movie_type, qulity=movie_quality)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all

    if (movie_type !='All' and movie_quality == 'All' and movie_year !='All'):
        choice_movie_type = MovieType.objects.get(type=movie_type)
        movies_all = Movie.objects.filter(type=choice_movie_type, release_date__year =  movie_year)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all
    
    if (movie_type =='All' and movie_quality == 'All' and movie_year !='All'):
        movies_all = Movie.objects.filter(release_date__year =  movie_year)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all

    if (movie_type =='All' and movie_quality != 'All' and movie_year !='All'):
        print('dfad')
        movies_all = Movie.objects.filter(qulity=movie_quality,release_date__year =  movie_year)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all

    if (movie_type =='All' and movie_quality != 'All' and movie_year =='All'):
        print('dfad')
        movies_all = Movie.objects.filter(qulity=movie_quality)
        if movie_genre and movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre, country__country__in = movie_country).distinct()
        if movie_genre and not movie_country:
            movies=movies_all.filter(genres__genre_choice__in=movie_genre).distinct()
        if movie_country and not movie_genre:
            movies=movies_all.filter(country__country__in = movie_country).distinct()
        if not movie_genre and not movie_country:
            movies = movies_all
    
    user_profile = get_profile(request)

    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,
        }

    return render(request, 'browse_fliter.html', context)

def login(request):
    # login
    form_login = loginForm()
    error_login = ''
    user = ''
    if request.method=="POST":
        form = loginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request,user)            
            return redirect('home')
        if user is None and username is not None:
            error_login = "Username and password not matched"
    # register        
    form_register = registationForm()
    if request.method=="POST":
        first_name = str(request.POST.get('first_name')).upper()
        last_name = str(request.POST.get('last_name')).upper()
        updatedata = request.POST.copy()
        updatedata['first_name'] = first_name
        updatedata['last_name'] = last_name
        form_register = registationForm(updatedata)
        if form_register.is_valid():                          
            form_register.save()
            return redirect('login')

    context = {
        'form_login':form_login,
        'form_register':form_register,
        'error_login': error_login,
        'user' : user,
        }

    return render(request, 'login.html', context)

def logout(request):
    auth_logout(request)
    return redirect('home')

def like_movie(request,pk, title):
    user= request.user
    movie = Movie.objects.get(id=pk)
    if request.user.is_authenticated:
        user_like = movie.like.filter(id=user.id).exists()
        if user_like == False:
            movie.like.add(user)
            return redirect(reverse('movie', kwargs={'pk':pk, 'title': title}))
        else:
            movie.like.remove(user)
            return redirect(reverse('movie', kwargs={'pk':pk, 'title': title}))
    else:
        messages.info(request, 'You need to login to perform the action')
        return redirect(reverse('movie',  kwargs={'pk':pk, 'title': title}))
        
def add_watchlist(request, pk, title):
    user= request.user
    movie = Movie.objects.get(id=pk)
    if request.user.is_authenticated:
        watchlist, created = Favorite.objects.get_or_create(user=user, movie=movie)
        if not created:
            watchlist.delete()
        return redirect(reverse('movie',  kwargs={'pk':pk, 'title': title}))
    
    else:
        messages.info(request, 'You need to login to perform the action')
        return redirect(reverse('movie',  kwargs={'pk':pk, 'title': title}))
    
def profile(request):
    types, year_list, genres, countries = browse()
    user = request.user.userprofile
    current_user = get_object_or_404(User,username=user)
    user_profile = current_user.userprofile
    form1=profileUpdateForm1(request.POST or None, request.FILES or None, instance=current_user)
    form2= profileUpdateForm2(request.POST or None, request.FILES or None, instance=user_profile)
    if form1.is_valid() and form2.is_valid():
            
            form1.save()
            form2.save()
            messages.info(request,'Your profile has been updated secessfully.') 
    
    context={
        'form1' : form1,
        'form2' : form2,
        'user_profile' : user_profile,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
    }

    return render(request, 'profile.html', context)

def change_password(request):
    types, year_list, genres, countries = browse()
    form = CustomPasswordChangeForm(user=request.user)
    user_profile = get_profile(request)
    if request.method == "POST":
        if request.user.is_authenticated:
            form =CustomPasswordChangeForm(user=request.user, data=request.POST)
            user_profile = get_profile(request)
            user = User.objects.get(username= request.user)
            if form.is_valid():
                user = form.save()
                messages.info(request,'Your password has been changed scucessfully')
                return redirect('login')
    
    context={
        'form' : form,
        'user_profile' : user_profile,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
    }

    return render(request, 'change_password.html', context)