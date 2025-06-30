from django.contrib import admin
from django.contrib import admin
from .models import Dataset
# Register your models here.
@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('data_name', 'uploaded_at')
    search_fields = ('data_name',)







# admin.site.register(Dataset)