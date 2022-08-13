from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    path('otp_view/',views.otp_view, name='otp_view'),
    path('otp_login/<uid>',views.otp_login, name='otp_login'),
    path('otp_login/',views.otp_login, name='otp_login'),
    path('logout/',views.logout, name='logout'),

]