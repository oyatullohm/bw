
from django.contrib import admin
from django.urls import path ,re_path , include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth.views import LogoutView
from django.views.static import serve as mediaserve 
from django.conf.urls.i18n import i18n_patterns
from django.urls import path

urlpatterns = [
     path('i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns (
    path('',include('main.urls')),
    path('login/',LoginView.as_view(),name='login'),
    path('api/login/', login, name='login_api'),
    
    path('register/',RegisterView.as_view(),name='register'),
    path('register/',RegisterView.as_view(),name='reset_password'),
    path('logout/', logout_, name='logout'),
    path('admin/', admin.site.urls),
)
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT )


# urlpatterns += [
#         re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.STATIC_ROOT}),
#     ]