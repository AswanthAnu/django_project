from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    path('otp_view/',views.otp_view, name='otp_view'),
    path('otp_login/<int:phone_number>/',views.otp_login, name='otp_login'),
    path('otp_login/',views.otp_login, name='otp_login'),
    path('otp_registration/<int:phone_number>/',views.otp_registration, name='otp_registration'),
    # path('otp_registration/',views.otp_registration, name='otp_registration'),
    path('logout/',views.logout, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('my_orders/',views.my_orders, name='my_orders'),
    path('edit_profile/',views.edit_profile, name='edit_profile'),
    path('change_password/',views.change_password, name='change_password'),

]