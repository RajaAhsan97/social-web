from django.contrib import admin
from .models import Profile

# Register your models here.
class profileadmin(admin.ModelAdmin):
    list_display = ['user', 'dob', 'photo']
    raw_id_fields = ['user']

admin.site.register(Profile, profileadmin) 