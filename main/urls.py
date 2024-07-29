from django.urls import path
from .views import *


urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('teacher/',TeacherView.as_view(),name='teacher'),
    path('teacher/<int:pk>/',TeacherDetailView.as_view(),name='teacher_detail'),
    path('teacher-password/<int:pk>/',password,name='edit_password'),
    path('add_teacher/',add_teacher,name='add_teacher'),
]
