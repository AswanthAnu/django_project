from .models import Cart, CartItem
from .views import _cart_id
from django.core.exceptions import ObjectDoesNotExist

def counter(request):

    cart_count = 0
    cart_total = 0

    if 'admin' in request.path:
        return{}

    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                cart_total += (cart_item.product.price * cart_item.quantity)
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count = cart_count, cart_total = cart_total)
        
def counters(request):

    cart_quantity = 0
    cart_total = 0

    if 'admin' in request.path:
        return{}


    else:
        
        try:
            
            cart =  Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart , is_active = True)
            for cart_item in cart_items:
                cart_total += (cart_item.product.price * cart_item.quantity)
                print(cart_total)
                cart_quantity += cart_item.quantity
                print(cart_quantity, '--------')
        except ObjectDoesNotExist:
                    
            cart_quantity = 0
            cart_total = 0

    return dict(cart_quantity = cart_quantity, cart_total = cart_total)