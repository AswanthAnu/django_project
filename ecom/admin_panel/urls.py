from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_login, name='admin_login'),
    path('admin_dashboard',views.admin_dashboard, name='admin_dashboard'),
    path('admin_user',views.admin_user, name='admin_user'),
    path('admin_product',views.admin_product, name='admin_product'),
    path('admin_category',views.admin_category, name='admin_category'),
    path('add_category', views.add_category, name="add_category"),
   path('block_unblock/<int:id>',views.block_unblock,name='block_unblock'),

  

]