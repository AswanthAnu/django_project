from multiprocessing import context
from pickle import TRUE
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from homeapp.models import banner
from .decorators import log
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.db.models import Count, Sum
import datetime as dt
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlwt


from accounts.models import Account
from category.models import category, SubCategory
from brand.models import brand
from store.models import product, Variation, Coupon
from orders.models import Order, OrderProduct, Payment, ReturnProduct

# Create your views here.
@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def admin_login(request):

    if 'is_admin' in request.session:
        return redirect('admin_dashboard')
    
   


    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password,)
        try:
            if user.is_admin == True:
                request.session['is_admin'] = True
                auth.login(request, user)
                return redirect('admin_dashboard')
            
            else:
                messages.error(request, 'Invalid admin credentials')
                return redirect('admin_login')
        except:
            messages.error(request, 'Invalid admin credentials')
            return redirect('admin_login')

    return render(request, 'admin/admin_login.html')

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def admin_dashboard(request):
    if 'is_admin' not in request.session:
        return redirect('admin_login')

    user = Account.objects.filter(~Q(is_admin=True)).count()
    active_user = Account.objects.filter(Q(is_active = True) & Q(is_admin = False)).count()
    blocked_user = Account.objects.filter(Q(is_active = False) & Q(is_admin = False)).count()
    

    total_orders = Order.objects.all().count()
    pay = Payment.objects.values('payment_method').annotate(count = Count('payment_method'))
    pay_method = []
    pay_count = []
    for i in pay:
        pay_method.append(i['payment_method'])
    for i in pay:
        pay_count.append(i['count'])

    status = Order.objects.filter(is_ordered = True).values('status').annotate(count = Count('status'))
    pay_status = []
    status_count = []
    for i in status:
        pay_status.append(i['status'])
    
    for i in status:
        status_count.append(i['count'])
      
    try: 
        day = 7 
        day = int(request.GET.get('days'))
        order_product_count_graph = OrderProduct.objects.filter().values('created_at__date').order_by('-created_at__date')[:day].annotate(count=Count('quantity'))
    except:
        order_product_count_graph = OrderProduct.objects.filter().values('created_at__date').order_by('-created_at__date')[:7].annotate(count=Count('quantity'))

    


    date = []
    sale_count = []
    order_total =[]
    for i in order_product_count_graph:
        date.append(i['created_at__date'])
    
   
    for i in order_product_count_graph:
        sale_count.append(i['count'])

    payments = Payment.objects.values('amount_paid').all()
    total_sales = 0
    for i in payments:
        total_sales = int( total_sales + float(i['amount_paid']))
    no_of_sales = 0
    no_of_sale = OrderProduct.objects.aggregate(Sum('quantity'))
    no_of_sales = no_of_sale['quantity__sum']

    context = {
        'active_users' : active_user,
        'blocked_users' : blocked_user,
        'pay_method' : pay_method,
        'pay_count' : pay_count,
        'pay_status' : pay_status,
        'status_count' : status_count,
        'date' : date,
        'sale_count' : sale_count,
        'day' : day,
        'no_of_sales':no_of_sales,
        'total_sales':total_sales,

    }


    
    return render(request, 'admin/admin_dashboard.html', context)

def admin_user(request):

    if 'is_admin' not in request.session:
        return redirect('admin_login')
    user = Account.objects.all().order_by('-id')
    paginator = Paginator(user, 10)
    page = request.GET.get('page')
    paged_user = paginator.get_page(page)
    return render(request, 'admin/admin_user.html', {'users' : paged_user})

@log(admin_login)
def block_unblock(request,id):
 
    user = Account.objects.get(id = id)
     
    if user.is_active == True:
        user.is_active = False
        user.save()
        return redirect(admin_user)

    else:
        user.is_active =True
        user.save()
        return redirect(admin_user)

