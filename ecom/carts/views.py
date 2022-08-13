from django.shortcuts import render, redirect
from .models import Cart, CartItem
from store.models import product
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

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


def cart(request, total = 0, quantity = 0 , cart_item = None):
    
    try:
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
