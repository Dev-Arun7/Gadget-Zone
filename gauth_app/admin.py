from django.contrib import admin
from gauth_app.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Order)