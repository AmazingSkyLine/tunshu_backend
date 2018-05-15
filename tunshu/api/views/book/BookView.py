from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework.views import APIView

from api.utils.serializers import BookSerializer, book_serializer
from api.utils.utils import json_res, save_or_not
from book.models import Book, Category
from custom_user.models import User
from ..custom_user.UserView import redis_service
import json

import logging

logger = logging.getLogger('tunshu.views')


class BookListView(APIView):

    def get(self, request):
        books = Book.objects.all()

        res_dict = book_serializer(books)
        return json_res(200, '获取书籍列表成功', res_dict)


class BookDetailView(APIView):

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        books = BookSerializer(book).data
        return json_res(200, '获取书籍详情成功', books)

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        req_data = request.POST

        image = request.FILES.get('img', None)
        if image:
            book.image = image

        try:
            save_or_not(book, req_data, ['name', 'price', 'original_price', 'category_id'])
        except Exception as e:
            logger.error(e)
            return json_res(400, '编辑书籍信息失败')
        return json_res(200, '编辑书籍信息成功', {'detail_url': 'http://139.199.131.21/api/book/{}'.format(book.id)})

    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        try:
            book.delete()
        except Exception as e:
            logger.error(e)
            return json_res(400, '删除书籍失败')
        return json_res(200, '删除书籍成功')


class BookListByCategoryView(APIView):

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        books = category.books.all()

        res_dict = book_serializer(books)
        return json_res(200, '获取书籍列表成功', res_dict)


@require_POST
def create_book_info(request):
    req_data = request.POST
    image = request.FILES.get('img', None)
    category_id = req_data.get('category_id', None)

    if not image:
        return json_res(400, '缺少图片')
    try:
        new_book = Book.objects.create(name=req_data['name'], price=req_data['price'],
                                       original_price=req_data['original_price'], owner=request.custom_user,
                                       category_id=category_id)
        new_book.image = image
        new_book.save()
    except Exception as e:
        logger.error(e)
        return json_res(400, '创建书籍信息失败')

    # 保存所有用户发布的书籍数用来进行推荐
    redis_service.zincrby('user_ranking', request.custom_user.id, 1)

    return json_res(200, '创建书籍信息成功', {'detail_url': 'http://139.199.131.21/api/book/{}'.format(new_book.id)})


def get_all_categories(request):
    categories = Category.objects.all()

    counter = categories.count()
    res_list = []
    for c in categories:
        res_list.append({"image_url": 'http://139.199.131.21' + c.image.url, "name": c.name,
                         "detail_url": "http://139.199.131.21/api/book/category/{}/".format(c.id), "id": c.id})
    res_dict = {'sum': counter, 'categories': res_list}
    return json_res(200, '获取所有分类成功', res_dict)


def book_search(request):

    # 基于关键字和类别进行查询
    category_id = request.GET.get('category_id', None)
    query = request.GET.get('query')

    books = Book.objects.all().order_by('-created')
    for c in query:
        books = [book for book in books if c in book.name]
    # books = Book.objects.filter(name__icontains=query).order_by('-created')

    if category_id:
        books = [book for book in books if book.category_id == int(category_id)]

    res_dict = book_serializer(books)
    return json_res(200, '搜索成功', res_dict)


def book_advice(request):

    # 基于用户发布的书籍量和时间对书籍进行推荐，　发布书越多的用户，会取其最新发布的一本书作为推荐
    user_ranking = redis_service.zrange('user_ranking', 0, -1, desc=True)[:5]
    user_ranking_ids = [int(id) for id in user_ranking]
    most_offer = list(User.objects.filter(id__in=user_ranking_ids))

    most_offer.sort(key=lambda x: user_ranking_ids.index(x.id))

    books = [user.sell_books.order_by('-created')[0] for user in most_offer]

    res_dict = book_serializer(books)
    return json_res(200, '获取推荐图书成功', res_dict)
