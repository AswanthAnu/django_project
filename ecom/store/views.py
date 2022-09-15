

from ast import keyword
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import product
from category.models import SubCategory, category
from brand.models import brand
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.


def store(request,category_slug= None, brand_slug= None, sub_category_slug=None ):
    categories = None
    brands = None
    products = None
    paged_products = None
    
    try:

        if brand_slug != None:
            
            brands = get_object_or_404(brand, slug = brand_slug  )
            products = product.objects.filter(brand = brands, is_available = True)
            product_count = products.count()
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()


        elif category_slug != None and sub_category_slug == None:
            
            categories = get_object_or_404(category, slug = category_slug  )
           
            products = product.objects.filter(category = categories, is_available = True)
            
            product_count = products.count()
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

        elif category_slug != None and sub_category_slug != None:
            
            categories = get_object_or_404(category, slug = category_slug  )
            sub_categories = get_object_or_404(SubCategory, slug = sub_category_slug  )
            products = product.objects.filter(category = categories, subcategory = sub_categories )
            product_count = products.count()
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

       

        else:
            products = product.objects.all().filter(is_available = True).order_by('id')
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

    except:
        products = product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()


    
    context = {
        'products' : paged_products,
        
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, subcategory_slug,  product_slug):


    try:
        categories = category.objects.get(slug = category_slug)
        products = product.objects.get(slug = product_slug)
        single_product = product.objects.get(category__slug = category_slug, subcategory__slug = subcategory_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
        
    except Exception as e:
        raise e
    

    
    context = {
        'single_product' : single_product, 
        'in_cart'        : in_cart,
        'categories'     : categories,
        'products'       : products,

    }

    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = product.objects.order_by('-create_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword))
            products_count = products.count()
    context = {
        'products' : products,
        'products_count' : products_count,
    }
    return render(request, 'store/store.html', context)