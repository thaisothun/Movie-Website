from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, MovieType, Genre, Country, Actor, MovieType, Subtitle, Favorite, User, UserProfile, Studio 
from datetime import date
from .forms import loginForm, registationForm, profileUpdateForm1, profileUpdateForm2, CustomPasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout  
from django.urls import reverse 
from django.contrib import messages
import requests
from django.views.decorators.csrf import ensure_csrf_cookie
import random
from django.utils.text import slugify
from django.db.models import Value
from django.db.models.functions import Concat

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

def get_actor_profile(tmdb_id):
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9' 
    url = f'https://api.themoviedb.org/3/person/{tmdb_id}?api_key={api_key}'
    actor = Actor.objects.filter(tmdb_id=tmdb_id)
    actor_profile_data_tmdb = requests.get(url).json()
    if actor.exists():    
        for data in actor:
            actor_profile = ({
                'full_name' : f'{data.first_name} {data.last_name}',
                'gender' : data.gender,
                'dob' : data.brith_day,
                'profile' : data.profile_picture,
                'biography' : actor_profile_data_tmdb['biography'],
                'place_of_birth' : actor_profile_data_tmdb['place_of_birth'],
                'popularity' : round(actor_profile_data_tmdb['popularity'])
            })
    else:
        actor_profile = None

    return actor_profile

def get_rating(pk):
    movie = Movie.objects.get(id=pk)
    tmdb_id = movie.tmdb_id
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9' 
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}'  
    rating_data = requests.get(url).json()
    if rating_data:
        rating = round(rating_data['vote_average'], 1)
    else:
        rating = None

    return rating
    
def get_popular_movie(count=None):
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9'
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    popular_movie_data = requests.get(url).json()
    movie_fliter = []
    for data in popular_movie_data['results']:
        movie_fliter.append(data['id']) 
    popular_movie = Movie.objects.filter(tmdb_id__in = movie_fliter)[0:count]
    
    return popular_movie

def get_trending_movie(count=None):
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9'
    url = f'https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}'
    trending_movie_data = requests.get(url).json()
    movie_fliter = []
    for data in trending_movie_data['results']:
        movie_fliter.append(data['id'])
        
    trending_movie = Movie.objects.filter(tmdb_id__in = movie_fliter)[0:count]

    return trending_movie

def get_now_playing_movie(count=None):
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9'
    url = f'https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}'
    upcoming_movie_data = requests.get(url).json()
    upcoming_movie = []
    if count is not None:
        i=1
        for data in upcoming_movie_data['results']:
            slug = str(data['original_title']).replace(' ','-')
            if i <= count:
                i += 1
                upcoming_movie.append({
                        'id' : data['id'],
                        'title' : data['original_title'],
                        'poster' : data['poster_path'],
                        'rating' : data['vote_average'],
                        'release_date' : data['release_date'],
                        'overview' : data['overview'],
                        'slug' : slug
                    })
    else:
        for data in upcoming_movie_data['results']:
            slug = str(data['original_title']).replace(' ','-')
            upcoming_movie.append({
                            'id' : data['id'],
                            'title' : data['original_title'],
                            'poster' : data['poster_path'],
                            'rating' : data['vote_average'],
                            'release_date' : data['release_date'],
                            'overview' : data['overview'],
                            'slug' : slug
                        })
    
    return upcoming_movie

def get_movie_trailer(tmdb_id):
    api_key = '7f3c4c10ff7da5d1a65cdbae1c27fad9'
    url_trailer = f'https://api.themoviedb.org/3/movie/{tmdb_id}/videos?language=en-US&api_key={api_key}'
    url_review_movie = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}'
    url_actor = f'https://api.themoviedb.org/3/movie/{tmdb_id}/credits?api_key={api_key}'
    url_image = f'https://api.themoviedb.org/3/movie/{tmdb_id}/images?api_key={api_key}'
    url_review = f'https://api.themoviedb.org/3/movie/{tmdb_id}/reviews?api_key={api_key}'
    
    review_movie_data = requests.get(url_review_movie).json()
    if review_movie_data:
        genre = []
        for data in review_movie_data['genres']:
            genre.append({
                'slug' : slugify(data['name']),
                'name' : data['name'],
                })
        studio = []
        for data in review_movie_data['production_companies']:
            studio.append({
                'slug' : slugify(data['name']),
                'name' : data['name'],
            })
        
        upcoming_review_movie = {
            'title' : review_movie_data['original_title'],
            'overview' : review_movie_data['overview'],
            'genres' : genre,
            'release_date' : review_movie_data['release_date'],
            'runtime' : review_movie_data['runtime'],
            'status' : review_movie_data['status'],
            'vote_average' : round(review_movie_data['vote_average'],1),
            'production_companies' : studio,
            'backdrop_path' : review_movie_data['backdrop_path'],
            'poster_path' : review_movie_data['poster_path'],
            'budget' : review_movie_data['budget'],
            'revenue' : review_movie_data['revenue'],
                
        }
    else:
        upcoming_review_movie = None

    trailer_movie_data = requests.get(url_trailer).json()
    if trailer_movie_data['results']:
        trailer_id = trailer_movie_data['results'][1]['key']
    else:
        trailer_id =None
    
    actor_data = requests.get(url_actor).json()
    if actor_data:
        director_filter = [data for data in actor_data['crew'] if data['job']=='Director']
        director_name = director_filter[0]['name']
        actors = []
        for data in actor_data['cast'][:4]:
            actors.append({
                'actor_id' : data['id'],
                'name' : data['name'],
                'profile_path' : data['profile_path'],
                'character' : data['character'],
                'slug' : slugify( data['name']),
            })
    else:
        actors = None
    
    backdrop_data = requests.get(url_image).json()
    if backdrop_data['backdrops']:
        backdrop_len = (len(backdrop_data['backdrops']))-1
        backdrops = {
            'backdrop1' : backdrop_data['backdrops'][random.randint(1, backdrop_len)]['file_path'],
            'backdrop2' : backdrop_data['backdrops'][random.randint(1, backdrop_len)]['file_path'],
            'backdrop3' : backdrop_data['backdrops'][random.randint(1, backdrop_len)]['file_path'],
        }
    else:
        backdrops= None
    
    review_content_data = requests.get(url_review).json()
    if review_content_data:
        review_contents = []
        for data in review_content_data['results']:
            review_contents.append({
                'username' : data['author_details']['username'],
                'avatar_path' : data['author_details']['avatar_path'],
                'content' : data['content'],
                'date' : data['updated_at'],
            })
    else:
        review_contents = None

    return trailer_id, upcoming_review_movie, actors, backdrops, review_contents, director_name    
    
