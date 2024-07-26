from django.urls import path
from .views import *


urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('teacher/<int:pk>/',TeacherView.as_view(),name='teacher'),
]
