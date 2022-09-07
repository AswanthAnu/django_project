from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart , name='add_cart'),
    path('update_cart/<int:product_id>/', views.update_cart , name='update_cart'),

    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart , name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item , name='remove_cart_item'),


    path('checkout/', views.checkout , name='checkout'),
    path('checkout/coupon', views.coupon , name='coupon'),
    path('checkout/remove_coupon', views.remove_coupon , name='remove_coupon'),
]