@log(admin_login)   
def admin_category(request):
    categ = category.objects.all().order_by('-id')
    paginator = Paginator(categ, 10)
    page = request.GET.get('page')
    paged_categ = paginator.get_page(page)
    context={'categ' : paged_categ }
   
    return render (request, 'admin/admin_category.html' , context)

@log(admin_login)
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')

        categ = category(category_name = category_name, description = description)
        categ.save()
        return redirect('admin_category')
    return render(request,'admin/admin_category.html')
@log(admin_login)
def edit_category(request):
    categories = category.objects.all()
    context={'categories' : categories }
   
    return render (request, 'admin/admin_category.html' , context)

def update_category(request, id):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        slug = category_name.replace(" ", "-").lower()
        

        categ = category( id = id, category_name = category_name, slug = slug,  description = description)
        categ.save()
        return redirect('admin_category')
    return render(request,'admin/admin_category.html')

def delete_category(request,id):

    categ = category.objects.filter(id = id)
    categ.delete()
    return redirect('admin_category')
    
@log(admin_login)  
def admin_brand(request):
    if 'is_admin' not in request.session:
        return redirect('admin_login')
    brandd = brand.objects.all().order_by('-id')
    paginator = Paginator(brandd, 10)
    page = request.GET.get('page')
    paged_brandd = paginator.get_page(page)
   
    context={'brandd' : paged_brandd}
   
    return render (request, 'admin/admin_brand.html' , context)

@log(admin_login)
def add_brand(request):
    if request.method == "POST":
        brand_name = request.POST.get('brand_name')
        description = request.POST.get('description')

        brandd = brand(brand_name = brand_name, description = description)
        brandd.save()
        return redirect('admin_brand')
    return render(request,'admin/admin_brand.html')

def edit_brand(request):
    brands = brand.objects.all()
    context={'brands' : brands }
   
    return render (request, 'admin/admin_brand.html' , context)

def update_brand(request, id):
    if request.method == "POST":
        brand_name = request.POST.get('brand_name')
        description = request.POST.get('description')
        slug = brand_name.replace(" ", "-").lower()
        

        brandd = brand( id = id, brand_name = brand_name, slug = slug,  description = description)
        brandd.save()
        return redirect('admin_brand')
    return render(request,'admin/admin_brand.html')

def delete_brand(request,id):

    brands = brand.objects.filter(id = id)
    brands.delete()
    return redirect('admin_brand')
    
@cache_control(no_cache =True, must_revalidate =True, no_store =True)
@log(admin_login)    
def admin_product(request):
    if 'is_admin' not in request.session:
        return redirect('admin_login')
    categories = category.objects.all().order_by('-id')
    brands = brand.objects.all().order_by('-id')
    products = product.objects.all().order_by('-id')
    subcategories = SubCategory.objects.all().order_by('-id')
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
   
    context={'products' : paged_products, 'brands': brands, 'categories': categories, 'subcategories' : subcategories }
   
    return render (request, 'admin/admin_product.html' ,  context)

def add_product(request):

    products = product()
    categ = category.objects.all()
    bran = brand.objects.all()  
    subcatd = SubCategory.objects.all()

    if request.method == "POST":

        products.product_name = request.POST.get('product_name')
        products.description = request.POST.get('description')
        products.price = request.POST.get('price')
        products.stock = request.POST.get('stock')
        sl =  request.POST.get('product_name')
        products.slug = sl.replace(" ", "-").lower()
        brands = request.POST.get('brand')
        categories= request.POST.get('category')
        subcategories = request.POST.get('subcategory')
        if products.price == "0" or products.stock == "0" :
            messages.error(request, 'Please Fill with correct Value')
            return redirect('admin_product')
        if len(products.product_name) == 0 or len(categories) == 0 or len(brands) == 0:
            messages.error(request, 'Fields cannot be blank')
            return redirect('admin_product')

        products.category   = category.objects.get(id = categories)
        products.brand   =  brand.objects.get(id = brands)   
        products.subcategory = SubCategory.objects.get(id = subcategories)
        if len(request.FILES) != 0:
            products.images = request.FILES['images']
            products.image2 = request.FILES['image2']
            products.image3 = request.FILES['image3']
        
            products.save()
          
            return redirect('admin_product')
    return render(request,'admin/admin_product.html')

