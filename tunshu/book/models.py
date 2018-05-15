from django.db import models

from custom_user.models import User


class Category(models.Model):
    name = models.CharField(max_length=200,
                            db_index=True, unique=True)
    image = models.ImageField(upload_to='categories/')

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Book(models.Model):
    owner = models.ForeignKey(
        User, related_name='sell_books', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='book/%Y/%m/%d', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, related_name='books', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created', '-updated')

    def __str__(self):
        return self.name
