from ast import Delete
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from accounts.models import Account, Address
from store.models import product, Variation, Coupon
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Order
from django.db.models import Q



def _cart_id(request):        # creating to session to get cart_id
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, product_id):

    current_user = request.user
    print('---')

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
     

                    
def update_cart(request,product_id ):

    current_user = request.user
    print('---')
    print("add_cart_from_cart")
    # product = Product.objects.get(id=product_id)
    # print(type(product))
  
     
    #fetching the product
    # if the user is authenticated
    if current_user.is_authenticated:
        
        product_variation = []

      

        cart_id = product_id
        print(cart_id)


        cart_ite = CartItem.objects.get(id = cart_id)
        cart_ite.quantity += 1
        cart_ite.save()

        cart_q = cart_ite.quantity
        print(cart_q, "cart quantity")
        

        return HttpResponse(cart_q)
     

   # if the user is not auth

    else:

        if request.method == 'POST':

            cart_id = request.POST['cart_id']
            print(cart_id)


            cart_ite = CartItem.objects.filter(id = cart_id)
            cart_ite.quantity += 1
            cart_ite.save()

            cart_q = cart_ite.quantity

        return HttpResponse(cart_q)
     






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
            if cart_item.product.discount > cart_item.product.category.discount:
                total += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.discount * 0.01 ))* cart_item.quantity)
            else:
                total += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.category.discount * 0.01 ))* cart_item.quantity)

            quantity += cart_item.quantity

        gst = int((12 * total)/100)
        grand_total = int(total + gst)
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
            cart_q =  cart_item.quantity
            print(cart_q)
        else:
            cart_item.delete()

    except:
        pass

    #return redirect('cart')
    return HttpResponse(cart_q)


def remove_cart_item(request, product_id, cart_item_id):
  
    prod = get_object_or_404(product, id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = prod, user = request.user, id = cart_item_id)
    else:    
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = prod, cart = cart, id = cart_item_id)
    cart_item.delete()
    return JsonResponse({"success" : True}, safe= False)




@login_required(login_url = 'login')
def checkout(request, totals = 0, quantity = 0 , cart_items = None):


    # try:
        total = 0
        gst = 0
        grand_total = 0
        coupon_discount_total=0
        coupon_code = 0
        cart_ii=[]
        cart_item_id = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            cart_ii = CartItem.objects.values().filter(user=request.user).order_by('id')[:1]
            addresses = Address.objects.filter(user = request.user)
    
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            cart_ii = CartItem.objects.values().filter(cart=cart, is_active=True).order_by('id')[:1]
        for cart_item in cart_items:
            if cart_item.product.discount > cart_item.product.category.discount:
                totals += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.discount * 0.01 ))* cart_item.quantity)
            else:
                totals += (int(cart_item.product.price - (cart_item.product.price * cart_item.product.category.discount * 0.01 ))* cart_item.quantity)
            
            quantity += cart_item.quantity
            for i in cart_ii:
                cart_item_id = (i['id'])
            print(cart_item_id, '.....cart_item id in checkout')

            cart_i = CartItem.objects.get(id =cart_item_id)
            coupon_code = cart_i.coupon
           
            try:        #coupon_code = cart_i.coupon
                coupon = Coupon.objects.get(coupon_code = coupon_code)
                print(coupon.id , 'coupon_id')
                print(coupon_code, '-----coupon_code')
                coupon_code_ = Coupon.objects.get(coupon_code = coupon_code)
                print(coupon_code_, '-----coupon_code_')

                coupon_discount = coupon_code_.disccount
                
                print(coupon_discount, '-------coupon_discount')

                coupon_discount_total = int((totals * (coupon_discount/100)))
                if coupon_discount_total > coupon_code_.maximum_amount:
                    coupon_discount_total = coupon_code_.maximum_amount
                elif coupon_discount_total < coupon_code_.minimum_amount:
                    coupon_discount_total = coupon_code_.minimum_amount

                total = totals - coupon_discount_total
                print(total, "=====total")

            except:
                total = totals
                print('except', total,'----')

        gst = int((12 * total)/100)
        grand_total = int(total + gst)
        request.session["grand_total"] = grand_total
        
    # except ObjectDoesNotExist:
        # pass

 
        context = {
            'totals' : totals,
            'total' : total,
            'coupon_discount_total': coupon_discount_total,
            'quantity' : quantity, 
            'cart_items' : cart_items,
            'coupon_code' : coupon_code,
            'gst' : gst,
            'grand_total' : grand_total,
            'addresses' : addresses,
        }
        
        return render(request, 'store/checkout.html', context )




