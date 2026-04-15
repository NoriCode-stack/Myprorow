from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('文学小说', '文学小说'),
        ('科技编程', '科技编程'),
        ('历史人文', '历史人文'),
        ('经济管理', '经济管理'),
        ('心理学', '心理学'),
        ('少儿读物', '少儿读物'),
        ('科幻奇幻', '科幻奇幻'),
        ('其他', '其他'),
    ]

    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    isbn = models.CharField(max_length=20, unique=True, verbose_name='ISBN')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='分类')
    description = models.TextField(verbose_name='简介', default='暂无简介')
    cover = models.URLField(verbose_name='封面图片', default='https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=book%20cover%20minimal%20design&image_size=square_hd')
    total_stock = models.IntegerField(default=5, verbose_name='总库存')
    available_stock = models.IntegerField(default=5, verbose_name='可借数量')
    publish_year = models.IntegerField(default=2024, verbose_name='出版年份')
    publisher = models.CharField(max_length=100, default='未知出版社', verbose_name='出版社')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.author}"

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书管理'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    max_borrow_days = models.IntegerField(default=30, verbose_name='最长借阅天数')
    max_borrow_books = models.IntegerField(default=5, verbose_name='最大可借数量')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('借阅中', '借阅中'),
        ('已归还', '已归还'),
        ('已逾期', '已逾期'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateField(auto_now_add=True, verbose_name='借阅日期')
    due_date = models.DateField(verbose_name='应还日期')
    return_date = models.DateField(null=True, blank=True, verbose_name='归还日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='借阅中', verbose_name='状态')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = date.today() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_overdue(self):
        if self.status == '借阅中' and date.today() > self.due_date:
            return True
        return False

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']
