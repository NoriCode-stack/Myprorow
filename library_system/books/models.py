from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('分类名称', max_length=50)
    description = models.TextField('分类描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

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
        ('reserved', '已预约'),
        ('maintenance', '维护中'),
    ]

    title = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100)
    isbn = models.CharField('ISBN', max_length=20, unique=True)
    publisher = models.CharField('出版社', max_length=100, blank=True)
    publish_date = models.DateField('出版日期', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    description = models.TextField('图书简介', blank=True)
    cover_image = models.URLField('封面图片', blank=True, default='https://via.placeholder.com/150x200?text=No+Cover')
    total_copies = models.PositiveIntegerField('总库存', default=1)
    available_copies = models.PositiveIntegerField('可借数量', default=1)
    location = models.CharField('存放位置', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField('入库时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.author}'

    def save(self, *args, **kwargs):
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        if self.available_copies == 0:
            self.status = 'borrowed'
        else:
            self.status = 'available'
        super().save(*args, **kwargs)


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', '借阅中'),
        ('returned', '已归还'),
        ('overdue', '已逾期'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='借阅用户')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='图书')
    borrow_date = models.DateTimeField('借阅日期', auto_now_add=True)
    due_date = models.DateTimeField('应还日期')
    return_date = models.DateTimeField('实际归还日期', null=True, blank=True)
    status = models.CharField('借阅状态', max_length=20, choices=STATUS_CHOICES, default='borrowed')
    fine_amount = models.DecimalField('罚款金额', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'

    def is_overdue(self):
        if self.status == 'returned':
            return False
        return timezone.now() > self.due_date

    def get_fine(self):
        if not self.is_overdue():
            return 0
        overdue_days = (timezone.now() - self.due_date).days
        return max(0, overdue_days * 1)  # 每天1元罚款

    def save(self, *args, **kwargs):
        if self.is_overdue() and self.status != 'returned':
            self.status = 'overdue'
            self.fine_amount = self.get_fine()
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    phone = models.CharField('手机号', max_length=20, blank=True)
    address = models.CharField('地址', max_length=200, blank=True)
    max_books = models.PositiveIntegerField('最大借阅数量', default=5)
    is_vip = models.BooleanField('VIP用户', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return self.user.username

    def get_current_borrows(self):
        return BorrowRecord.objects.filter(user=self.user, status__in=['borrowed', 'overdue']).count()

    def can_borrow(self):
        return self.get_current_borrows() < self.max_books
