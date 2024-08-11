from django.urls import path
from .views import *
from .ajax import *


urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('teacher/',TeacherView.as_view(),name='teacher'),
    path('teacher/<int:pk>/',TeacherDetailView.as_view(),name='teacher_detail'),
    path('teacher-password/<int:pk>/',password,name='edit_password'),
    path('add_teacher/',add_teacher,name='add_teacher'),
    path('edit-amount/<int:pk>/',salary,name='edit_amount'),
    path('group',GroupView.as_view(),name='group'),
    path('group-detail/<int:pk>/',GroupDetailView.as_view(),name='group_detail'),
    path('update-attendance-child/', UpdateAttendanceChildView.as_view(), name='update-attendance'),
    path('update-attendance-teacher/', UpdateAttendanceTeacherView.as_view(), name='update-attendance-teacer'),
    path('update-payment/', UpdatePaymenntView.as_view(), name='update-payment'),
    path('child',ChildView.as_view(),name='child'),
    path('tarif',TarifCompanyView.as_view(),name='tarif'),
    path('edit-tarif/<int:pk>/',edit_tarif,name='edit_tarif'),
    path('chaild-edit/<int:pk>/',chaild_edit,name='chaild_edit'),
    path('chaild-edit-tarif/<int:pk>/',chaild_edit_tarif,name='chaild_edit_tarif'),
    path('delete-chaild/<int:pk>/',delete_chaild,name='delete_chaild'),
    path('calendar/child/<int:pk>/',calendar_child,name='calendar_child'),
    path('calendar/teacher/<int:pk>/',calendar_teacher,name='calendar_teacher'),
    path('payment/child/<int:pk>/',payment_child,name='payment_child'),
    path('payment/',PaymentView.as_view(), name='payment'),
    path('payment-cost/',PaymentCostView.as_view(), name='payment_cost'),
    path('payment-create/',PaymentCreateView.as_view(), name='payment-create'),
    path('cash/',CashView.as_view(), name='cash'),
    path('transfer/',TransferView.as_view(), name='transfer'),
    path('get-teacher-cash/', get_teacher_cash, name='get_teacher_cash'),
    path('transfer-create/',TransferCreateView.as_view(), name='transfer_create'),
    path('search-payment-cost/',search_payment_cost, name='search_payment_cost'),
    path('search-payment/',search_payment, name='search_payment'),
    

]
