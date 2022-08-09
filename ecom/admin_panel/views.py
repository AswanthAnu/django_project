from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from accounts.models import Account
from category.models import category
from .decorators import log


# Create your views here.

def admin_login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email)
        print(password)

        user = authenticate(email=email, password=password,)
        
        if user.is_admin == True:
            print(user.is_admin)
            auth.login(request, user)
            print('dash')
            return redirect('admin_dashboard')
           
        else:
            print('else')
            messages.error(request, 'Invalid admin credentials')
            return redirect('admin_login')

    return render(request, 'admin/admin_login.html')


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


def admin_product(request):
    return render (request, 'admin/admin_product.html')


    
def admin_category(request):
    categories = category.objects.all()
    context={'categories' : categories }
   
    return render (request, 'admin/admin_category.html' , context)


def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')

        categ = category(category_name = category_name, description = description)
        categ.save()
        return redirect('admin_category')
    return render(request,'admin/admin_category.html')