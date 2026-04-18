from django.contrib import admin
from django.urls import path
from books import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 首页
    path('', views.home, name='home'),
    
    # 图书相关
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/borrow/', views.borrow_book, name='borrow_book'),
    
    # 借阅相关
    path('my-borrows/', views.my_borrows, name='my_borrows'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),
    
    # 用户认证
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    
    # 后台管理
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/books/', views.admin_book_list, name='admin_book_list'),
    path('admin-panel/books/create/', views.admin_book_create, name='admin_book_create'),
    path('admin-panel/books/<int:pk>/edit/', views.admin_book_edit, name='admin_book_edit'),
    path('admin-panel/books/<int:pk>/delete/', views.admin_book_delete, name='admin_book_delete'),
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
    path('admin-panel/borrows/', views.admin_borrow_list, name='admin_borrow_list'),
]
