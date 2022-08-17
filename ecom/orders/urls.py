from django.urls import path
from . import views

urlpatterns = [
    path('place_order/',views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_success/', views.order_success, name='order_success'),

]