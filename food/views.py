from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render , redirect
from django.http import JsonResponse
from django.views import View 
from django.db import transaction
from .models import *
import json


def get_last_12_weeks():
    today = datetime.today()
    weeks = []

    # Joriy hafta
    if today.weekday() == 0:  # Agar bugun dushanba bo'lsa
        start_of_week = today
    else:
        start_of_week = today - timedelta(days=today.weekday())  # Dushanba

    end_of_week = start_of_week + timedelta(days=6)  # Yakshanba
    weeks.append({
        'start_date': start_of_week.date(),
        'end_date': end_of_week.date(),
    })

    # Oldingi 11 hafta
    for i in range(11):  # 12 haftani to'ldirish uchun yana 11 hafta
        end_of_week = start_of_week - timedelta(days=1)  # O'tgan haftaning yakshanbasi
        start_of_week = end_of_week - timedelta(days=6)  # O'tgan haftaning dushanbasi
        weeks.append({
            'start_date': start_of_week.date(),
            'end_date': end_of_week.date(),
        })
    
    return weeks

unit = [{'id': i[0], 'name': i[1]} for i in UNIT]

class WarehouseView(LoginRequiredMixin,View):
    def get(self,request):
        products = ProductCount.objects.filter(company=request.user.company)
        total_summa_all = products.aggregate(total_summa_all=Sum(F('price') * F('count')))['total_summa_all']
                            
        context = {
            'products':products,
            'unit':unit,
            "total_summa_all":total_summa_all
        }
        return render(request , 'food/warehouse.html',context)


class FoodView(LoginRequiredMixin, View):
    def get(self, request):
        week = request.GET.get('week')
        page = request.GET.get('page')
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
        weeks = get_last_12_weeks()
        
        start_date = datetime(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)  # Keyingi oyning birinchi kuni
        end_date = next_month - timedelta(days=next_month.day)  # Tanlangan oyning oxirgi kuni
       
        if week:
            week = week.split('+')
            start_date = week[0].strip()
            end_date = week[1].strip()
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
 
        product = ProductCount.objects.filter(company=request.user.company)
        
        food = Food.objects.filter(company=request.user.company).order_by('-id')\
            .prefetch_related('foods__product')\
            .annotate(
        total_summa=Sum(F('foods__summa'), output_field=DecimalField())
        )

        food_summa = food.filter(
                             date__range=(start_date, end_date))\
                            .aggregate(total=Sum('total_summa'))['total']
                            
        paginator = Paginator(food, 25)  # Sahifalarni 25 tadan ko'rsatish
        try:
            paginator = paginator.page(page)
        except PageNotAnInteger:
            paginator = paginator.page(1)
        except EmptyPage:
            paginator = paginator.page(paginator.num_pages)
        context = {
            'food':paginator,
            'product':product,
            'unit':unit ,
            'weeks':weeks,
            'month':month,
            'year':year,
            'food_summa':food_summa
        }
        return render(request , 'food/food.html',context)


class ProductView(LoginRequiredMixin, View):
    def get(self, request):
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))

        start_date = datetime(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)  # Keyingi oyning birinchi kuni
        end_date = next_month - timedelta(days=next_month.day)  # Tanlangan oyning oxirgi kuni

        page = request.GET.get('page')
        product = Product.objects.filter(
            company=request.user.company,
            type = 1).order_by('-id')
        
        
        product_Total_summa  = product.filter(
            date__range=(start_date, end_date)
        ).aggregate(total_summa_all= Sum('summa'))['total_summa_all'] or 0 
        
        
        paginator = Paginator(product, 25)  # Sahifalarni 25 tadan ko'rsatish
        try:
            paginator = paginator.page(page)
        except PageNotAnInteger:
            paginator = paginator.page(1)
        except EmptyPage:
            paginator = paginator.page(paginator.num_pages)
        context = {
            'product':paginator,
            'product_Total_summa':product_Total_summa,
            'year':year,
            "month":month,
            "unit":unit
        }
        return render(request, 'food/product.html', context)


@login_required 
def create_product_count(request):
    name = request.POST.get('name')
    unit = request.POST.get('unit')
    product_count = ProductCount.objects.get_or_create(
        company = request.user.company,
        name=name,
        unit = unit
    )
    return redirect('/food')


@login_required
def create_product(request):
    product = request.POST.get('product')
    unit = request.POST.get('unit')
    count = request.POST.get('count')
    price = request.POST.get('price')
    product = ProductCount.objects.get(id=int(product))
    product.price = price
    product.count += Decimal(count)
    product.save()
    
    Product.objects.create(
        company = request.user.company,
        user=request.user,
        type=1,
        product=product,
        unit=unit,
        price= price,
        quantity=Decimal(count)
        
    )
    return redirect('/food')


@login_required
def create_food(request):
    try:
        data = json.loads(request.body)  # JSON ma'lumotni o'qing
        company = request.user.company
        name = data[0].get('name', None)
        user = request.user

        if not name:
            return JsonResponse({'error': 'Food name is required'}, status=400)

        with transaction.atomic():  # Transaction orqali barcha operatsiyalarni boshqarish
            # Yangi food yaratish
            food = Food.objects.create(company=company,user=user, name=name)

            # `Product` modellarini yaratish uchun vaqtinchalik saqlash
            products_to_create = []
            product_ids = []

            for item in data:
                product_id = item.get('product')
                unit = item.get('unit')
                count = item.get('count')
                # Har bir mahsulot uchun tekshirish
                if not all([product_id, unit, count]):
                    return JsonResponse({'error': 'Incomplete data in request'}, status=400)

                # Unit konvertatsiyasi
                unit_conversion = 1000 if unit in ['g', 'ml'] else 1
                adjusted_count = Decimal(count) / Decimal(unit_conversion)
                p_count = ProductCount.objects.get(id=product_id)
                products_to_create.append(
                    Product(
                        company=company,
                        user=user,
                        type=2,
                        product = p_count,
                        unit=unit,
                        quantity=Decimal(count),
                        food = food,
                        price = p_count.price, 
                        summa = Product(
                            company=company,
                            user=user,
                            type=2,
                            product_id=product_id,
                            unit=unit,
                            quantity=Decimal(count),
                            food=food,
                            ).calculate_summa(), 
                    )
                )
                product_ids.append(product_id)
            Product.objects.bulk_create(products_to_create)
            
            product_counts_to_update = [
                ProductCount(
                    id=product_id, 
                    count=F('count') - adjusted_count  # O'zini ishlatamiz, quantity emas
                )
                for product_id in product_ids
            ]
            
            ProductCount.objects.bulk_update(product_counts_to_update, ['count'])
        
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
