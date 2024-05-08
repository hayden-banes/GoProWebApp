from django.contrib import admin

# Register your models here.
from .models import GoPro, Timelapse

admin.site.register(GoPro)
admin.site.register(Timelapse)