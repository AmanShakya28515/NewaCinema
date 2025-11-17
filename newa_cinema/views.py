from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistrationForm, LoginForm, ProfileForm, OTPChangeForm
from .models import Profile, User, Movie
from .utils import generate_otp, send_otp_email
from .models import Movie
from newa_cinema.models import Favourite
from django.contrib import messages
import os
import mimetypes
from django.http import StreamingHttpResponse, HttpResponse, Http404
from django.conf import settings
from wsgiref.util import FileWrapper
from django.shortcuts import render
from .models import Movie, Purchase

# Static pages



def movies(request):
    movies = Movie.objects.all()
    return render(request, "Movies/movies.html", {"movies": movies})

def news(request):
    return render(request, "News/news.html")

def vote(request):
    return render(request, "Voting/vote.html")

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def series(request):
    return render(request, "series.html")

def inputPin(request):
    return render(request, 'inputPin.html')
# Auth
from django.contrib import messages

from .utils import generate_otp, send_otp_email  # your OTP functions

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Please login.")
                return redirect('login')

            # Save new user
            user = form.save(commit=False)
            user.username = email  # Ensure username is set
            user.set_unusable_password()  # No password needed
            user.save()

            # Send welcome email
            send_mail(
                subject="Welcome to CineDabali!",
                message=f"Hi {name},\n\nYour account has been created successfully! Please login using OTP.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('login')

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'login_registration/registration.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = form.cleaned_data['otp']

            try:
                user = User.objects.get(email=email)
                if user.otp == otp:
                    login(request, user)
                    messages.success(request, f"Welcome, {user.name}!")

                    if user.is_superuser:
                        return redirect('admin_dashboard')
                    else:
                        return redirect('dashboard')
                else:
                    form.add_error('otp', 'Incorrect OTP. Please try again.')
            except User.DoesNotExist:
                form.add_error('email', 'Email not found.')
    else:
        form = LoginForm()

    return render(request, 'login_registration/login.html', {'form': form})

from django.db.models import Sum
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def update_profile(request):
    profile = request.user.profile
    profile_form = ProfileForm(instance=profile)
    otp_form = OTPChangeForm(instance=request.user)

    # Get all watch progress for this user
    qs = UserWatchProgress.objects.filter(user=request.user)

    # Counters
    watched_count = qs.filter(progress__gt=0).count()       # started / in progress
    completed_count = qs.filter(progress__gte=100).count()  # completed

    # Total watched time in seconds (sum of last_position)
    total_watched_seconds = qs.aggregate(total_time=Sum('last_position'))['total_time'] or 0
    watched_minutes = total_watched_seconds // 60
    hours = watched_minutes // 60
    minutes = watched_minutes % 60

    open_pin_modal = request.GET.get("open_pin_modal") == "1"

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile_view")

    context = {
        "profile_form": profile_form,
        "otp_form": otp_form,
        "open_pin_modal": open_pin_modal,
        "watched_count": watched_count,
        "completed_count": completed_count,  # optional in template
        "watched_hours": hours,
        "watched_minutes": minutes,
    }
    return render(request, "edit_profile.html", context)

@login_required
def profile_view(request):
    saved_count = Favourite.objects.filter(user=request.user).count()
    return render(request, 'profile.html', {
        'saved_count': saved_count
    })

@login_required
def saved_list(request):
    saved_movies = Movie.objects.filter(favourite__user=request.user)
    return render(request, 'saved_list.html', {
        'movies': saved_movies
    })

@login_required
def change_otp(request):
    if request.method == 'POST':
        form = OTPChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "OTP updated successfully!")
            return redirect('dashboard')
    else:
        form = OTPChangeForm(instance=request.user)
    return render(request, 'changePin.html', {'form': form})

@login_required
def changePin(request):
    if request.method == 'POST':
        form = OTPChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "OTP updated successfully!")
            return redirect('dashboard')
    else:
        form = OTPChangeForm(instance=request.user)
    return render(request, "changePin.html", {'form': form})

