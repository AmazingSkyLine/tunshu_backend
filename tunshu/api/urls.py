from django.urls import path
from .views.custom_user import UserView
from .views.book import BookView

urlpatterns = [
    path('user/wx_login/', UserView.wx_login, name='wx_login'),
    path('user/<int:user_id>/', UserView.user_info, name='user_info'),
    path('user/', UserView.change_user_info, name='change_user_info'),
    path('user/books/', UserView.get_user_books, name='get_user_books'),
    path('user/auth/', UserView.user_auth, name='user_auth'),

    path('book/', BookView.create_book_info, name='create_book_info'),
    path('books/', BookView.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', BookView.BookDetailView.as_view(), name='book_detail'),
    path('book/category/<int:pk>/',
         BookView.BookListByCategoryView.as_view(), name='book_list_categories'),
    path('book/search/', BookView.book_search, name='book_search'),
    path('book/advice/', BookView.book_advice, name='book_advice'), 
    path('categories/', BookView.get_all_categories, name='get_all_categories'),
]

