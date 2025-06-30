from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import mark_safe
from decimal import Decimal
from django.conf import settings
import math
from django.db.models import Avg, Count
from django.urls import reverse
# Create your models here.
# analysis/models.py
STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Dataset(models.Model):
    data_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True,blank=True)
    title_tag = models.CharField(max_length=255, default='Data Analysis')
    meta_description = models.TextField(max_length=455, blank=True)
    meta_keywords = models.TextField(max_length=455, blank=True)
    thumbnail = models.ImageField(upload_to='datasets/thumbnail/%Y/%m/%d/', blank=True)
    content = CKEditor5Field(config_name='extends',blank=True, null=True)
    file = models.FileField(upload_to='datasets/%Y/%m/%d/',blank=True)
    is_approved = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS, default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)  # Save first to ensure self.id is available

        # Generate slug after initial save if not set
        if not self.slug and self.data_name:
            base_slug = slugify(self.data_name)
            self.slug = f"{base_slug}-{self.id}"
            super().save(update_fields=['slug'])
            
    def get_url(self):
         return reverse('dataset_detail', args=[self.slug])        
    
    def __str__(self):
        return self.data_name
    
