from django.contrib import admin
from .models import image

class imageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'image', 'created']
    list_filter = ['created']

admin.site.register(image, imageAdmin)