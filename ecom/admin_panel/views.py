from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect


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