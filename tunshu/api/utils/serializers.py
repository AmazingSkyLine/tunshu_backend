from rest_framework import serializers

from book.models import Book, Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ('id', 'name', 'image', 'price', 'original_price', 'description', 'created', 'updated', 'category')


def book_serializer(books):
    if not books:
        return {'books': None}

    book_list = []
    for book in books:
        book_list.append({'id': book.id, 'name': book.name, 'image': 'http://139.199.131.21' + book.image.url,
                          'detail_url': 'http://139.199.131.21/api/book/{}'.format(book.id), 
                          'weixin': book.owner.weixin, 'original_price': book.original_price, 'price': book.price,
                          'description': book.description})
    res_dict = {'books': book_list}

    return res_dict
