
from django.contrib import admin
from django.urls import path ,re_path , include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth.views import LogoutView
from django.views.static import serve as mediaserve 

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



urlpatterns = [
    path('',include('main.urls')),
    path('login/',LoginView.as_view(),name='login'),
    path('api/login/', login, name='login_api'),
    
    path('register/',RegisterView.as_view(),name='register'),
    path('register/',RegisterView.as_view(),name='reset_password'),
    path('logout/', logout_, name='logout'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT )
# urlpatterns += [
#         re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.STATIC_ROOT}),
#     ]