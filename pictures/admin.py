from django.contrib import admin

from .models import Picture, Author, Museum, Address, Person

admin.site.register(Picture)
admin.site.register(Author)
admin.site.register(Museum)
admin.site.register(Address)
admin.site.register(Person)