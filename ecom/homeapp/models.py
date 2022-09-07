from django.db import models
from django.db import models

# Create your models here.


class banner(models.Model):
    
    banner_image =models.ImageField( upload_to='photos/banner', height_field=None, width_field=None, max_length=None,blank=True)
    
    is_selected = models.BooleanField(default=False)