def edit_product(request):
    Products = product.objects.all()
    categories = product.objects.all()
    Products = product.objects.all()
    context={'products' : Products , 'categories' :categories, "Products" : Products}
   
    return render (request, 'admin/admin_product.html' , context)

def update_product(request, id):
    # if request.method == "POST":
    #     brand_name = request.POST.get('brand_name')
    #     description = request.POST.get('description')
    #     slug = brand_name.replace(" ", "-").lower()
        

    #     brandd = brand( id = id, brand_name = brand_name, slug = slug,  description = description)
    #     brandd.save()
    #     return redirect('admin_product')
    # return render(request,'admin/admin_product.html')
    product_detail = product.objects.get(id=id)
    if request.method == 'POST':
        if len(request.FILES) != 0: 
            if product_detail.images:  product_detail.images = request.FILES.get('image1')
              
            if product_detail.image2: product_detail.image2 = request.FILES.get('image2')
             
            if product_detail.image3: product_detail.image3  = request.FILES.get('image3')
               

        product_detail.product_name = request.POST.get('product_name')
        product_detail.description  = request.POST.get('description')
        product_detail.price        = request.POST.get('price')
        product_detail.stock        = request.POST.get('stock')
        if product_detail.price < "0" or product_detail.stock  < "0":
            messages.error(request, 'Please Fill with correct Value')
            return redirect(update_product,id)

        product_detail.save()  
        return redirect(update_product)
       

    products = product.objects.get(id=id)
    categories  = category.objects.all()
    brands  = brand.objects.all()
    return render(request, 'admin/admin_product.html', {'product': product, 'categories': categories, 'brands':brands} )

def delete_product(request,id):
    products = product.objects.filter(id = id)
    products.delete()
    return redirect('admin_product')

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
@log(admin_login)
def admin_variation(request):
    products = product.objects.all().order_by('-id')
    variations = Variation.objects.all().order_by('-id')

    
    paginator = Paginator(variations, 10)
    page = request.GET.get('page')
    paged_variations = paginator.get_page(page)

    context = {
        'variations': paged_variations, 'products' : products
    }

    return render(request, 'admin/admin_variation.html', context )

def add_variation(request):

    prod = product.objects.all()
    variations = Variation()
    bran = brand.objects.all()


    if request.method == "POST":


        variations.product_id = request.POST.get('products')
        variations.variation_category = request.POST.get('variation_category')
        variations.variation_value = request.POST.get('variation_value')

        if len(variations.variation_value.strip()) == 0 :
            return JsonResponse({
                'success' : False} ,
                  safe= False  )
        
        else:   
            variations.save()
            return JsonResponse({
                'success' : True} ,
                  safe= False  )

    return render(request,'admin/admin_variation.html')

def edit_variation(request):
    variations = Variation.objects.all()
    products = product.objects.all()
    context = { 'variations' : variations, 'products' : products}

    return render(request, "admin/admin_variation.html", context)

def update_variation(request, id):


    variation_detail =  Variation.objects.get(id = id)
    if request.method =="POST":
        variation_detail.product_id = request.POST.get('products')
        variation_detail.variation_category = request.POST.get('variation_category')
        variation_detail.variation_value = request.POST.get('variation_value')
        if len(variation_detail.variation_value.strip()) == 0 :
            return JsonResponse({
                'success' : False} ,
                    safe= False  )
    
        else:   
            variation_detail.save()
            return JsonResponse({
                'success' : True} ,
                    safe= False  )
    return render(request,'admin/admin_variation.html' )

def delete_variation(request, id):
        variations = Variation.objects.filter(id = id)
        variations.delete()
        return JsonResponse({
            'success': True
        }, safe= False)

