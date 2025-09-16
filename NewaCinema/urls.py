from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views  # ✅ Import this

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', RedirectView.as_view(url='/landingPage/', permanent=False)),  # Redirect root
    path('', include('newa_cinema.urls')),

    # ✅ Override the login URL to use your custom template
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='login_registration/login.html'),
        name='login'
    ),
    path('accounts/', include('django.contrib.auth.urls')),  # Keep this for other auth URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
