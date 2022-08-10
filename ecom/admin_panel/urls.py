from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_login, name='admin_login'),

    path('admin_dashboard',views.admin_dashboard, name='admin_dashboard'),
    path('admin_user',views.admin_user, name='admin_user'),
   
    path('admin_category',views.admin_category, name='admin_category'),
    path('add_category', views.add_category, name="add_category"),
    path('edit_category', views.edit_category, name="edit_category"),
    path('delete_category/<str:id>', views.delete_category, name='delete_category'),
    path('update_category/<str:id>', views.update_category, name="update_category"),

    path('admin_brand', views.admin_brand, name='admin_brand'),
    path('add_brand', views.add_brand, name='add_brand'),
    path('edit_brand', views.edit_brand, name='edit_brand'),
    path('delete_brand/<str:id>', views.delete_brand, name='delete_brand'),
    path('update_brand/<str:id>', views.update_brand, name='update_brand'),
    

    path('block_unblock/<int:id>',views.block_unblock,name='block_unblock'),


  

]