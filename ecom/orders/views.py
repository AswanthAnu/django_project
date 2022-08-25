from multiprocessing import context
from time import process_time_ns
from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import product
import datetime
import json
from django.views.decorators.cache import cache_control
from openexchangerate import OpenExchangeRates
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
import string
import random



# Create your views here.

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def payments_cod(request):


    if CartItem.quantity == 0:
        return redirect('cart')

    try: 
        
    
            print('entering into payments_cod')
            if request.method == "POST":
                order = Order.objects.get(user=request.user, is_ordered=False, order_number=request.POST['orderID'])
            # Store transaction details inside Payment model
                
                payment_method =  request.POST['payment_method']
                status = request.POST['status']
                randomLetter = random.choice(string.ascii_letters)
                print(randomLetter)
                randomnumber = random.randrange(10000, 99999)
                print(randomnumber)
                payment = Payment(
                    user = request.user,
                    payment_method ='cod',
                    amount_paid = order.order_total,
                    status = status,
                    payment_id = randomLetter + str(randomnumber),
                
                )

                payment.save()
                print(payment, '-----------')

                order.payment = payment
                order.is_ordered = True
                order.save()

                # Adding cart item to product table
                cart_items = CartItem.objects.filter(user=request.user)

                for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = payment
                    orderproduct.user_id = request.user.id
                    orderproduct.product_id = item.product_id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.product.price
                    orderproduct.ordered = True
                    orderproduct.save()


                    cart_item = CartItem.objects.get(id=item.id)
                    product_variation = cart_item.variation.all()
                    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variations.set(product_variation)
                    orderproduct.save()
                    print(orderproduct, '-----------67')

                # Reduce the quantity of the stock
                    prod = product.objects.get(id=item.product_id)
                    prod.stock -= item.quantity
                    prod.save()
                
                # clear the cart item
                CartItem.objects.filter(user=request.user).delete()
                
                # send email
                mail_subject = 'Your order placed successfully...!'
                print(mail_subject)
                message = render_to_string('orders/success_email.html', {
                    'user': request.user,
                    'order': order,
                })
                to_email = request.user.email
                
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                #send_email.send()

                


                # data = {
                #     'success' : True,
                #     'order_number': order.order_number,
                #     'transID': payment.payment_id,
                #     }
                print("enter into data")
                return JsonResponse({
                    'success' : True,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    })

    except:
        return redirect('cart')


@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def payments(request):

    if CartItem.quantity == 0:
        return redirect('cart')

    try:
        if cart_value == 10:

            body = json.loads(request.body)
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

            # Store transaction details inside Payment model
            payment = Payment(
                user = request.user,
                payment_id = body['transID'],
                payment_method = body['payment_method'],
                amount_paid = order.order_total,
                status = body['status'],
            )
            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            # Adding cart item to product table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variation.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

            # Reduce the quantity of the stock
                prod = product.objects.get(id=item.product_id)
                prod.stock -= item.quantity
                prod.save()
            
            # clear the cart item
            CartItem.objects.filter(user=request.user).delete()
            
            # send email
            mail_subject = 'Your order placed successfully...!'
            print(mail_subject)
            message = render_to_string('orders/success_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            #send_email.send()

            


            data = {
                'order_number': order.order_number,
                'transID': payment.payment_id,
            }
            return JsonResponse(data)
    except:
        return redirect('cart')

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def place_order(request, total=0, quantity=0, ):

    if CartItem.quantity == 0:
        print(CartItem.quantity)
        print("----quantity")
        return redirect('cart')

    current_user = request.user
    print('entering into place_order')

    
    
    # if the cart count is less than 0 return back to shop
    cart_items  = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
     
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    
    
    if request.method == 'POST':
        
        
        
            # Store all the billing information inside Order table
            print('entering if')
            data = Order()
            pay_method = Payment()
            
            data.user = current_user
            data.first_name = request.POST['first_name']
            data.last_name = request.POST['last_name']
            data.phone = request.POST['phone']
            data.email = request.POST['email']
            data.address_line_1 = request.POST['address_line_1']
            data.address_line_2 = request.POST['address_line_2']
            data.country = request.POST['country']
            data.state = request.POST['state']
            data.city = request.POST['city']
            data.order_note = request.POST['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            payment_method = request.POST['payment_method']
            
            # generate order number 
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #2021-03-05
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # converting indian rupee intto dollar
            
            client = OpenExchangeRates(api_key=settings.API_KEY)
            openx = list(client.latest())
            openx = openx[0]
            openxrupee = openx['INR']
            grand_dollar = round(grand_total / openxrupee,2)


            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'grand_dollar':grand_dollar

            }
            if "cod_method" == payment_method:


                #return render(request, 'orders/payments_cod.html', context)
                return render(request, 'orders/payments_cod.html', context)

            else:
                return render(request, 'orders/payments.html', context)
          
    else:
        return redirect('checkout')

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def order_success(request):


    if CartItem.quantity == 0:
        return redirect('cart')

    try :
        
    
            transID = request.GET.get('payment_id')
            order_number = request.GET.get('order_number')

            try:
                order = Order.objects.get(order_number=order_number, is_ordered=True)
                ordered_products = OrderProduct.objects.filter(order_id=order.id)

                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity

                payment = Payment.objects.get(payment_id=transID)
                cart_value = 9
                context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal': subtotal,
                }
            
                return render(request, 'orders/order_success.html', context )
            
            except (Payment.DoesNotExist, Order.DoesNotExist):
            
                return redirect('home')

    except:
        return redirect('cart')