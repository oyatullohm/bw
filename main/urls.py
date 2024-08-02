from django.urls import path
from .views import *


urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('teacher/',TeacherView.as_view(),name='teacher'),
    path('teacher/<int:pk>/',TeacherDetailView.as_view(),name='teacher_detail'),
    path('teacher-password/<int:pk>/',password,name='edit_password'),
    path('add_teacher/',add_teacher,name='add_teacher'),
    path('edit-amount/<int:pk>/',salary,name='edit_amount'),
    path('group',GroupView.as_view(),name='group'),
    path('child',ChildView.as_view(),name='child'),
    path('tarif',TarifCompanyView.as_view(),name='tarif'),
    path('edit-tarif/<int:pk>/',edit_tarif,name='edit_tarif'),
    path('chaild-edit/<int:pk>/',chaild_edit,name='chaild_edit'),
    path('delete-chaild/<int:pk>/',delete_chaild,name='delete_chaild'),
]
