
from django.contrib import admin
from django.urls import path ,re_path , include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth.views import LogoutView
from django.views.static import serve as mediaserve

urlpatterns = [
    path('',include('main.urls')),
    path('login/',LoginView.as_view(),name='login'),
    path('register/',RegisterView.as_view(),name='register'),
    path('register/',RegisterView.as_view(),name='reset_password'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGIN_URL), name='logout'),
    path('admin/', admin.site.urls),
]
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT )
# urlpatterns += [
#         re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.STATIC_ROOT}),
#     ]