
from unicodedata import category
from django.shortcuts import render
from store.models import product
from category.models import category
from .models import banner



# Create your views h


def home(request):
    products = product.objects.all().filter(is_available = True).order_by('-create_date')[:6]
    banners = banner.objects.filter( is_selected = True )[:3]


    context = {
        'products' : products,
        'banners': banners,
       
    }
    return render(request, 'index.html',context)