def coupon(request):

    cart_coupon = None
    cart_ii=[]
    cart_item_id = 0
    if request.method == "GET":
        coupon_code = request.GET['coupon_code']
        coupon = Coupon.objects.get(coupon_code = coupon_code)
        print(coupon_code,'request post...order')
        
        
        try:
            
            print('code is true')

            if coupon.is_expired == False:
                if request.user.is_authenticated:
                    user = request.user 
                    cart_ii = CartItem.objects.values().filter(user=request.user).order_by('id')[:1]

                    for i in cart_ii:
                        cart_item_id = (i['id'])
                    cart_i = CartItem.objects.get(id =cart_item_id)
                    cart_coupon = cart_i.coupon
                    print(cart_item_id, '.....cart_item id in coupon')


                    if cart_coupon == coupon_code:

                        return JsonResponse(
                        {
                        'coupon_exist' : True,
                        
                        },safe= False
                                            )
                    elif Order.objects.filter(Q(user_id = user.id)& Q(coupon_id = coupon.id) & Q(is_ordered = True)).exists():
                        return JsonResponse(
                        {
                        'already' : True,
                        
                        },safe= False
                                            )


                    else:
                        cart_i.coupon = coupon_code
                        cart_i.save()
                        print('cart_i.coupon afret,', cart_i.coupon)
                else:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    cart_ii = CartItem.objects.values().filter(user=request.user).order_by('id')[:1]
                    for i in cart_ii:
                        cart_item_id = (i['id'])
                    cart_i = CartItem.objects.get(id =cart_item_id)
                    coupon_code = cart_i.coupon
                    if cart_i.coupon == coupon_code:
                        return JsonResponse(
                        {
                        'coupon_exist' : False,
                        
                        },safe= False
                                            )

                    else:
                        cart_i.coupon = coupon_code
                        cart_i.save()



                return JsonResponse(
                    {
                        'success' : True,
                    },safe= False
                )
            else:
                return JsonResponse(
                    {
                        'success' : False,
                    },safe= False
                )

    
        except:
            return JsonResponse(
                    {
                        'coupon_valid' : False,
                        
                    },safe= False
                )
    return JsonResponse(
                    {
                        'coupon_valid' : True,
                        
                    },safe= False
                )

def remove_coupon(request):


    if request.method == "GET":


        if request.user.is_authenticated:
            cart_ii = CartItem.objects.values().filter(user=request.user).order_by('id')[:1]
            for i in cart_ii:
                cart_item_id = (i['id'])
            cart_i = CartItem.objects.get(id =cart_item_id)
            cart_i.coupon = None
            cart_i.save()

            print('usr cart')
            return JsonResponse(
            {
            'success' : True,
            
            },safe= False
                                )

                    
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_ii = CartItem.objects.values().filter(user=request.user).order_by('id')[:1]
            for i in cart_ii:
                cart_item_id = (i['id'])
            cart_i = CartItem.objects.get(id =cart_item_id)
            cart_i.coupon = None
            cart_i.save()
            print('not user')
            return JsonResponse(
            {
            'success' : False,
            
            },safe= False
                                )

    else:               


        print('aaaroooo..')
        return JsonResponse(
            {
                'notget' : True,
            },safe= False
        )

