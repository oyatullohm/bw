from django.urls import path
from .views import *



urlpatterns = [

    path('', HomeApiView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('register/', RegisterApiView.as_view()),
]
