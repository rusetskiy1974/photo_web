from distutils.command import register

from django.contrib import admin
from .models import User

admin.site.register(User)
