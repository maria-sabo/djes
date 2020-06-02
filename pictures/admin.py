from django.contrib import admin

from .models import Picture, Author, Museum, Address, Person, TestModel, TestFk, Picture2, Author2, Museum2, Address2, Person2

admin.site.register(Picture)
admin.site.register(Author)
admin.site.register(Museum)
admin.site.register(Address)
admin.site.register(Person)

admin.site.register(Picture2)
admin.site.register(Author2)
admin.site.register(Museum2)
admin.site.register(Address2)
admin.site.register(Person2)
admin.site.register(TestModel)
admin.site.register(TestFk)