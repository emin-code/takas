from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('takas.urls')),
    path('giris/', auth_views.LoginView.as_view(template_name='takas/login.html'), name='login'),
    path('cikis/', auth_views.LogoutView.as_view(next_page='takas:anasayfa'), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 