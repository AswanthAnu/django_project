from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .form import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile, Address
from django.http import JsonResponse
from django.urls import reverse
from orders.models import Order, OrderProduct, ReturnProduct, Payment
from carts.views import _cart_id
from carts.models import Cart, CartItem
from store.models import product
import requests
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlwt




# Create your views here.

def register(request):

    if 'email' in request.session:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            

            username = email.split('@')[0]

            if len(first_name.strip()) == 0:

                return JsonResponse({'first_name' : True}, safe= False)

            elif len(last_name.strip()) == 0:
                
                return JsonResponse({'first_name' : False}, safe= False)

            elif len(phone_number.strip()) == 0:

                return JsonResponse({'phone_number' : True}, safe= False)

            
            if len(phone_number) == 10:

                user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
                user.phone_number = phone_number   
                user.is_staff = False
                user.is_admin = False
                user.save()
                username = user.email
                profile = UserProfile()
                profile.user_id = user.id
                profile.profile_picture = 'default/default-user.png'
                profile.save()

                phone_num = "+91" + phone_number

                account_sid = settings.ACCOUNT_SID
                auth_token = settings.TOKEN_SID


                client=Client(account_sid,auth_token)
                verification = client.verify \
                    .services(settings.SERVICES) \
                    .verifications \
                    .create(to=phone_num,channel='sms')


                
                
                messages.success(request,'OTP has been sent to ' + str(phone_num))
                return JsonResponse({'success': True, 'phone_number': phone_number}, safe=True)
                return render(request, 'accounts/otp_registration.html', {'phone_number': phone_number,  'username' : username})
                
            
            else: 
                
                return JsonResponse({'success': False}, safe=True)
               

            

        else:
            
            
            return JsonResponse({'phone_number' : False}, safe= False)
                
            
            
        
    else:
        form = RegistrationForm()

    context = {
            'form' : form,
            }
    return render(request, 'accounts/register.html', context)
def otp_registration(request):
     return render(request, 'accounts/otp_registration.html')

def otp_registration(request, phone_number):
    if request.method == "POST":
        phone_num = "+91"+ str(phone_number)
        otp_input = request.POST['otp']

        try:
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
                        user.is_active = True   
                        user.Phone_number = phone_number        
                        user.save()          
                        auth.login(request,user)
                        return JsonResponse({"success" :True }, safe= False)
                    else:
                        return JsonResponse({"success" :False }, safe= False)
            else:
                return JsonResponse({"phone" : True }, safe= False)
        except:
            return JsonResponse({"phone" : False }, safe= False)

    else:
        return render(request, 'accounts/otp_registration.html', {'phone_number': phone_number} )


def login(request):


        if 'email' in request.session:

            return redirect ('home')
        
    
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            if len(email.strip()) == 0: 
                length = len(email.strip())
                return JsonResponse({"email_length" : True }, safe= False)
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
                except:
                    pass
                request.session['email'] = user.email
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
                    
                return JsonResponse({"success":True}, safe= False)

            else:
                return JsonResponse({"success":False}, safe= False)

        return render(request, 'accounts/login.html')

def otp_view(request):
       

        if request.method == 'POST':
            phone_number = request.POST.get('phone_number')
         
            if Account.objects.filter(phone_number = phone_number).exists():
                users = Account.objects.get(phone_number = phone_number)
                phone_num = "+91"+ phone_number
                account_sid= settings.ACCOUNT_SID
                auth_token= settings.TOKEN_SID
               
                request.session['email'] = users.email

                client=Client(account_sid,auth_token)
                verification = client.verify \
                    .services(settings.SERVICES) \
                    .verifications \
                    .create(to=phone_num,channel='sms')
                
                #messages.success(request,'OTP has been sent to ' + str(phone_num))
               
                return JsonResponse({'phone': True,  'phone_number':phone_number}, safe=False)

            elif  len(phone_number) < 10 or len(phone_number) > 10 :
                 
                #messages.error(request, '10 digits number required')
                return JsonResponse({'success': True}, safe=False)

            else:
                #messages.error(request, 'Invalid Phone Number')
                return JsonResponse({'success': False}, safe=False)




        
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
                    return JsonResponse({"phone" :True }, safe= False)

                else:
                    return JsonResponse({"phone" :False }, safe= False)
            else:
                return JsonResponse({"success" : True }, safe= False)

        else:
            return JsonResponse({"success" : False }, safe= False)

    return render(request, 'accounts/otp_login.html',{'phone_number':phone_number})



