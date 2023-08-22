from django.contrib import admin

from .models import Greeting, Profile

admin.site.register(Profile)
admin.site.register(Greeting)
