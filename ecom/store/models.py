from django.db import models
from category.models import SubCategory, category
from brand.models import brand 
from django.urls import reverse



# Create your models here.

class product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to = 'photo/products', null = True)
    image2 = models.ImageField(upload_to = 'photo/products', null = True)
    image3 = models.ImageField(upload_to = 'photo/products', null = True)
    stock = models.IntegerField()
    discount = models.IntegerField(null= False, default= 0 )
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    brand = models.ForeignKey(brand, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null="false")
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.subcategory.slug, self.slug])

    def __str__(self):
        return self.product_name



class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value     = models.CharField(max_length=100)
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)

    objects = VariationManager()
    

    def __str__(self):
        return self.variation_value


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=8)
    is_expired = models.BooleanField(default=False)
    disccount = models.IntegerField(default=0)
    minimum_amount = models.IntegerField(default=500)
    maximum_amount = models.IntegerField(null=True)

    def __str__(self):
        return self.coupon_code