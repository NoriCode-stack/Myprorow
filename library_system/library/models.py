from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('分类描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = '图书分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', '可借阅'),
        ('borrowed', '已借出'),
        ('maintenance', '维护中'),
    ]

    title = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100)
    isbn = models.CharField('ISBN', max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    publisher = models.CharField('出版社', max_length=100)
    publish_date = models.DateField('出版日期', null=True, blank=True)
    description = models.TextField('简介', blank=True)
    cover_image = models.URLField('封面图片URL', blank=True, default='')
    total_copies = models.PositiveIntegerField('总册数', default=1)
    available_copies = models.PositiveIntegerField('可借册数', default=1)
    location = models.CharField('馆藏位置', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def borrow_rate(self):
        if self.total_copies == 0:
            return 0
        borrowed = self.total_copies - self.available_copies
        return round((borrowed / self.total_copies) * 100, 1)


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', '借阅中'),
        ('returned', '已归还'),
        ('overdue', '已逾期'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='借阅人', related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='图书', related_name='borrow_records')
    borrow_date = models.DateTimeField('借阅日期', default=timezone.now)
    due_date = models.DateTimeField('应还日期')
    return_date = models.DateTimeField('实际归还日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='borrowed')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return timezone.now() > self.due_date

    @property
    def overdue_days(self):
        if not self.is_overdue:
            return 0
        delta = timezone.now() - self.due_date
        return delta.days

    def save(self, *args, **kwargs):
        if self.return_date and self.status != 'returned':
            self.status = 'returned'
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户', related_name='profile')
    phone = models.CharField('电话', max_length=20, blank=True)
    student_id = models.CharField('学号/工号', max_length=20, blank=True)
    department = models.CharField('院系/部门', max_length=50, blank=True)
    max_borrow_limit = models.PositiveIntegerField('最大借阅数', default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

    def __str__(self):
        return self.user.username

    @property
    def current_borrowed_count(self):
        return self.user.borrow_records.filter(status='borrowed').count()

    @property
    def can_borrow(self):
        return self.current_borrowed_count < self.max_borrow_limit
