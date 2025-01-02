from django.urls import path
from .views import *

urlpatterns= [
    path('', WarehouseView.as_view(),name='warehous'),
    path('food', FoodView.as_view(),name='food'),
    path('product', ProductView.as_view(),name='product'),
    path('create/product/count/', create_product_count,name='create_product_count'),
    path('create/product/', create_product,name='create_product'),
    path('create/food/', create_food,name='create_food'),
]