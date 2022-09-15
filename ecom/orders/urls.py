from django.urls import path
from . import views

urlpatterns = [
    path('place_order/',views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payments_cod/', views.payments_cod, name='payments_cod'),
    path('payments_razor/', views.payments_razor, name='payments_razor'),
    path('order_success/', views.order_success, name='order_success'),

]