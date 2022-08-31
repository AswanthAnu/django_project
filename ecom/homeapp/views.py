
from unicodedata import category
from django.shortcuts import render
from store.models import product
from category.models import category



# Create your views h


def home(request):
    products = product.objects.all().filter(is_available = True)
    

    context = {
        'products' : products,
       
    }
    return render(request, 'index.html',context)