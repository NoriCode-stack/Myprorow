from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.book_list, name='book_list'),
    path('borrow/', views.borrow_manage, name='borrow_manage'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my-records/', views.my_records, name='my_records'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-book/add/', views.admin_book_add, name='admin_book_add'),
    path('admin-book/edit/<int:book_id>/', views.admin_book_edit, name='admin_book_edit'),
    path('admin-book/delete/<int:book_id>/', views.admin_book_delete, name='admin_book_delete'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
]
