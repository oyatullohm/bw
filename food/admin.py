from django.contrib import admin
from .models import Product , ProductCount, Food
# Register your models here.
admin.site.register(ProductCount)
admin.site.register(Product)
admin.site.register(Food)