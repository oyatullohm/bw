from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from .viewsets import *
router = DefaultRouter()

router.register('group',GroupViewSet, basename='group')
router.register('user',TeacherViewSet, basename='users')

urlpatterns = [

    path('',HomeApiView.as_view()),
    path('login/',LoginApiView.as_view()),
    path('register/',RegisterApiView.as_view()),
    
]
urlpatterns += router.urls