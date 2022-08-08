from django.contrib import admin
from .models import brand

# Register your models here.

class brandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('brand_name',)}
    list_display = ('brand_name', 'slug')


admin.site.register(brand, brandAdmin)