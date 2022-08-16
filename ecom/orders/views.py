from django.shortcuts import render, redirect
from carts.models import CartItem, Cart
from .forms import OrderForm
from .models import Order
import datetime

# Create your views here.
def place_order(request, total=0, quantity=0, ):

    current_user = request.user
    
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

        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['user_address1']
            data.address_line_2 = form.cleaned_data['user_address2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number 
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #2021-03-05
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            return redirect('checkout')
    else:
        return redirect('checkout')


