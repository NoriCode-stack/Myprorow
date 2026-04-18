from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/borrow/', views.borrow_book, name='borrow_book'),
    path('books/<int:pk>/return/', views.return_book, name='return_book'),
    path('my-records/', views.my_records, name='my_records'),
    path('overdue-alerts/', views.overdue_alerts, name='overdue_alerts'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/books/', views.admin_books, name='admin_books'),
    path('admin/books/add/', views.admin_book_add, name='admin_book_add'),
    path('admin/books/<int:pk>/edit/', views.admin_book_edit, name='admin_book_edit'),
    path('admin/books/<int:pk>/delete/', views.admin_book_delete, name='admin_book_delete'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/borrow-records/', views.admin_borrow_records, name='admin_borrow_records'),
]
