from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta , date
from django.db.models import Q, Sum, Case, When, DecimalField , F ,Prefetch


class Tarif(models.Model):
    name = models.CharField(max_length=155)
    summa = models.PositiveIntegerField(default=0)
    child = models.PositiveIntegerField(default=0)
    user = models.PositiveIntegerField(default=0)
    group = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Company(models.Model):
    tarif = models.ForeignKey(Tarif, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=155,default=0)
    phone = models.CharField(max_length=15)
    working_day = models.PositiveIntegerField(default=22) 
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class TarifCompany(models.Model):
    STATUS = (
        (1,'Hodimlar'),
        (2,'Bolalar')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='salaries')
    name = models.CharField(max_length=100)
    status = models.PositiveIntegerField(default=1,choices=STATUS)
    amount = models.DecimalField(max_digits=10, decimal_places=0,default=0)
    created = models.DateField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name}"


class Teacher(AbstractUser):
    TYPE = (
        (1, 'direktor'),
        (2, 'tarbiyachi'),
        (3, 'yordamchi')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True , related_name='teachers')
    phone = models.CharField(max_length=15) 
    tarif = models.ForeignKey(TarifCompany, on_delete=models.SET_NULL, null=True, blank=True,)
    type = models.PositiveIntegerField( choices=TYPE, default=1)
    is_payment = models.BooleanField(default=False)
    is_salary = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    

class Group(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=100)
    teacher = models.OneToOneField(Teacher, on_delete=models.SET_NULL, null=True, blank=True,  related_name='group_teachers')
    helper = models.OneToOneField(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_helpers')
    is_active = models.BooleanField(default=True)

    
class Child(models.Model):
    STATUS = (
        (1,"yigit"),
        (2,"qiz")
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    tarif = models.ForeignKey(TarifCompany, on_delete=models.SET_NULL, null=True, blank=True,)
    birth_date = models.DateField()
    phone = models.CharField(max_length=15)
    status = models.PositiveIntegerField(default=1)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='child', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name

class Attendance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendances')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True, related_name='attendances')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    presence = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')}"


class Payment(models.Model):
    TYPE_CHOICES = (
        (1, 'Kirim'),
        (2, 'Chiqim'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='payments_user')# chiqim qilayotgan user Yoki krim 
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True, related_name='payments') 
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='payment_teachers') # oylik ilishi 
    date = models.DateField(default=timezone.now)
    
    user_before_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    user_after_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    date_month = models.DateField(null=True ,blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.PositiveIntegerField(default=1,choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_edit = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.child:
            return f"{self.child.name} - {self.date} - {self.amount} {self.payment_type}"
        elif self.teacher:
            return f"{self.teacher.first_name} - {self.date} - {self.amount} {self.payment_type}"
        else:
            return f"General - {self.date} - {self.amount} {self.payment_type}"

    class Meta:
        ordering = ['-date']


class Transfer(models.Model):
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='transfers')
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='user')
    teacher_1 = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_1')
    teacher_2 = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='transfer_1')
   
    teacher_1_before_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    teacher_1_after_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    teacher_2_before_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    teacher_2_after_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    date = models.DateField(auto_now_add=True)
    summa = models.DecimalField(default=0,max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.summa} {self.user}'


class Cash(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cashs')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='cash')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.amount}"