from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    new_releases = Movie.objects.filter(category="new_release")
    now_showing = Movie.objects.filter(category="now_showing")
    shorts = Movie.objects.filter(category="short")

    continue_entries = (
        UserWatchProgress.objects
        .filter(user=request.user, watched=False, progress__gt=0)
        .select_related("movie")
        .order_by("-updated_at")
    )

    if not request.session.get('welcome_shown', False):
        messages.success(request, f"Welcome, {request.user.name}!")
        request.session['welcome_shown'] = True

    return render(request, "dashboard.html", {
        "new_releases": new_releases,
        "now_showing": now_showing,
        "shorts": shorts,
        "continue_entries": continue_entries,
    })

def LandingPage(request):
    new_releases = Movie.objects.filter(category="new_release")
    shorts = Movie.objects.filter(category="short")
    now_showing = Movie.objects.filter(category="now_showing")

    context = {
        'new_releases': new_releases,
        'shorts': shorts,
        'now_showing': now_showing,
    }
    return render(request, 'LandingPage.html', context)

def stream_video(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path):
        raise Http404

    file_size = os.path.getsize(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'

    range_header = request.headers.get('Range')
    if range_header:
        range_match = range_header.strip().split('=')[-1]
        start, end = range_match.split('-')
        start = int(start) if start else 0
        end = int(end) if end else file_size - 1
        length = end - start + 1

        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)

        response = HttpResponse(data, status=206, content_type=content_type)
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        return response
    else:
        # No range header, return full file
        response = StreamingHttpResponse(FileWrapper(open(file_path, 'rb')), content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response

@login_required(login_url='login')
def movie_list(request):
    movies = Movie.objects.all()
    user_fav_ids = []
    if request.user.is_authenticated:
        user_fav_ids = Favourite.objects.filter(user=request.user).values_list('movie_id', flat=True)
    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'user_fav_ids': user_fav_ids
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Movie, Favourite

def toggle_favourite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.user.is_authenticated:
        fav, created = Favourite.objects.get_or_create(user=request.user, movie=movie)
        if not created:
            fav.delete()
            messages.success(request," Removed from watchlist.")
        else:
            messages.success(request,"Added to watchlist.")
    else:
        messages.error(request, "Please log in to manage your watchlist.")

    # 👇 Redirect back to movie_detail, not dashboard
    return redirect('movie_detail', pk=movie.id)

@login_required
def favourites_list(request):
    fav_movies = Movie.objects.filter(favourite_user = request.user)
    return render(request, 'movies/favourites_list.html',{'movies': fav_movies})

from django.shortcuts import get_object_or_404
import uuid
from django.shortcuts import get_object_or_404

@login_required(login_url='login')
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, id=pk)

    # Check if this user already purchased this movie
    user_paid = Purchase.objects.filter(user=request.user, movie=movie, status='PAID').exists()

    suggested_movies = Movie.objects.exclude(id=pk)[:12]
    user_fav_ids = Favourite.objects.filter(user=request.user).values_list('movie_id', flat=True)

    unique_id = str(uuid.uuid4())  # Always generate a new ID
    amount_in_paisa = movie.price * 100  # Convert Rs → paisa for Khalti

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'user_paid': user_paid,  # <-- IMPORTANT: renamed to match template logic
        'suggested_movies': suggested_movies,
        'user_fav_ids': user_fav_ids,
        'uuid': unique_id,
        'amount_in_paisa': amount_in_paisa
    })

@login_required
def saved_list(request):
    saved_movies = Movie.objects.filter(favourite__user = request.user)
    return render(request, 'saved_list.html',{
        'movies':saved_movies
    })

@login_required(login_url='login')
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('LandingPage')  # Change to your homepage or login page
    return redirect('LandingPage')

def series(request):
    movies = Movie.objects.filter(category__in=["new_release", "now_showing"])
    return render(request, 'series.html',{'movies':movies})

from django.shortcuts import render, get_object_or_404
from .models import Movie

@login_required(login_url='login')  # Redirects to login if not logged in
def payment_after_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    last_progress = UserWatchProgress.objects.filter(
        user=request.user, movie=movie
    ).order_by('-updated_at').first()
    last_position = last_progress.last_position if last_progress else 0

    suggested_movies = Movie.objects.filter(
    category__in=["now_showing", "new_release"]
    ).exclude(pk=pk)[:12]

    # ✅ Check if movie is already in the user's favourites
    is_favourite = Favourite.objects.filter(user=request.user, movie=movie).exists()

    user_paid = request.session.get(f'paid_for_{movie.id}', True)  # or actual payment check

    return render(request, "payment_after_movie.html", {
        'movie': movie,
        'suggested_movies': suggested_movies,
        'is_favourite': is_favourite,  # 👈 Pass to template
        'user_paid': user_paid,
        'last_position': last_position
    })

