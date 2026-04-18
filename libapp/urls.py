from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('borrow-manage/', views.borrow_manage, name='borrow_manage'),
    path('my-records/', views.my_records, name='my_records'),
    path('admin-manage/', views.admin_manage, name='admin_manage'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('admin-manage/book/add/', views.add_book, name='add_book'),
    path('admin-manage/book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('admin-manage/book/<int:book_id>/delete/', views.delete_book, name='delete_book'),
]