def admin_subcategory(request):

    subcategory = SubCategory.objects.all().order_by('-id')
    categories = category.objects.all().order_by('-id')
    paginator = Paginator(subcategory, 10)
    page = request.GET.get('page')
    paged_subcategory = paginator.get_page(page)
    context={'subcategory' : paged_subcategory, 'categories' : categories  }


    return render(request, 'admin/admin_subcategory.html', context)

def add_subcategory(request):

    if request.method == "POST":

        category_id = request.POST.get('category')
        subcategory_name = request.POST.get('subcategory_name')
        description = request.POST.get('description')
        slug = subcategory_name.replace(" ", "-").lower()

        if len(subcategory_name.strip()) == 0:
            return JsonResponse({
                'success' : False} ,
                  safe= False  )
        else:
            subcategory = SubCategory( category_id = category_id,  sub_category_name = subcategory_name, slug = slug  )   
            subcategory.save()
            return JsonResponse({
                'success' : True} ,
                  safe= False  )

    return render(request,'admin/admin_category.html')

def edit_subcategory(request):
    subcategory = SubCategory.objects.all()
    
    context = { 'subcategory' : subcategory}

    return render(request, "admin/admin_variation.html", context)

def update_subcategory(request, id):
    if request.method == "POST":

        subcategory = SubCategory.objects.get(id = id)
        subcategory.subcategory_name = request.POST['subcategory_name']
        
        subcategory.slug = subcategory.subcategory_name.replace(" ", "-").lower()

        if len(subcategory.subcategory_name.strip()) == 0:
            return JsonResponse({
                'success' : False} ,
                  safe= False  )
        else:
            subcategory.save()
            return JsonResponse({
                'success' : True} ,
                  safe= False  )

    return render(request,'admin/admin_subcategory.html')

def delete_subcategory (request, id):
        subcategory = SubCategory.objects.filter(id = id)
        subcategory.delete()
        return JsonResponse({
            'success': True
        }, safe= False)

def admin_order(request):

    orderproducts = OrderProduct.objects.all().order_by('-id')
    paginator = Paginator(orderproducts, 10)
    page = request.GET.get('page')
    paged_orderproducts = paginator.get_page(page)
    total_orders_count= OrderProduct.objects.all().count()
    orders_pending = Order.objects.filter(status__contains='New', is_ordered = True).count()
    orders_deliverd = Order.objects.filter(status__contains='Completed').count()

    context = {
        'orderproducts': paged_orderproducts,
        'total_orders_count': total_orders_count,
        'orders_pending' : orders_pending,
        'orders_deliverd' : orders_deliverd,
    }
    return render(request, 'admin/admin_order.html', context)       

def change_order_status(request,st,oid,pid):
    order_product_details = Order.objects.get(order_number=oid)
    order_product_details.status = st
    order_product_details.save()
    order_product_details=Order.objects.all().order_by('-created_at')
    orders_pending = Order.objects.filter(status__contains='New').count()
    return HttpResponse(orders_pending)
 
def admin_cancel_order(request,oid):
    order_cancel = Order.objects.get(id=oid)
    order_cancel.status = 'Cancelled'
    order_cancel.save()
    return HttpResponseRedirect(reverse('index'))

def admin_offer(request):

    products = product.objects.all().order_by('-id')
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'productss' : paged_products,
        'products'  : products
    }


    return render(request, 'admin/admin_offer.html', context)

def add_offer(request):

    if request.method == "POST":
        product_id = request.POST.get('product_id')
        prdct_ofer = request.POST.get('prdct_offer')
        prdct_offer = int(prdct_ofer)

        if prdct_offer < 0 or prdct_offer > 80  :
            return JsonResponse({
                'success' : False} ,
                  safe= False  )

        else:
            products = product.objects.get(id = product_id)
            
            products.discount = prdct_offer
            
            products.save()
            return JsonResponse({
                'success' : True} ,
                  safe= False  )

    return render(request,'admin/admin_offer.html')

