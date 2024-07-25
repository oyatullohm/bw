from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    name = models.CharField(max_length=155)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Teacher(AbstractUser):
    TYPE = (
        (1, 'direktor'),
        (2, 'tarbiyachi'),
        (3, 'yordamchi')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='teachers')
    phone = models.CharField(max_length=15) 
    hired_date = models.DateField(null=True, blank=True)
    type = models.PositiveIntegerField( choices=TYPE, default=1)
    is_payment = models.BooleanField(default=False)
    is_salary = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.username

class Child(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    phone = models.CharField(max_length=15)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, related_name='child_groups')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='group_teachers')
    helper = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='group_helper')
    children = models.ManyToManyField(Child, related_name='group_children', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Salary(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='salaries')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True, related_name='salaries') 
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='salaries')
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.month.strftime('%Y-%m')}"

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
        ('1', 'Kirim'),
        ('2', 'Chiqim'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='payments_user')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='payment_teachers')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
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
    teacher_chief = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_chiefs')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='transfers')
    text = models.TextField(null=True)
    date = models.DateField(auto_now_add=True)
    summa = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.summa} {self.text}'

class Cash(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cashes')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='cash_teachers')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.amount}"
