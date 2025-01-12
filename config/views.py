from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import  login, logout
from django.shortcuts import render, redirect
from django.utils import translation
from django.views import View
from main.models import *
import re

class LoginView(View):
    def get(self,request):
        return render(request, 'login.html')
    # @method_decorator(csrf_protect)
    def post(self, request):
        username = self.sanitize_input(request.POST.get('username'))
        password = self.sanitize_input(request.POST.get('password'))
        keep_me_logged_in = request.POST.get('keep_me_logged_in')
        try:
            user = Teacher.objects.get(username=username)
        except Teacher.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            login(request, user) 
            
            if keep_me_logged_in:
                request.session.set_expiry(1209600)  # Sessiyani 2 haftaga uzaytirish
            else:
                request.session.set_expiry(0)  # Brauzer yopilganda sessiyani tugatish
            
            return redirect('home')  # Tizimga kirganidan keyin yo'naltirish
        else:
            # Parol noto'g'ri yoki foydalanuvchi mavjud emas
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    def sanitize_input(self, value):
        # Maxsus belgilarni qochirish
        if value:
            value = re.sub(r'[^\w\s@.-]', '', value)  # Yaroqsiz belgilarni olib tashlash
        return value


class RegisterView(View):
    def get(self,request):
        return render(request, 'register.html')

    def post(self,request):
        company = request.POST.get('company')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password_2 = request.POST.get('password_2')
        if password == password_2:
            tarif = Tarif.objects.get(name='standart')
            company = Company.objects.create(tarif=tarif,name=company,
                                             phone=phone,start_date=timezone.now(),
                                             end_date=timezone.now()+timedelta(days=30))
            teacher=Teacher.objects.create_user(
                        company=company,
                        username=username,
                        phone=phone,
                        # hired_date = timezone.now(),
                        type = 1,
                        is_payment = True,
                        is_salary = True,
                        is_child = True, 
                        is_main  = True,
                        is_food  = True,
                        password=password                  
            )
            Cash.objects.get_or_create(
                company=company,
                teacher=teacher,
            )
            return redirect('/login')
        return redirect('/register')


def logout_(request):
    logout(request)
    return redirect('login')


def change_language(request, lang_code):
    translation.activate(lang_code)
    request.session['language'] = translation.get_language()
    return redirect('/')