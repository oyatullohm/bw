from django.views import View
from django.shortcuts import render , redirect
from main.models import *
from django.contrib.auth import authenticate, login 
from django.contrib.auth.hashers import make_password, check_password
class LoginView(View):
    def get(self,request):
        return render(request, 'login.html')
    
     
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
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
            company = Company.objects.create(tarif=tarif,name=company)
            Teacher.objects.create_user(
                        company=company,
                        username=username,
                        phone=phone,
                        hired_date = timezone.now(),
                        type = 1,
                        is_payment = True,
                        is_salary = True,
                        is_child = True, 
                        password=password                  
            )
        
            return redirect('/login')
        return redirect('/register')


