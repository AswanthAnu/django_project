
import email
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

            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password,)
            user.phone_number = phone_number
            user.is_active = True
            user.is_staff = False
            user.is_admin = False

            otp=random.randint(1000,9999)

            prof= profile.objects.create(user=user,phone_number=phone_number,otp=f'{otp}')

            messagehandler=MessageHandler(f'+91'+phone_number,otp).send_otp_via_message()

            red = redirect()

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

def login(request):


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
            print(phone_number,'-')
            if Account.objects.filter(phone_number = phone_number).exists():
                
                
               
            #     prof[0].otp = random.randint(1000, 9999)
            #     print('account here')
            #     #print(profile.otp)
            #     prof.save()
                
               
                id = request.session['email'] = email
                otp = random.randint(1000, 9999)
                print(otp)
                profi = Account(otp = otp)
                
                profi.save
                #message_handler = MessageHandler(f'+91'+phone_number ,prof.otp).send_otp_on_phone
                #message_handler()
                print('------',profi.otp, '-------')
                return redirect( 'otp_login')
                #     return JsonResponse(
                #             {
                #             'success': object.uid }, safe=False,

                        
                        
                #         )

                # else:
                #     # return render('login')
                #     print("Failed")
                #     return JsonResponse(
                #         {
                #         'success':False},
                #          safe=False
                        
                #         )

        
        return render(request, 'accounts/otp_view.html ')
       

def otp_login(request, email=None):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        
        prof = Account.objects.filter(email = email, otp = otp)
        if otp == prof.otp:
            login(request, Account.user)
            return redirect('home')
        
        return redirect('login')
    return render(request, 'accounts/otp_login.html')



def logout(request):
    return render(request, 'accounts/login.html')

