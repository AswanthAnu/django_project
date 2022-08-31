from django.urls import reverse
from django.db import models

# Create your models here.

class category(models.Model):
    category_name = models.CharField(max_length=100, unique= True)
    slug = models.SlugField(max_length=100, unique=True, null=True, )
    discount = models.IntegerField(null= False, default= 0 )
    description = models.TextField(max_length=255, blank=True)
    category_img = models.ImageField(upload_to='photos/category', blank=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
            return reverse('products_by_category',args=[self.slug] )



    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    sub_category_name = models.CharField(max_length=100, unique= True)
    slug = models.SlugField(max_length=100, unique=True, null=True, )
    


    class Meta:
        verbose_name = 'SubCategory'
        verbose_name_plural = 'SubCategories'

    def get_url(self):
            return reverse('products_by_sub_category',args=[self.category.slug, self.slug] )


    def __str__(self):
        return self.sub_category_name
