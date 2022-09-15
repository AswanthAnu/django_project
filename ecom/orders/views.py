from multiprocessing import context
from time import process_time_ns
from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import product, Coupon
import datetime
import json
from django.views.decorators.cache import cache_control
from openexchangerate import OpenExchangeRates
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
import string
import random
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q,F


# Create your views here.

@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def payments_cod(request):


    if CartItem.quantity == 0:
        return redirect('cart')

    try: 
            if request.method == "POST":
                order = Order.objects.get(user=request.user, is_ordered=False, order_number=request.POST['orderID'])
            # Store transaction details inside Payment model
                
                payment_method =  request.POST['payment_method']
                status = request.POST['status']
                randomLetter = random.choice(string.ascii_letters)
                randomnumber = random.randrange(10000, 99999)
                payment = Payment(
                    user = request.user,
                    payment_method ='cod',
                    amount_paid = order.order_total,
                    status = status,
                    payment_id = randomLetter + str(randomnumber),
                
                )

                payment.save()

                order.payment = payment
                order.is_ordered = True
                order.save()

                # Adding cart item to product table
                cart_items = CartItem.objects.filter(user=request.user)
                

                for item in cart_items:
                    product_pri = 0
                    if item.product.discount > item.product.category.discount:
                        product_pri += (int(item.product.price - (item.product.price * item.product.discount * 0.01 )))
                    else:
                        product_pri += (int(item.product.price - (item.product.price * item.product.category.discount * 0.01 )))
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = payment
                    orderproduct.user_id = request.user.id
                    orderproduct.product_id = item.product_id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = product_pri
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
                message = render_to_string('orders/success_email.html', {
                    'user': request.user,
                    'order': order,
                })
                to_email = request.user.email
                
                send_email = EmailMessage(mail_subject, message, to=[to_email])
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
                product_pri = 0
                if item.product.discount > item.product.category.discount:
                    product_pri += (int(item.product.price - (item.product.price * item.product.discount * 0.01 )))
                else:
                    product_pri += (int(item.product.price - (item.product.price * item.product.category.discount * 0.01 )))
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = product_pri
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

# authorize razorpay client with API Keys.


def payments_razor(request):

    response = request.POST
    order_number = request.POST['order_number']
    params_dict = {
        'razorpay_order_id' : response['razorpay_order_id'],
        'razorpay_payment_id' : response['razorpay_payment_id'],
        'razorpay_signature' : response['razorpay_signature']
    }

    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
    
    status = client.utility.verify_payment_signature(params_dict)
    payment = Payment.objects.get(payment_id = response['razorpay_order_id'])
    payment.status = 'COMPLETED'
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
            product_pri = 0
            if item.product.discount > item.product.category.discount:
                product_pri += (int(item.product.price - (item.product.price * item.product.discount * 0.01 )))
            else:
                product_pri += (int(item.product.price - (item.product.price * item.product.category.discount * 0.01 )))
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = product_pri
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variation.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            prod = product.objects.get(id=item.product_id)
            prod.stock -= item.quantity
            prod.save()

            CartItem.objects.filter(user=request.user).delete()

            try:
                order = Order.objects.get(order_number=order_number, is_ordered=True)
                ordered_products = OrderProduct.objects.filter(order_id=order.id)

                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity
                context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal': subtotal,
                }
            except:
                pass


            return render(request, 'orders/order_success.html', context )



    return render(request, 'orders/payments_razor.html')


@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def place_order(request, totals=0, quantity=0, ):

    if CartItem.quantity == 0:
        return redirect('cart')

    current_user = request.user

    coupon_discount_total=0
    cart_ii=[]
    cart_item_id = 0
    
    # if the cart count is less than 0 return back to shop
    cart_items  = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    cart_ii = CartItem.objects.values().filter(user=request.user).order_by('id')[:1]
    coupon_discount_total=0
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        if cart_item.product.discount > cart_item.product.category.discount:
            totals += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.discount * 0.01 ))* cart_item.quantity)
        else:
            totals += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.category.discount * 0.01 ))* cart_item.quantity)
        
        quantity += cart_item.quantity
        for i in cart_ii:
                cart_item_id = (i['id'])

        cart_i = CartItem.objects.get(id =cart_item_id)
        coupon_code = cart_i.coupon
        try:
            coupon_code_ = Coupon.objects.get(coupon_code = coupon_code)

            coupon_discount = coupon_code_.disccount

            coupon_discount_total = int((totals * (coupon_discount/100)))
            if coupon_discount_total > coupon_code_.maximum_amount:
                coupon_discount_total = coupon_code_.maximum_amount
            elif coupon_discount_total < coupon_code_.minimum_amount:
                coupon_discount_total = coupon_code_.minimum_amount

            total = totals - coupon_discount_total
        except:
            total = totals
    tax = int((12 * total)/100)
    grand_total = int(total + tax)
    
    
    if request.method == 'POST':
        
        
        
            # Store all the billing information inside Order table
            data = Order()
            pay_method = Payment()
            try:
                coupon = Coupon.objects.get(coupon_code = coupon_code)
                data.coupon = coupon
            except:
                pass
            
            data.user = current_user
            data.first_name = request.POST['first_name']
            data.last_name = request.POST['last_name']
            data.phone = request.POST['phone_number']
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
            request.session['order_number'] = order_number

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
                'totals': totals,
                'total': total,
                'tax': tax,
                'coupon_code' : coupon_code,
                'coupon_discount_total': coupon_discount_total,
                'grand_total': grand_total,
                'grand_dollar':grand_dollar

            }
            if "cod_method" == payment_method:


                #return render(request, 'orders/payments_cod.html', context)
                return render(request, 'orders/payments_cod.html', context)

            elif "razor_method" == payment_method:


                currency = 'INR'
                amount = int(grand_total) * 100 # Rs. 200

                razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                # Create a Razorpay Order
                razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                                currency=currency,
                                                                payment_capture='0'))
                
            
                # order id of newly created order.
                razorpay_order_id = razorpay_order['id']
                razorpay_order_status = razorpay_order['status']

                if razorpay_order_status == 'created':
                    user = current_user
                    payment = Payment(
                        user_id = user.id,
                        payment_id = razorpay_order_id,
                        amount_paid = amount/100,
                        payment_method = 'Rayzor Pay'


                    )
                    payment.save()


                callback_url = 'paymenthandler/'
            
                # we need to pass these details to frontend.
                context = {
                'order_number' : order_number,
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'totals': totals,
                'tax': tax,
                'coupon_code' : coupon_code,
                'coupon_discount_total': coupon_discount_total,
                'grand_total': grand_total,
                'grand_dollar':grand_dollar,
                'razorpay_order_id' : razorpay_order_id,
                'razorpay_merchant_key' : settings.RAZOR_KEY_ID,
                'razorpay_amount' : amount,
                'currency' : currency,
                'callback_url' : callback_url
                }



               
                
                return render(request, 'orders/payments_razor.html', context )


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
                discount_total = ((subtotal + order.tax)-order.order_total )
                context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal': subtotal,
                    'discount_total': discount_total,
                }
            
                return render(request, 'orders/order_success.html', context )
            
            except (Payment.DoesNotExist, Order.DoesNotExist):
            
                return redirect('home')

    except:
        return redirect('cart')