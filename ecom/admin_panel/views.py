from math import prod
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from accounts.models import Account
from category.models import category
from brand.models import brand
from store.models import product
from .decorators import log
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def admin_login(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email)
        print(password)

        user = authenticate(email=email, password=password,)
        
        if user.is_admin == True:
            request.session['email'] = email
            print(user.is_admin)
            auth.login(request, user)
            print('dash')
            return redirect('admin_dashboard')
           
        else:
            print('else')
            messages.error(request, 'Invalid admin credentials')
            return redirect('admin_login')

    return render(request, 'admin/admin_login.html')

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
@log(admin_login)
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')


def admin_user(request):
    user = Account.objects.all()
    return render(request, 'admin/admin_user.html', {'users' : user})



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
def admin_product(request):
    return render (request, 'admin/admin_product.html')


@log(admin_login)   
def admin_category(request):
    categ = category.objects.all()
    context={'categ' : categ }
   
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
    

   
def admin_brand(request):
    brandd = brand.objects.all()
    context={'brandd' : brandd }
   
    return render (request, 'admin/admin_brand.html' , context)



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
    


      
def admin_product(request):
    categories = category.objects.all()
    brands = brand.objects.all()
    products = product.objects.all()
    context={'products' : products, 'brands': brands, 'categories': categories }
   
    return render (request, 'admin/admin_product.html' ,  context)




def add_product(request):


    products = product()
    categ = category.objects.all()
    bran = brand.objects.all()  


    if request.method == "POST":


        products.product_name = request.POST.get('product_name')
        products.description = request.POST.get('description')
        products.price = request.POST.get('price')
        products.stock = request.POST.get('stock')
        
        brands = request.POST.get('brand')
        categories= request.POST.get('category')
        print('below  categ')
        print(categories)
        print(brands)
        if products.price == "0" or products.stock == "0" :
            messages.error(request, 'Please Fill with correct Value')
            print('inside  price')
            return redirect('admin_product')
        if len(products.product_name) == 0 or len(categories) == 0 or len(brands) == 0:
            print('inside  categ')
            messages.error(request, 'Fields cannot be blank')
            return redirect('admin_product')

        products.category   = category.objects.get(id = categories)
        products.brand   =  brand.objects.get(id = brands)   
        print('below  brand')
        if len(request.FILES) != 0:
            print('inside images')
            products.images = request.FILES['images']
            products.image2 = request.FILES['image2']
            products.image3 = request.FILES['image3']
            print('inside images')
        
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
    