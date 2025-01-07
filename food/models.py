from main.models import Company, Teacher, timezone, date, datetime, timedelta, F, Sum, DecimalField
from django.db import models
from decimal import Decimal, ROUND_DOWN

UNIT = (
        ('pc', 'dona'),
        ('g', 'Gram'),
        ('kg', 'Kilogram'), 
        ('lt', 'Liter'),
        ('ml', 'Millilitre')
    )


class ProductCount(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='product_counts')
    name = models.CharField(max_length=100)  # Mahsulot nomi (olma, yog', go'sht va h.k.)
    unit = models.CharField(max_length=20,choices=UNIT)  # O'lchov birlig
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)  # Mahsulotning narxi (ixtiyoriy)
    count = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    is_active  = models.BooleanField(default=True)  # Mahsulot aktivligi
    
    @property
    def total_summa(self):
        result = Decimal(self.count) * Decimal(self.price)
        return result.quantize(Decimal('1'), rounding=ROUND_DOWN)  # Natijani ikki o‘nlik kasr bilan qaytarish

    def formatted_count(self):
        # Agar kasr qismi `0.000` bo‘lsa, faqat butun qismi chiqadi
        if self.unit == 'pc' :
            return int(self.count)  # Butun qismni qaytarish
        return Decimal(self.count)


class Food(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='daily_usages')
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='food_users') 
    name = models.CharField(max_length=100)  # Ovqat nomi (osh, manti, sho'rva va h.k.)
    # product = models.ManyToManyField(Product, related_name='daily_usages')  # Qaysi mahsulot
    date = models.DateField(default=timezone.now) # Ovqat tayyorlangan sana
    is_active  = models.BooleanField(default=True)  # food aktivligi


class Product(models.Model):
    TYPE = (
        (1,'krim'),
        (2,'Chqim')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='product_users') 
    type = models.PositiveIntegerField( choices=TYPE, default=1)  # Mahsulot nomi (olma, yog', go'sht va h.k.)
    unit = models.CharField(max_length=20,choices=UNIT)  # O'lchov birlig
    food = models.ForeignKey(Food,on_delete=models.CASCADE, null=True, blank=True, related_name='foods')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # miqdor
    product = models.ForeignKey(ProductCount, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    summa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Mahsulotning narxi (ixtiyoriy)
    date = models.DateField(default=timezone.now) # Ovqat tayyorlangan sana
    is_active  = models.BooleanField(default=True)  # Mahsulot aktivligi

    def formatted_quantity(self):
        # Agar kasr qismi `0.000` bo‘lsa, faqat butun qismi chiqadi
        if self.unit == 'pc' :
            return int(self.quantity)  # Butun qismni qaytarish
        return Decimal(self.quantity)
    
    def __str__(self):
        return self.product.name
     
    def calculate_summa(self):
        """
        Umumiy narxni hisoblaydi va summa maydoniga saqlaydi.
        """
        unit_conversion = 1  # Kilogram yoki litrda birligi bo'lsa
        if self.unit in ['g', 'ml']:
            unit_conversion = 1000  # Gram yoki millilitrni kilogram yoki litrga aylantirish
        
        try:
        # `self.quantity` va `self.product.price` ni raqamga aylantirish
            quantity = Decimal(self.quantity) if self.quantity else Decimal('0')
            price = Decimal(self.product.price) if self.product and self.product.price else Decimal('0')

        # Hisoblash
            return (quantity / Decimal(unit_conversion)) * price
        except (TypeError, ValueError) as e:
        # Agar noto'g'ri qiymat bo'lsa, 0 qaytariladi
            return Decimal('0')
        
    
    def save(self, *args, **kwargs):
        self.summa = int(self.calculate_summa())
        super().save(*args, **kwargs)




