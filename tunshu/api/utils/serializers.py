from rest_framework import serializers

from book.models import Book, Category
from custom_user.models import User
from message.models import Notification


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'qq', 'weixin', 'nickname', 'gender', 'major', 'avatarUrl')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ('id', 'name', 'image', 'price', 'original_price', 'created',
                  'updated', 'category')


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('from_user', 'to_user', 'content', 'created')


def book_serializer(books):
    book_list = []
    for book in books:
        book_list.append({'id': book.id, 'name': book.name, 'image': 'http://139.199.131.21' + book.image.url,
                          'detail_url': 'http://139.199.131.21/api/book/{}'.format(book.id), 'qq': book.owner.qq,
                          'weixin': book.owner.weixin, 'original_price': book.original_price, 'price': book.price})
    res_dict = {'books': book_list}

    return res_dict
