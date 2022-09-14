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

    path('admin_subcategory',views.admin_subcategory, name='admin_subcategory'),
    path('add_subcategory',views.add_subcategory, name='add_subcategory'),
    path('edit_subcategory',views.edit_subcategory, name='edit_subcategory'),
    path('update_subcategory/<str:id>', views.update_subcategory, name="update_subcategory"),
    path('delete_subcategory/<str:id>', views.delete_subcategory, name='delete_subcategory'),

    path('admin_brand', views.admin_brand, name='admin_brand'),
    path('add_brand', views.add_brand, name='add_brand'),
    path('edit_brand', views.edit_brand, name='edit_brand'),
    path('delete_brand/<str:id>', views.delete_brand, name='delete_brand'),
    path('update_brand/<str:id>', views.update_brand, name='update_brand'),

    path('admin_product', views.admin_product, name='admin_product'),
    path('add_product', views.add_product, name='add_product'),
    path('edit_product', views.edit_product, name='edit_product'),
    path('delete_product/<str:id>', views.delete_product, name='delete_product'),
    path('update_product/<str:id>', views.update_product, name='update_product'),

    path('admin_variation', views.admin_variation, name='admin_variation'),
    path('add_variation', views.add_variation, name='add_variation'),
    path('edit_variation', views.edit_variation, name='edit_variation'),
    path('update_variation/<str:id>', views.update_variation, name='update_variation'),
    path('delete_variation/<str:id>', views.delete_variation, name='delete_variation'),

    path('admin_order', views.admin_order, name='admin_order'),
    path('change_order_status/<str:st>/<int:oid>/<int:pid>',views.change_order_status,name="order_status_change"),
    path('admin_cancel_order/<int:oid>', views.admin_cancel_order, name='admin_cancel_order'),

    path('admin_offer', views.admin_offer, name='admin_offer'),
    path('add_offer', views.add_offer, name='add_offer'),
    path('edit_offer', views.edit_offer, name='edit_offer'),
    path('delete_offer/<str:id>', views.delete_offer, name='delete_offer'),

    path('admin_offer_cat', views.admin_offer_cat, name='admin_offer_cat'),
    path('add_offer_cat', views.add_offer_cat, name='add_offer_cat'),
    path('delete_offer_cat/<str:id>', views.delete_offer_cat, name='delete_offer_cat'),

    path('admin_coupon', views.admin_coupon, name='admin_coupon'),
    path('add_coupon', views.add_coupon, name='add_coupon'),
    path('expire_coupon/<str:id>', views.expire_coupon, name='expire_coupon'),


    path('admin_sales', views.admin_sales, name='admin_sales'),
    path('export_pdf', views.export_pdf, name='export_pdf'),
    path('export_excel', views.export_excel, name='export_excel'),

    path('admin_return', views.admin_return, name="admin_return"),

    path('admin_banner', views.admin_banner, name="admin_banner"),
    path('banner_select/<str:id>', views.banner_select, name="banner_select"),
    path('add_banner', views.add_banner, name="add_banner"), 

    

    path('block_unblock/<int:id>',views.block_unblock,name='block_unblock'),

]