def edit_offer(request):
    if request.method == "POST":
        product_name = request.POST.get('product_name')
        product_offer = int(request.POST.get('product_offer'))
        category_name = request.POST.get('category_name')
        category_offer = int(request.POST.get('category_offer'))
        

        if product_offer < 0 or product_offer > 80  :
            return JsonResponse({
                'product_offer' : False} ,
                  safe= False  )
        elif category_offer < 0 or category_offer > 80  :
            return JsonResponse({
                'category_offer' : False} ,
                  safe= False  )
        else:
            products = product.objects.get(product_name = product_name)
            categories = category.objects.get(category_name = category_name)
            products.discount = product_offer
            categories.discount = category_offer
            products.save()
            categories.save()
            return JsonResponse({
            'success' : True} ,
                safe= False  )

        




def delete_offer(request, id):

    products = product.objects.get(id = id )
    products.discount = 0
    products.save()
    return JsonResponse({
            'success': True
        }, safe= False)

def admin_offer_cat(request):

    categories = category.objects.all().order_by('-id')
    paginator = Paginator(categories, 10)
    page = request.GET.get('page')
    paged_categories = paginator.get_page(page)

    context = {
        'categoriess' : paged_categories,
        'categories'  : categories,
    }

    return render(request, 'admin/admin_offer_cat.html', context)

def add_offer_cat(request):

    if request.method == "POST":
        category_id = request.POST.get('category_id')
        categ_ofer = request.POST.get('categ_offer')
        categ_offer = int(categ_ofer)

        if categ_offer < 0 or categ_offer > 80  :

            return JsonResponse({
                'success' : False} ,
                  safe= False  )

        else:
            categories = category.objects.get(id = category_id)
            
            categories.discount = categ_offer
            
            categories.save()
            return JsonResponse({
                'success' : True} ,
                  safe= False  )


    return render(request, 'admin/admin_offer_cat.html' )

def delete_offer_cat(request, id):

    cateogries = category.objects.get(id = id)
    cateogries.discount = 0
    cateogries.save()
    return JsonResponse({
            'success': True
        }, safe= False)

def admin_coupon(request):

    coupons = Coupon.objects.all().order_by('-id')
    paginator = Paginator(coupons, 10)
    page = request.GET.get('page')
    paged_coupons = paginator.get_page(page)

    context = {
        'couponss' : paged_coupons,
        'coupons'  : coupons,
    }

    return render(request, 'admin/admin_coupon.html', context )

def add_coupon(request):

    if request.method == "POST":
        coupon_cod = request.POST.get('coupon_code')
        discount = int(request.POST.get('add_discount'))
        maximum_amount = int(request.POST.get('add_maximum'))
        minimum_amount = int(request.POST.get('add_minimum'))
        coupon_code = coupon_cod.replace(" ", "")
        try:
            coupon = Coupon.objects.get(coupon_code = coupon_code)
            if coupon.coupon_code == coupon_code:
                return JsonResponse(
                    { 'coupon_exist' : True}, safe= False
                )
        except:
            if discount < 0 or discount > 80:
                return JsonResponse(
                    {'discount' : False }, safe= False
                )

            elif minimum_amount < 0 or minimum_amount > 1000 :
                return JsonResponse(
                    { 'minimum' : False}, safe= False
                )
            elif maximum_amount < 1000 :
                return JsonResponse(
                    {'maximum' : False }
                )
            else:

                coupons = Coupon.objects.create(coupon_code = coupon_code, disccount = discount,minimum_amount = minimum_amount, maximum_amount = maximum_amount  )
                coupons.save()
                return JsonResponse(
                    {'success' : True}, safe= False
                )   

    return render(request, 'admin/admin_coupon.html', context )


def expire_coupon(request , id ):
    coupons = Coupon.objects.get(id = id )
    if coupons.is_expired == True:
        coupons.is_expired = False
        coupons.save()
        return JsonResponse({
                'success': True
            }, safe= False)
    elif coupons.is_expired == False:
        coupons.is_expired = True
        coupons.save()
        return JsonResponse({
                'success': False
            }, safe= False)

