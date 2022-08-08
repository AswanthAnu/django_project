
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .form import RegistrationForm
from .models import Account
from django.http import HttpResponse,JsonResponse






# Create your views here.

def register(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            username = email.split('@')[0]

            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password,)
            user.phone_number = phone_number
          
            user.is_active = True
            user.is_staff = False
            user.is_admin = False
            user.save()
            messages.success(request, 'Your account registered successfully')
            return redirect('register')


    else:
        form = RegistrationForm()

    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email)
        print(password)

        # user = User.objects.get(email=email, password=password)
        # if check_password(password, user.password):
        #     if user.is_active:
        #         login(request, user)
        #         return redirect('home')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('register')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

        if user is not None:
             return JsonResponse(
                    {
                    'success':True},

                    safe=False
                
                )
        else :
            print("Failed")
            return JsonResponse(
                {
                'success':False},

                 safe=False
                
                )




    return render(request, 'accounts/login.html')

def logout(request):
    return render(request, 'accounts/login.html')
