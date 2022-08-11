
from cProfile import Profile
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .form import RegistrationForm
from .mixins import MessageHandler
from .models import Account, profile
from django.http import HttpResponse,JsonResponse
import random   




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

            # # user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password,)
            # # user.phone_number = phone_number
            # first_name = request.POST['first_name']
            # last_name = request.POST['last_name']
            # email = request.POST['email']
            # phone_number = request.POST['phone_number']
            # password = request.POST['password']
            # # username = request.POST['username']
            # username = email.split('@')[0]

            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password,)
            user.phone_number = phone_number
          
            user.is_active = True
            user.is_staff = False
            user.is_admin = False
            user.save()
            print("save")
            messages.success(request, 'Your account registered successfully')
            return redirect('register')

        
    else:
        form = RegistrationForm()

    context = {
            'form' : form,
            }
    return render(request, 'accounts/register.html', context)

def login(request,):


        if 'email' in request.session:

            return redirect ('home')

    
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
            
            # if user is not None:
            #     auth.login(request, user)
            #     return redirect('register')
            # else:
            #     messages.error(request, 'Invalid login credentials')
            #     return redirect('login')

            if user is not None:
                request.session['email'] = email
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

def otp_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if Account.objects.filter(phone_number = phone_number):

            profile = Account.objects.get(phone_number, id)
            Profile.otp = random.randint(1000, 9999)
            Profile.save()
            message_handler = MessageHandler(f'+91'+phone_number ,Profile[0].otp).send_otp_on_phone
            message_handler()
            return JsonResponse(
                    {
                    'success':True},  id, safe=False,

                  
                
                )

        else:
            # return render('login')
            print("Failed")
            return JsonResponse(
                {
                'success':False},
                 safe=False
                
                )

        
    # return redirect(request, 'otp_login/{profiles[0].uid}')
       

def otp_login(request, id):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Account.objects.get(uid = id)
        if otp == profile.otp:
            login(request, profile.user)
            return redirect('home')
        
        return redirect('otp_login')
    return render(request, 'login.html')



def logout(request):
    return render(request, 'accounts/login.html')