def admin_return(request):
    return_product = ReturnProduct.objects.all().order_by('-id')
    paginator = Paginator(return_product, 10)
    page = request.GET.get('page')
    paged_return_product = paginator.get_page(page)

    context = {
        'return_products' : paged_return_product,
        'return_product'  : return_product,
    }
    return render(request, 'admin/admin_return.html', context)

def admin_sales(request, *args, **kwargs):

    products = product.objects.all()
    
    total_with_offer=0
      
    dates_date =OrderProduct.objects.values('created_at__date').distinct().order_by('created_at__date')
    
   
    dates=[]
    for dd in dates_date:
        
       
        dates.append(dd['created_at__date'].strftime("%Y-%m-%d"))
    
    try:
            
        dates_max=dates[-1]
        salesdate=dates[-1]
    except:
        dates_max=''
        salesdate=''
    current_date =dates_max
    dates_len =len(dates)
    dates_len-=dates_len
  
    try:
        sales = OrderProduct.objects.filter(created_at__date=dates[-1]).values('product_id').annotate(qty=Sum('quantity'))
        grandtotalfind=OrderProduct.objects.filter(created_at__date=dates[-1]).all()
        total_without_discount=0
        for t in grandtotalfind:
            total_without_discount+=(t.product.price)*(t.quantity)
    except:
        sales=[]
    # get total money earned in day qty*productprice
        try:
            total_earn= Payment.objects.filter(created_at=dates[-1]).aggregate(Sum('amount_paid'))
        except:
            pass
    try:
                
              total_earn= Payment.objects.filter(created_at=salesdate).all()
              total=0
              for t in total_earn:
                total+=float(t.amount_paid)
    except:
            total="calculating"
    if request.method=="POST":
        try:
            salesdates = True
            salesdate =request.POST['salesdate']

            sales = OrderProduct.objects.filter(created_at__date=salesdate).values('product_id').annotate(qty=Sum('quantity'))
            grandtotalfind=OrderProduct.objects.filter(created_at__date=salesdate).all()
            total_without_discount=0
            total_with_offer=0
            for t in grandtotalfind:
                total_without_discount+=(t.product.price)*(t.quantity)
                total_with_offer+=int((t.product_price)*(t.quantity))
            for s in sales:
                    pass
            current_date=salesdate
        except KeyError:
            pass
            salesdate=dates_max
      
        try:
              total_payment= Payment.objects.filter(created_at__date=salesdate).all()
              total=0
              for t in total_payment:
                total+=float(t.amount_paid)
        except:
            total="calculating"   
    else:
        try:
            salesdates = None

            sales = OrderProduct.objects.filter().values('product_id').annotate(qty=Sum('quantity'))
            grandtotalfind=OrderProduct.objects.filter().all()
            total_without_discount=0
            total_with_offer=0
            for t in grandtotalfind:
                total_without_discount+=(t.product.price)*(t.quantity)
                total_with_offer+=int((t.product_price)*(t.quantity))
            
            
            for s in sales:
                    pass
            current_date=salesdate
        except KeyError:
            pass
            salesdate=dates_max
      
        try:
              total_payment= Payment.objects.filter(created_at__date=salesdate).all()
              total=0
              for t in total_payment:
                total+=float(t.amount_paid)
        except:
            total="calculating" 

    context= {
      'dates':dates,
      'dates_max':dates_max,
      'current_date':current_date,
      'sales':sales,
        'products':products,
        'salesdate':salesdate,
        'salesdates':salesdates,
        'total':total,
        'total_without_discount':total_without_discount,
        'total_with_offer' : total_with_offer,

    }





    return render( request, 'admin/admin_sales.html', context)