def movies(request):
    movies = Movie.objects.filter(category__in = ["now_showing", "new_release"])  # or filter as needed
    return render(request, 'movies.html', {'movies': movies})

from django.shortcuts import render
from .models import Movie
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string

def search_movies(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # ✅ Only search in the title
        results = Movie.objects.filter(
            title__icontains=query
        )

    # Check if AJAX request (for live search)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/search_results.html', {'results': results})
        return JsonResponse({'html': html})

    # Fallback: full page
    return render(request, 'search_results.html', {'query': query, 'results': results})

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from .forms import OTPChangeForm
@login_required
def changePin(request):
    if request.method == "POST":
        new_otp = request.POST.get("otp")
        if new_otp:
            request.user.otp = new_otp
            request.user.save()
            messages.success(request, "OTP updated successfully!")
            return redirect("update_profile")
        else:
            messages.error(request, "Please enter a valid OTP.")
            # Redirect with query param to auto-open modal
            return redirect("/edit-profile/?open_pin_modal=1")
    return redirect("update_profile")

# def search_movies(request):
#     query = request.GET.get('q', '')
#     results = []
#     if query:
#         results = Movie.objects.filter(
#             Q(title__istartswith=query)
#         )[:5]  # limit to top 5 results

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('partials/search_results.html', {'results': results})
#         return JsonResponse({'html': html})

#     return render(request, 'search_results.html', {'query': query, 'results': results})

#only if u want exact word to be filterned not other to be displayed 
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Movie

def esewa_payment(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    amount = 100  # or dynamically use movie.price if you have it

    esewa_url = "https://uat.esewa.com.np/epay/main"  # demo URL

    context = {
        'movie': movie,
        'amount': amount,
        'esewa_url': esewa_url,
        'pid': f"movie-{movie.id}-{request.user.id}",  # unique payment ID
        'su': request.build_absolute_uri(f"/esewa-success/{movie.id}/"),
        'fu': request.build_absolute_uri(f"/esewa-fail/{movie.id}/"),
    }
    return render(request, 'esewa_payment.html', context)

def esewa_success(request, pk):
    movie = get_object_or_404(Movie, id=pk)

    # Mark movie as paid in session
    request.session[f'paid_for_{movie.id}'] = True

    messages.success(request, f"Payment successful! You can now watch {movie.title}.")
    return redirect('movie_detail', pk=movie.id)

# eSewa fail
def esewa_fail(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    messages.error(request, "Payment failed or canceled. Please try again.")
    return redirect('movie_detail', pk=movie.id)

import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Movie, UserWatchProgress

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Movie, UserWatchProgress

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import Movie, UserWatchProgress

@login_required
@csrf_exempt  # Only needed if using fetch and CSRF token issues occur
def video_progress(request, movie_id):
    if request.method == "POST":
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return JsonResponse({"error": "Movie not found"}, status=404)

        data = json.loads(request.body)
        last_position = data.get("last_position", 0)
        duration = data.get("duration", 0)
        ended = data.get("ended", False)

        progress = 0
        if duration > 0:
            progress = round((last_position / duration) * 100, 2)

        # Get or create the progress record
        uwp, created = UserWatchProgress.objects.get_or_create(
            user=request.user,
            movie=movie,
            defaults={"last_position": last_position, "duration": duration, "progress": progress, "watched": ended}
        )

        if not created:
            # Update existing
            uwp.last_position = last_position
            uwp.duration = duration
            uwp.progress = progress
            uwp.watched = ended
            uwp.save()

        return JsonResponse({"progress": progress, "last_position": last_position, "watched": ended})

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.shortcuts import render
from django.contrib.auth import login
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import User
import random
from django.core.mail import EmailMultiAlternatives

@csrf_exempt
def send_otp(request):
    """Send OTP to email with a professional HTML template"""
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

            # Plain text fallback
            text_content = f"""
Hi,

Enter this code to continue logging in without a password:
{otp}

This code can only be used once.

If you didn't attempt to log in, you can safely ignore this email.

Best regards,
CineDabali Team
"""

            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Your CineDabali login code</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; padding: 30px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
    <img src='https://yourdomain.com/static/cinema.png' alt='CineDabali Logo' style='height: 60px; margin-bottom: 20px;'>
    <h2 style="color: #B11226;">Your Login Code</h2>
    <p style="font-size: 18px; margin: 20px 0;">Enter this code to continue logging in without a password:</p>
    <p style="font-size: 32px; font-weight: bold; letter-spacing: 4px; color: #333;">{otp}</p>
    <p style="color: #555; margin-top: 20px;">This code can only be used once.</p>
    <p style="color: #777; font-size: 14px; margin-top: 30px;">If you didn't attempt to log in, you can safely ignore this email.</p>
    <p style="margin-top: 20px; color: #B11226; font-weight: bold;">CineDabali Team</p>
  </div>
</body>
</html>
"""
            msg = EmailMultiAlternatives(
                subject="Your CineDabali Login Code",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return JsonResponse({"success": True, "message": "OTP sent to your email!"})

        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Email not registered!"})

    return JsonResponse({"success": False, "message": "Invalid request."})

@csrf_exempt
def verify_otp(request):
    """Verify OTP and login user"""
    if request.method == "POST":
        email = request.POST.get("email")
        otp = request.POST.get("otp")

        try:
            user = User.objects.get(email=email, otp=otp)
            user.otp = None
            user.save()
            login(request, user)
            redirect_url = "/admin_dashboard/" if user.is_superuser else "/dashboard/"
            return JsonResponse({"success": True, "redirect_url": redirect_url})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid OTP!"})
    return JsonResponse({"success": False, "message": "Invalid request."})

import json
import uuid
import requests
from django.shortcuts import render, redirect

def home(request):
    id = uuid.uuid4()
    return render(request, 'index.html', {'uuid': id})

@login_required(login_url='login')
def initkhalti(request):
    if request.method == "POST":
        url = settings.KHALTI_INITIATE_URL
        return_url = request.POST.get('return_url')
        website_url = request.POST.get('return_url')
        amount = request.POST.get('amount')
        purchase_order_id = request.POST.get('purchase_order_id')

        if not purchase_order_id:
            import uuid
            purchase_order_id = str(uuid.uuid4())

        payload = json.dumps({
            "return_url": return_url,
            "website_url": website_url,
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "test",
            "customer_info": {
                "name": "Ram Shakya",
                "email": "test@khalti.com",
                "phone": "9800000001"
            }
        })

        headers = {
            'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            res_data = response.json()
            print("🔍 KHALTI RESPONSE:", res_data)

            payment_url = res_data.get('payment_url')
            if payment_url:
                return redirect(payment_url)
            return render(request, 'error.html', {'message': res_data})

        except Exception as e:
            return render(request, 'error.html', {'message': f'API error: {e}'})

    return redirect('home')

def verifyKhalti(request):
    url = settings.KHALTI_LOOKUP_URL
    if request.method == 'GET':
        headers = {
            'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        query_status = request.GET.get('status')
        pidx = request.GET.get('pidx')
        purchase_order_id = request.GET.get('purchase_order_id')
        movie_pk = purchase_order_id

        if not movie_pk:
            return render(request, 'myapp/error.html', {'message': 'Missing movie ID'})

        if query_status == 'Completed':
            movie = Movie.objects.get(id=movie_pk)
            Purchase.objects.get_or_create(user=request.user, movie=movie, defaults={'status': 'PAID'})
            request.session[f'paid_for_{movie_pk}'] = True
            return redirect('payment_after_movie', pk=movie_pk)

        if not pidx:
            return render(request, 'myapp/error.html', {'message': 'Missing pidx parameter'})

        try:
            data = json.dumps({'pidx': pidx})
            res = requests.post(url, headers=headers, data=data)
            new_res = res.json()
        except Exception as e:
            return render(request, 'myapp/error.html', {'message': f'API error: {e}'})

        print(new_res)
        status = new_res.get('status')

        if status == 'Completed':
            movie = Movie.objects.get(id=movie_pk)
            Purchase.objects.get_or_create(user=request.user, movie=movie, defaults={'status': 'PAID'})
            request.session[f'paid_for_{movie_pk}'] = True
            return redirect('payment_after_movie', pk=movie_pk)
        else:
            return render(request, 'myapp/error.html', {'message': f'Payment failed: {status}'})

    return redirect('home')













