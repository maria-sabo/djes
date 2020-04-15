from django.contrib import admin

from .models import Picture, Author, Museum

admin.site.register(Picture)
admin.site.register(Author)
admin.site.register(Museum)