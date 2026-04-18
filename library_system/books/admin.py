from django.contrib import admin
from .models import Category, Book, BorrowRecord, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'available_copies', 'total_copies', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    list_editable = ['status']


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'fine_amount']
    list_filter = ['status', 'borrow_date']
    search_fields = ['user__username', 'book__title']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'max_books', 'is_vip', 'created_at']
    list_filter = ['is_vip']
    search_fields = ['user__username', 'phone']
