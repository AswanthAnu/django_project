
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .form import RegistrationForm
from .models import Account, profile
from django.http import HttpResponse,JsonResponse
from orders.models import Order  
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.conf import settings



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

            if len(phone_number) == 10:

                user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
                user.phone_number = phone_number

                print(phone_number)
                
                user.is_staff = False
                user.is_admin = False
                user.save()
                username = user.email
                print(username)

                phone_num = "+91" + phone_number

                account_sid = settings.ACCOUNT_SID
                auth_token = settings.TOKEN_SID


                client=Client(account_sid,auth_token)
                verification = client.verify \
                    .services(settings.SERVICES) \
                    .verifications \
                    .create(to=phone_num,channel='sms')


                
                
                messages.success(request,'OTP has been sent to ' + str(phone_num))
                return render(request, 'accounts/otp_registration.html', {'phone_number': phone_number,  'username' : username})
                
            
            else: 
                messages.error(request, '10 digits number required')
               

            

        else:
            
            messages.error(request, "")
                
            
            
        
    else:
        form = RegistrationForm()

    context = {
            'form' : form,
            }
    return render(request, 'accounts/register.html', context)

def otp_registration(request, phone_number):

    #username = Account.request.get('email')
    #print(username,"username" )
    


    if request.method == "POST":
        phone_num = "+91"+ str(phone_number)
        otp_input = request.POST['otp']


        if len(otp_input)  >0:


                account_sid= settings.ACCOUNT_SID
                auth_token= settings.TOKEN_SID
                
                client = Client(account_sid, auth_token)

                otp_check = client.verify \
                                    .services(settings.SERVICES) \
                                    .verification_checks \
                                    .create(to= phone_num, code= otp_input)


                if otp_check.status == "approved":
                    user = Account.objects.get(phone_number =phone_number )
                    print(user)
                    user.is_active = True   
                    user.Phone_number = phone_number        
                    user.save()          
                    auth.login(request,user)
                    return redirect('home')
                else:
                    messages.success(request, "Invalid OTP")
                    print("inside otp")
                    return redirect("otp_registration", phone_number)
        else:
            messages.success(request, "Invalid OTP")
            print("outside otp")
            return redirect("otp_registration", phone_number)

    else:
        print("out")
        return render(request, 'accounts/otp_registration.html', {'phone_number': phone_number} )





   




def login(request):


        if 'email' in request.session:

            return redirect ('home')

    
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            print(email)
            print(password)
            user = authenticate(email=email, password=password)
            if user is not None and user.is_admin == False:

                try:
                    cart = Cart.objects.get(cart_id = _cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart = cart ).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart = cart)
                    # getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation  = item.variation.all()
                        product_variation.append(list(variation))

                    #get cart item from the user to access his product variations
                    cart_item = CartItem.objects.filter( user = user)
                   
                    existing_variation_list = []
                    id = []
                    for item  in cart_item:
                        existing_variation = item.variation.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # existing_variation_list = [4, 5, 3, 5]

                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item.id)
                            item.quantity +=  1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

                #     for item in cart_item:
                #         item.user = user
                #         item.save()
                except:
                    pass
                request.session['email'] = email
                auth.login(request, user)
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    # next=/cart/checkout/
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)  
                except:
                    pass
                    
                return redirect('home')

            else:
                messages.info(request,"Invalid credantials")
                return redirect('login')
                




        return render(request, 'accounts/login.html')

def otp_view(request):
       

        if request.method == 'POST':
            phone_number = request.POST.get('phone_number')
            print(phone_number,'-')
            if Account.objects.filter(phone_number = phone_number).exists():
                users = Account.objects.get(phone_number = phone_number)
                print(users)
                phone_num = "+91"+ phone_number
                account_sid= settings.ACCOUNT_SID
                auth_token= settings.TOKEN_SID
                
               
                request.session['id'] = users.id
                request.session['email'] = users.email

                client=Client(account_sid,auth_token)
                verification = client.verify \
                    .services(settings.SERVICES) \
                    .verifications \
                    .create(to=phone_num,channel='sms')
                
                messages.success(request,'OTP has been sent to ' + str(phone_num))
                return render (request, 'accounts/otp_login.html',{'phone_number':phone_number,'user':users})

            elif  len(phone_number) < 10 or len(phone_number) > 10 :
                 
                messages.error(request, '10 digits number required')
                return redirect('otp_view')

            else:
                messages.error(request, 'Invalid Phone Number')
                return render (request, 'accounts/otp_view.html')




        
        return render(request, 'accounts/otp_view.html ')
       

def otp_login(request, phone_number):
    
    if request.method == 'POST':
        if Account.objects.filter(phone_number= phone_number).exists():
            user = Account.objects.get(phone_number= phone_number)


            phone_num = "+91"+ str(phone_number)
            otp_input = request.POST['otp']

            if len(otp_input)  >0:


                account_sid= settings.ACCOUNT_SID
                auth_token= settings.TOKEN_SID
                
                client = Client(account_sid, auth_token)

                otp_check = client.verify \
                                    .services(settings.SERVICES) \
                                    .verification_checks \
                                    .create(to= phone_num, code= otp_input)


                if otp_check.status == "approved":
                    auth.login(request, user)
                    return redirect('home')

                else:
                    messages.error(request, "Invalid OTP")
                    return redirect("otp_login", phone_number)
            else:
                messages.error(request, "Invalid OTP")
                return redirect("otp_login", phone_number)

        else:
            messages.error(request, "Invalid Phone Number")
            return redirect('otp_login', phone_number)

    print(phone_number)
    return render(request, 'accounts/otp_login.html',{'phone_number':phone_number})



def logout(request):

    
    request.session.flush() 

    return redirect('home')
@login_required(login_url = 'login')
def dashboard(request):

    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    orders_count = orders.count()

    

    context = {
        
       
        'orders_count' : orders_count,
    }

    return render(request, 'accounts/dashboard.html', context )


def my_orders(request):

    orders = Order.objects.filter(user = request.user, is_ordered= True).order_by('-created_at')
    context = {
        'orders' : orders,
    }

    return render(request, 'accounts/my_orders.html', context)


def edit_profile(request):
    return render(request, 'accounts/my_orders.html')


def change_password(request):
    return render(request, 'accounts/my_orders.html')