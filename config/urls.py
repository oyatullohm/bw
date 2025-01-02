
from django.views.static import serve as mediaserve 
from django.contrib.auth.views import LogoutView
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from .views import *

urlpatterns = [
    path('app/',include('app.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns (
    path('',include('main.urls')), 
    path('food/',include('food.urls')), 
    path('login/',LoginView.as_view(),name='login'),
    path('register/',RegisterView.as_view(),name='register'),
    path('kattaadmin/',admin.site.urls),
    path('logout/',logout_, name='logout'),
    path('api/login/',login, name='login_api'),
    path('change-language/<str:lang_code>/', change_language, name='change_language'),
    
)
# urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT )
urlpatterns += [
        re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.STATIC_ROOT}),
    ]