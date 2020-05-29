from django.contrib import admin

from .models import Picture, Author, Museum, Address, Person, TestModel, TestFk

admin.site.register(Picture)
admin.site.register(Author)
admin.site.register(Museum)
admin.site.register(Address)
admin.site.register(Person)
admin.site.register(TestModel)
admin.site.register(TestFk)