def logout(request):

    
    request.session.flush() 

    return redirect('home')

def dashboard(request):

    try:
        orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
        orders_count = orders.count()
        userprofile = get_object_or_404(UserProfile, user=request.user)
    except:
        orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id)
        userprofile = get_object_or_404(Account, email=request.user.email)
        return render(request, 'accounts/dashboard.html' )
        
        

    context = {
        
       
        'orders_count' : orders_count,
        'userprofile'  : userprofile,
    }

    return render(request, 'accounts/dashboard.html', context )


def my_orders(request):




    orderproducts = OrderProduct.objects.filter(user = request.user).order_by('-created_at')
    paginator = Paginator(orderproducts, 10)
    page = request.GET.get('page')
    paged_orderproducts = paginator.get_page(page)

    context = {
        'orderproducts' : paged_orderproducts,
    }

    return render(request, 'accounts/my_orders.html', context)

  
def cancel_order(request, order_no, order_prdt, order_qnty ):
    order_cancel = Order.objects.get(order_number=order_no)
    
    order_product = product.objects.get(product_name = order_prdt)
    
    order_cancel.status = 'Cancelled'
    
    order_product.stock += int(order_qnty)
    
    
    order_cancel.save()
    order_product.save()

    return JsonResponse({'success': True},safe= False)

def return_product(request):
    if request.method == "POST":
        orderprdct_id = request.POST['orderprdct_id']
        reason = request.POST['reason']
        order_pd = OrderProduct.objects.get(id = orderprdct_id)
        order_pd.order.status = "Returned"
        order_pd.order.save()
        return_prdt = ReturnProduct(
            return_product = order_pd,
            reason = reason,
            returnstatus = 'Waiting'
        )

        return_prdt.save()

        return JsonResponse(
            {'success' : True}, safe= False
        )
        


def address(request):


    user = request.user
    addresses = []
    us = user.id
    try:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            phone_number = request.POST['phone_number']
            address_line_1 = request.POST['address_line_1']
            address_line_2 = request.POST['address_line_2']
            city = request.POST['city']
            state = request.POST['state']
            country = request.POST['country']

            address = Address(user_id = us ,first_name = first_name, last_name = last_name, email = email, phone_number = phone_number, address_line_1 = address_line_1, address_line_2 = address_line_2, city = city, state = state, country = country )

            address.save()
            
            addresses = Address.objects.get(user_id = us)
            messages.success(request, 'New Address added to the list...')
            return redirect('address')
    except:
        return redirect('address')

    addresses = Address.objects.filter(user_id = us)
    context = {
        'addresses' : addresses,
    }
    return render(request, 'accounts/address.html', context)

def edit_profile(request):
    try:
        userprofile = get_object_or_404(UserProfile, user=request.user)
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile )

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('edit_profile')

        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=userprofile)
    except:
        user_form = UserForm()
        profile_form = UserProfileForm()
        context = {
        'user_form' : user_form, 
        'profile_form' : profile_form,
    }

        return render(request, 'accounts/edit_profile.html', context)
    context = {
        'user_form' : user_form, 
        'profile_form' : profile_form,
        'userprofile'  : userprofile,
    }

    return render(request, 'accounts/edit_profile.html', context)


def change_password(request):

    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            success  = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Your password is in correct.')
                return redirect('change_password')

        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html' )

def invoice_download(request):
    if request.method == "POST":
        order_number = request.POST['order_number']
        transID = request.POST['payment_id']

        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            payment = Payment.objects.get(payment_id=transID)
            discount_total = ((subtotal + order.tax)-order.order_total )
            template_path = 'export/invoice_pdf.html' 
            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
                'transID': payment.payment_id,
                'payment': payment,
                'subtotal': subtotal,
                'discount_total': discount_total,
            }
        
            response = HttpResponse(content_type ='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="invoice_report.pdf"'
        
            template = get_template(template_path)

            html = template.render(context)

            # create a pdf
            pisa_status = pisa.CreatePDF(
            html, dest=response)
            # if error then show some funy view
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response
        
        except (Payment.DoesNotExist, Order.DoesNotExist):
        
            return redirect('home')
