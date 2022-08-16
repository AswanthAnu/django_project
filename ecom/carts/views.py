from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.



def _cart_id(request):        # creating to session to get cart_id
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, product_id):

    current_user = request.user

    prod = product.objects.get(id = product_id)  #fetching the product
    # if the user is authenticated
    if current_user.is_authenticated:
        
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    varia = Variation.objects.get(product = prod, variation_category__iexact = key, variation_value__iexact = value)
                    product_variation.append(varia)
                except:
                    pass  
        
        
        is_cart_item_exists = CartItem.objects.filter(product = prod, user = current_user).exists()
        if is_cart_item_exists:
        
            cart_item = CartItem.objects.filter(product = prod, user = current_user)
  
            existing_variation_list = []
            id = []
            for item  in cart_item:
                existing_variation = item.variation.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)


            if product_variation in existing_variation_list:
                # increase the cart item quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = prod, id = item_id)
                item.quantity +=  1
                item.save()


            else:
                # create a new cart item
                item = CartItem.objects.create(product = prod, quantity = 1, user = current_user)
                if len(product_variation)> 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                    item.save()

        else:
            
            cart_item = CartItem.objects.create(
                product = prod,
                quantity = 1, 
                user = current_user, 

            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        

        return redirect('cart')

   # if the user is not auth

    else:
        

        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    varia = Variation.objects.get(product = prod, variation_category__iexact = key, variation_value__iexact = value)
                    product_variation.append(varia)
                except:
                    pass
        
    
        try:
        
            cart = Cart.objects.get(cart_id = _cart_id(request) )  #get the cart id by using the session
            
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()    
        
        
        is_cart_item_exists = CartItem.objects.filter(product = prod, cart = cart ).exists()
        if is_cart_item_exists:
        
            cart_item = CartItem.objects.filter(product = prod, cart = cart )
            # existing_variation from database
            # current variation in product_variation
            # item_id from database
            existing_variation_list = []
            id = []
            for item  in cart_item:
                existing_variation = item.variation.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)


            if product_variation in existing_variation_list:
                # increase the cart item quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = prod, id = item_id)
                item.quantity +=  1
                item.save()


            else:
                # create a new cart item
                item = CartItem.objects.create(product = prod, quantity = 1, cart = cart)
                if len(product_variation)> 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                    item.save()

        else:
            
            cart_item = CartItem.objects.create(
                product = prod,
                quantity = 1, 
                cart =  cart,

            )
            if len(product_variation)> 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
                cart_item.save()
        

        return redirect('cart')


def cart(request, total = 0, quantity = 0 , cart_items = None):
    
    try:
        gst = 0
        cart_items = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user , is_active = True)
        else:
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


def remove_cart(request, product_id, cart_item_id):

    
    prod = get_object_or_404(product, id = product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = prod, user = request.user, id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = prod, cart = cart, id = cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except:
        pass

    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
  
    prod = get_object_or_404(product, id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = prod, user = request.user, id = cart_item_id)
    else:    
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = prod, cart = cart, id = cart_item_id)
    cart_item.delete()
    return redirect('cart')




@login_required(login_url = 'login')
def checkout(request, total = 0, quantity = 0 , cart_items = None):


    try:
        total = 0
        gst = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            print(total,'============')
            quantity += cart_item.quantity

        gst = (17 * total)/100
        grand_total = total + gst
        print(grand_total, '==============')
    except ObjectDoesNotExist:
        pass

 
    context = {
        'total' : total,
        'quantity' : quantity, 
        'cart_items' : cart_items,
        'gst' : gst,
        'grand_total' : grand_total,
    }
    print(context)
    return render(request, 'store/checkout.html', context )