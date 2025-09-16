from django.urls import path
from . import views
from django.urls import path
from . import views
urlpatterns = [
    path('', views.LandingPage, name='LandingPage'),
    path('landingPage/', views.LandingPage, name='LandingPage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('movies/', views.movies, name='movies'),
    path('news/', views.news, name='news'),
    path('vote/', views.vote, name='vote'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('admin_dashboard/', views.admin_dashboard, name= 'admin_dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('profile/', views.update_profile, name='update_profile'),
    path('series/', views.series , name='series'),
    path('changePin/',views.changePin,name='changePin'),
    path('inputPin/',views.inputPin,name='inputPin'),
    path('movie_detail/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('media-stream/<path:path>/', views.stream_video, name='stream_video'),
    path('favourite/<int:movie_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('my-favourites/', views.favourites_list, name='favourites_list'),
    path('savedList/', views.saved_list, name='saved_list'),
    path('profile/', views.profile_view, name='profile_view'),
    path('saved_list/', views.saved_list, name='saved_list'),
    path('edit-profile/', views.update_profile, name='update_profile'),
    path('payment_after_movie/',views.payment_after_movie, name='payment_after_movie'),
    path("payment_after_movie/<int:pk>/", views.payment_after_movie, name="payment_after_movie"),
    path('search/', views.search_movies, name='search_movies'),
    path('movie/<int:pk>/pay/', views.esewa_payment, name='esewa_payment'),
    path('esewa-success/<int:pk>/', views.esewa_success, name='esewa_success'),
    path('esewa-fail/<int:pk>/', views.esewa_fail, name='esewa_fail'),
    path("api/progress/<int:movie_id>/", views.video_progress, name="video_progress"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('initiate/,', views.initkhalti, name="initiate"),
    path('verify/', views.verifyKhalti, name="verify"),
    path('home/', views.home, name="home"),

]













