from django.db import models
from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_staff = models.BooleanField(default=False)  # Default: normal users are not staff

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

# models.py
class Movie(models.Model):
    CATEGORY_CHOICES = [
        ('new_release', 'New Release'),
        ('short', 'Short'),
        ('now_showing', 'Now Showing'),
    ]
    title = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    genre = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='movie_posters/')
    release_date = models.DateField()
    duration = models.CharField(max_length=50)
    cast = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='movies/', blank=True, null=True)  # <-- Make it optional

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='now_showing')  # 👈 new field

    published_at = models.DateTimeField(auto_now_add=True)  # when added to DB
    views = models.PositiveIntegerField(default=0)  # store number of views

    def __str__(self):
        return self.title

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='PAID')  # For simplicity, mark as PAID
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
class Favourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','movie')

    def __str__(self):
        return f"{self.user} = {self.movie}"

class Trending_Now(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='movie_posters/')
    release_date = models.DateField()
    duration = models.CharField(max_length=50)
    cast = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class New_Release(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='movie_posters/')
    release_date = models.DateField()
    duration = models.CharField(max_length=50)
    cast = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Comedy(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='movie_posters/')
    release_date = models.DateField()
    duration = models.CharField(max_length=50)
    cast = models.CharField(max_length=255)

    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings

class UserWatchProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watch_progress"
    )
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)
    progress = models.FloatField(default=0)
    last_position = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('user', 'movie')  # <--- enforce 1 entry per user/movie

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.progress:.0f}%)"

    