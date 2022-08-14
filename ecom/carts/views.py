from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import product
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.



def _cart_id(request):        # creating to session to get cart_id
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, product_id):
    
    prod = product.objects.get(id = product_id)  #fetching the product
    
    print(type(prod))
   
    try:
        print("---------------tryhere------------------")
        cart = Cart.objects.get(cart_id = _cart_id(request) )  #get the cart id by using the session
        
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        
        print(';--987$%$%#',cart)
    cart.save()

    try:
       
        cart_item = CartItem.objects.get(product = prod, cart = cart )
        print("--------------here-------------")
        cart_item.quantity += 1
        
        cart_item.save()

    except CartItem.DoesNotExist:
        print("--------------here---------here-------------")
        print(prod.id,'---------' ,cart)
        cart_item = CartItem.objects.create(
            product = prod,
            quantity = 1, 
            cart =  cart,

        )
        cart_item.save()
    

    return redirect('cart')


def cart(request, total = 0, quantity = 0 , cart_items = None):
    
    try:
        gst = 0
        cart_items = 0
        grand_total = 0
        cart =  Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart , is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            print(total)
            quantity += cart_item.quantity

        gst = (17 * total)/100
        grand_total = total + gst
    except ObjectDoesNotExist:
        pass

 
    context = {
        'total' : total,
        'quantity' : quantity, 
        'cart_items' : cart_items,
        'gst' : gst,
        'grand_total' : grand_total
    }

    return render(request, 'store/cart.html', context)


def remove_cart(request, product_id):

    cart = Cart.objects.get(cart_id = _cart_id(request))
    prod = get_object_or_404(product, id = product_id)
    cart_item = CartItem.objects.get(product = prod, cart = cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        context = {
            'quantity' : cart_item.quantity
        }
        
    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    prod = get_object_or_404(product, id = product_id)
    cart_item = CartItem.objects.get(product = prod, cart = cart)
    cart_item.delete()
    return redirect('cart')




# @login_required(login_url = 'login')
def checkout(request, total = 0, quantity = 0 , cart_items = None):


    try:
        total = 0
        gst = 0
        cart_items = 0
        grand_total = 0
        cart =  Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart , is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            print(total)
            quantity += cart_item.quantity

        gst = (17 * total)/100
        grand_total = total + gst
    except ObjectDoesNotExist:
        pass

 
    context = {
        'total' : total,
        'quantity' : quantity, 
        'cart_items' : cart_items,
        'gst' : gst,
        'grand_total' : grand_total
    }

    return render(request, 'store/checkout.html', context )