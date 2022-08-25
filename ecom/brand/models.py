from django.db import models
from django.urls import reverse

# Create your models here.

class brand(models.Model):
    brand_name = models.CharField(max_length=100, unique= True)
    slug = models.SlugField(max_length=100, unique=True, null=True)
    description = models.TextField(max_length=255, blank=True)
    brand_img = models.ImageField(upload_to='photos/brand', blank=True)
    
    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'

    def get_url(self):
            return reverse('products_by_brand',args=[self.slug] )


    def __str__(self):
        return self.brand_name
