from rest_framework.permissions import BasePermission


class IsPayment(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_payment)


class IsSalary(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_salary)

    
class IsChild(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_child)

