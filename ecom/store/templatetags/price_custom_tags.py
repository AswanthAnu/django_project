from django import template
import math
register = template.Library()


@register.simple_tag
def sell_price(pric , discout):

    price = int(pric)
    discount = int(discout)

    if discount is None or discount is 0:
        return price 

    
    # 100 - 10% = sellprice \ 100- (100 * 10 * .1/100)= 90
    # mrp-(mrp * discount * 0.01) = sellprice 
    sellprice = price
    sellprice = (price - ( price * discount * 0.01))
    return math.floor(sellprice)

