
from unicodedata import category
from django.shortcuts import render, get_object_or_404
from .models import product
from category.models import category
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.


def store(request,category_slug= None):
    categories = None
    products = None
    

    if category_slug != None:
        categories = get_object_or_404(category, slug = category_slug  )
        products = product.objects.filter(category = categories, is_available = True)
        product_count = products.count()
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products' : paged_products
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
        
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product, 
        'in_cart'        : in_cart,

    }

    return render(request, 'store/product_detail.html', context)