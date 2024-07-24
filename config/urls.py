
from django.contrib import admin
from django.urls import path ,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as mediaserve
urlpatterns = [
    path('admin/', admin.site.urls),
]
# urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT )
urlpatterns += [
        re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.STATIC_ROOT}),
    ]