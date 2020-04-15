from django.db import models


class Author(models.Model):
    name = models.TextField(db_index=True)
    date_birth = models.DateField()
    date_death = models.DateField()
    country_birth = models.TextField()
    note = models.CharField(default='', max_length=10000)

    def repr_json(self):
        return dict(name=self.name,
                    countrybirth=self.country_birth, note=self.note)


class Museum(models.Model):
    name = models.TextField()
    city = models.TextField()
    country = models.TextField()
    year_foundation = models.IntegerField()
    note = models.TextField(default='')

    def repr_json(self):
        return dict(name=self.name, city=self.city, country=self.country,
                    yearfoundation=self.year_foundation, note=self.note)


class Picture(models.Model):
    name = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE)
    note = models.TextField(default='')

    def repr_json(self):
        return dict(name=self.name, author=self.author, museum=self.museum, note=self.note)
