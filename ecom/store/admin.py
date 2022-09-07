from django.contrib import admin
from .models import product, Variation, Coupon

# Register your models here.
class productAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'brand', 'price', 'stock', 'discount', 'modified_date', 'is_available' )
    prepopulated_fields = {'slug' : ('product_name', )}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'disccount', 'is_expired', 'minimum_amount', 'maximum_amount' )
    




admin.site.register(product, productAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Coupon, CouponAdmin)
