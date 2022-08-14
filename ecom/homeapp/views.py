
from django.shortcuts import render
from store.models import product 



# Create your views here.
def home(request):
    products = product.objects.all().filter(is_available = True)

    context = {
        'products' : products,
    }
    return render(request, 'index.html',context)