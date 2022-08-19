
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
from orders.models import Order  
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests
from django.contrib.auth.decorators import login_required



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

            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password, phone_umber = phone_number)
            
            user.is_active = True
            user.is_staff = False
            user.is_admin = False

            otp=random.randint(1000,9999)

            prof= profile.objects.create(user=user,phone_number=phone_number,otp=otp)

            message_handler = MessageHandler(f'+91'+phone_number ,prof.otp).send_otp_on_phone
            message_handler()
            return redirect('otp_registration')

        
    else:
        form = RegistrationForm()

    context = {
            'form' : form,
            }
    return render(request, 'accounts/register.html', context)

def otp_registration(request):

    pass




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
                
               
                request.session['id'] = users.id
                request.session['email'] = users.email

                otp = random.randint(1000, 9999)
                print(otp)
                prof = profile.objects.get(user = users.id )
                print(prof)
                prof.otp = otp
                prof.save()
                message_handler = MessageHandler(f'+91'+phone_number ,prof.otp).send_otp_on_phone
                message_handler()
                print('------',prof.otp, '-------')
                return redirect( 'otp_login')
            print('183')
            messages.success(request, 'Invalid Phone Number')
            return redirect('otp_view')

        
        return render(request, 'accounts/otp_view.html ')
       

def otp_login(request):
    
    id = request.session['id']
    users = Account.objects.get(id=id)
    if request.method == 'POST':
        otp = request.POST.get('otp')
        
        #email = request.session['email']
        print(otp, '-----')
        prof = profile.objects.get( id = id) 
        print(prof, '--prof-otp-')
        if otp == prof.otp:
            auth.login(request, users)
            print("232")
            return redirect('home')
        print("234")
        messages.success(request, 'Wrong OTP')
        return redirect('login')
    return render(request, 'accounts/otp_login.html')



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