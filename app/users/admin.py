from distutils.command import register

from django.contrib import admin
from users.models import User

admin.site.register(User)
