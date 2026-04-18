from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')

    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = '图书分类'

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    isbn = models.CharField(max_length=13, unique=True, verbose_name='ISBN')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    cover = models.URLField(verbose_name='封面图片URL', default='https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=book%20cover%20abstract%20minimal&image_size=square')
    description = models.TextField(verbose_name='图书简介')
    publication_date = models.DateField(verbose_name='出版日期')
    publisher = models.CharField(max_length=100, verbose_name='出版社')
    total_copies = models.IntegerField(default=1, verbose_name='总馆藏')
    available_copies = models.IntegerField(default=1, verbose_name='可借数量')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'

    def __str__(self):
        return f'{self.title} - {self.author}'

    def is_available(self):
        return self.available_copies > 0


class BorrowRecord(models.Model):
    STATUS_BORROWED = 'borrowed'
    STATUS_RETURNED = 'returned'
    STATUS_OVERDUE = 'overdue'

    STATUS_CHOICES = [
        (STATUS_BORROWED, '借阅中'),
        (STATUS_RETURNED, '已归还'),
        (STATUS_OVERDUE, '已逾期'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='借阅用户')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='图书')
    borrow_date = models.DateTimeField(default=timezone.now, verbose_name='借阅日期')
    due_date = models.DateTimeField(verbose_name='应还日期')
    return_date = models.DateTimeField(null=True, blank=True, verbose_name='归还日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BORROWED, verbose_name='状态')

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=30)
        if self.return_date:
            self.status = self.STATUS_RETURNED
        elif timezone.now() > self.due_date:
            self.status = self.STATUS_OVERDUE
        super().save(*args, **kwargs)

    def is_overdue(self):
        if self.return_date:
            return False
        return timezone.now() > self.due_date

    def get_overdue_days(self):
        if self.return_date or not self.is_overdue():
            return 0
        return (timezone.now() - self.due_date).days
