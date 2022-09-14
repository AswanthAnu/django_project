from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('otp_registration/<int:phone_number>/',views.otp_registration, name='otp_registration'),
    path('otp_registration/',views.otp_registration, name='otp_registration'),

    path('login/',views.login, name='login'),
    path('otp_view/',views.otp_view, name='otp_view'),
    path('otp_login/<int:phone_number>/',views.otp_login, name='otp_login'),
    path('otp_login/',views.otp_login, name='otp_login'),
   
    # path('otp_registration/',views.otp_registration, name='otp_registration'),
    path('logout/',views.logout, name='logout'),

    path('dashboard/',views.dashboard, name='dashboard'),
    path('my_orders/',views.my_orders, name='my_orders'),
    path('edit_profile/',views.edit_profile, name='edit_profile'),
    path('address/',views.address, name='address'),
    path('change_password/',views.change_password, name='change_password'),
    path('my_orders/cancel_order/<str:order_no>/<str:order_prdt>/<str:order_qnty>', views.cancel_order, name='cancel_order'),
    path('my_orders/return_product', views.return_product, name='return_product'),
    path('invoice_download', views.invoice_download, name='invoice_download'),
    
]