@ensure_csrf_cookie
def home(request):
    types, year_list, genres, countries = browse()
    movies = Movie.objects.all().prefetch_related('genres').order_by('-views')[:5]
    user_profile = get_profile(request)
    type_movie = MovieType.objects.get(type= 'Movies')
    upcoming_movie = get_now_playing_movie(4)
    movie_type = Movie.objects.filter(type=type_movie).order_by('-id')[:10]
    type_tv_show = MovieType.objects.get(type= 'TV Shows')
    movie_tv_show = Movie.objects.filter(type=type_tv_show).order_by('-id')[:10]
    popular_movie = get_popular_movie(10)
    trending_movie =get_trending_movie(10)
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
        'upcoming_movie' : upcoming_movie,
        }
    
    return render(request, 'home.html',context)

def movie_detail(request,pk,title):
    movies = Movie.objects.filter(id=pk).prefetch_related('genres')  
    watchlist_movie = Movie.objects.get(id=pk)
    types, year_list, genres, countries = browse()
    rating = get_rating(pk)
    user_profile = get_profile(request)
    for movie in movies:
        tmdb_id = movie.tmdb_id
    request.session['temporary_data1'] = tmdb_id
    request.session['temporary_data2'] = title
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
        'movies': movies,
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

def genre(request, slug):
    movie_genre1 = request.POST.get('genre')
    types, year_list, genres, countries = browse()
    tmdb_id = request.session.get('temporary_data1')
    title = request.session.get('temporary_data2')
    
    try:
        data = str(slug).replace('-',' ')
        a = Genre.objects.get(genre_choice__icontains=data)
        movies= Movie.objects.filter(genres=a)
        user_profile = get_profile(request)
    except:
        return redirect(reverse('upcoming_review', kwargs={'tmdb_id':tmdb_id, 'title' : title}))
    
    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'movie_genre1': data,
        'user_profile' : user_profile,
    }

    return render(request, 'genre.html', context)

def actor(request,slug,tmdb_id):
    data = str(slug).replace('-',' ')
    types, year_list, genres, countries = browse()
    tmdb_id = tmdb_id
    try:
        a = Actor.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).get(full_name__icontains=data)
        actor = get_actor_profile(a.tmdb_id)
        movies = Movie.objects.filter(actors=a)
        user_profile = get_profile(request)
        actor_profile = get_actor_profile(a.tmdb_id)
        context ={
            'movies':movies,
            'types':types,
            'year_list':year_list,
            'genres':genres,
            'countries':countries,
            'actor': actor,
            'user_profile' : user_profile,
            'actor_profile' : actor_profile,
        }
        return render(request, 'actor_filter.html', context)
    except:
        return redirect(f'https://www.themoviedb.org/person/{tmdb_id}')

def studio(request, slug):
    types, year_list, genres, countries = browse()
    tmdb_id = request.session.get('temporary_data1')
    title = request.session.get('temporary_data2')
    try:
        data = str(slug).replace('-',' ')
        a = Studio.objects.get(name__icontains=data)    
        movies = Movie.objects.filter(studio=a)
        user_profile = get_profile(request)
    except:
        
        return redirect(reverse('upcoming_review', kwargs={'tmdb_id':tmdb_id, 'title' : title}))
    
    context ={
        'movies':movies,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'user_profile' : user_profile,
        'studio' : data,
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

@ensure_csrf_cookie
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

@ensure_csrf_cookie
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

@ensure_csrf_cookie
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
    
@ensure_csrf_cookie    
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

@ensure_csrf_cookie
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

def upcoming_review(request, tmdb_id, title):
    types, year_list, genres, countries = browse()
    user_profile = get_profile(request)
    trailer_id, upcoming_review_movie, actors, backdrops, review_contents, director_name = get_movie_trailer(tmdb_id)
    request.session['temporary_data1'] = tmdb_id
    request.session['temporary_data2'] = title
    context = {
        'trailer_id' : trailer_id,
        'upcoming_review_movie' : upcoming_review_movie, 
        'actors' : actors,
        'backdrops' : backdrops,
        'review_contents' : review_contents,
        'tmdb_id' : tmdb_id,
        'director_name' : director_name,
        'user_profile' : user_profile,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
    }

    return render(request, 'upcoming_review.html', context)

def upcoming_movie(request):
    types, year_list, genres, countries = browse()
    user_profile = get_profile(request)
    upcoming_movie = get_now_playing_movie()

    context = {
        'user_profile' : user_profile,
        'types':types,
        'year_list':year_list,
        'genres':genres,
        'countries':countries,
        'upcoming_movie' : upcoming_movie,
    }

    return render(request, 'upcoming_movie.html', context)