def export_pdf(request):


    products = product.objects.all()
    
    
    dates_date =OrderProduct.objects.values('created_at__date').distinct().order_by('created_at__date')
    
   
    dates=[]
    for dd in dates_date:
        
       
        dates.append(dd['created_at__date'].strftime("%Y-%m-%d"))
    
    try:
            
        dates_max=dates[-1]
        salesdate=dates[-1]
    except:
        dates_max=''
        salesdate=''
    current_date =dates_max
    dates_len =len(dates)
    dates_len-=dates_len
  
    try:
        sales = OrderProduct.objects.filter(created_at__date=dates[-1]).values('product_id').annotate(qty=Sum('quantity'))
        grandtotalfind=OrderProduct.objects.filter(created_at__date=dates[-1]).all()
        total_without_discount=0
        for t in grandtotalfind:
            total_without_discount+=(t.product.price)*(t.quantity)
    except:
        sales=[]
    # get total money earned in day qty*productprice
        try:
            total_earn= Payment.objects.filter(created_at=dates[-1]).aggregate(Sum('amount_paid'))
        except:
            pass
    try:
                
              total_earn= Payment.objects.filter(created_at=salesdate).all()
              total=0
              for t in total_earn:
                total+=float(t.amount_paid)
    except:
            total="calculating"
    if request.method=="POST":
        try:
            salesdate =request.POST['salesdate_pdf_id']

            sales = OrderProduct.objects.filter(created_at__date=salesdate).values('product_id').annotate(qty=Sum('quantity'))
            grandtotalfind=OrderProduct.objects.filter(created_at__date=salesdate).all()
            total_without_discount=0
            total_with_offer=0
            for t in grandtotalfind:
                total_without_discount+=(t.product.price)*(t.quantity)
                total_with_offer+=(t.product_price)*(t.quantity)
            
            for s in sales:
                    pass
            current_date=salesdate
        except KeyError:
            pass
            salesdate=dates_max
      
        try:
              total_payment= Payment.objects.filter(created_at__date=salesdate).all()
              total=0
              for t in total_payment:
                total+=float(t.amount_paid)
        except:
            total="calculating"    

    template_path = 'export/sales_pdf.html'  
    context= {
      'dates':dates,
      'dates_max':dates_max,
      'current_date':current_date,
      'sales':sales,
        'products':products,
        'salesdate':salesdate,
        'total':total,
        'total_without_discount':total_without_discount,
        'total_with_offer' : total_with_offer,

    }



    response = HttpResponse(content_type ='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
   
    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def export_excel(request):
    if request.method=='POST':
        salesdate=request.POST['salesdate_excel']
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=SalesReport' +str(dt.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('SalesReport')
    row_num = 0
    font_style =xlwt.XFStyle()
    font_style.font.bold =True

    columns = ['order number','name ','amount ','tax','date']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num, columns[col_num],font_style)
    
    font_style= xlwt.XFStyle()

    rows = Order.objects.filter(Q(created_at__date=salesdate) & Q(is_ordered=True)).values_list('order_number','first_name','order_total','tax','created_at__date')

    for row in rows:
        row_num+=1

        for col_num in range(len(row)):
            ws.write(row_num,col_num, str(row[col_num]),font_style)

    wb.save(response)

    return response

def admin_banner(request):
    banners = banner.objects.all().order_by('id')
    paginator = Paginator(banners, 1)
    page = request.GET.get('page')
    paged_banners = paginator.get_page(page)
   

    context={
        'banners':paged_banners,
    }

    return render(request, 'admin/admin_banner.html', context)

def banner_select(request, id):
    banners = banner.objects.get(id = id)
    if banners.is_selected == True:
        banners.is_selected = False
    else:
        banners.is_selected = True
    banners.save()

    return redirect('admin_banner')

def add_banner(request):
    banners = banner()
    if request.method == "POST":
        banners.banner_image = request.FILES['images']
        banners.save()

        return redirect('admin_banner')
        


@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def admin_logout(request):

    
    request.session.flush() 
    auth.logout(request)

    return redirect(admin_login)