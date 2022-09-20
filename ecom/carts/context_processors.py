from .models import Cart, CartItem
from .views import _cart_id
from django.core.exceptions import ObjectDoesNotExist

def counter(request):

    cart_count = 0
    cart_total = 0
    cart_grand_total = 0
    cart_gst = 0


    if 'admin' in request.path:
        return{}

    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user = request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart = cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                if cart_item.product.discount > cart_item.product.category.discount:
                    cart_total += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.discount * 0.01 ))* cart_item.quantity)
                else:
                    cart_total += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.category.discount * 0.01 ))* cart_item.quantity)
            cart_gst = int((12 * cart_total)/100)
            cart_grand_total = int(cart_total + cart_gst)
        except Cart.DoesNotExist:
            cart_count = 0
        
    return dict(cart_count = cart_count, cart_total = cart_total, cart_grand_total = cart_grand_total, cart_gst = cart_gst)
        
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