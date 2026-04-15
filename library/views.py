from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from datetime import date, timedelta
from .models import Book, BorrowRecord, UserProfile


def index(request):
    books = Book.objects.all()[:6]
    total_books = Book.objects.count()
    total_borrowed = BorrowRecord.objects.filter(status='借阅中').count()
    return render(request, 'index.html', {
        'books': books,
        'total_books': total_books,
        'total_borrowed': total_borrowed,
    })


def book_list(request):
    books = Book.objects.all()
    categories = dict(Book.CATEGORY_CHOICES).keys()

    search = request.GET.get('search', '')
    category = request.GET.get('category', '')

    if search:
        books = books.filter(Q(title__icontains=search) | Q(author__icontains=search))
    if category:
        books = books.filter(category=category)

    return render(request, 'book_list.html', {
        'books': books,
        'categories': categories,
        'search': search,
        'selected_category': category,
    })


@login_required
def borrow_manage(request):
    books = Book.objects.filter(available_stock__gt=0)
    my_borrowed = BorrowRecord.objects.filter(user=request.user, status='借阅中')
    return render(request, 'borrow_manage.html', {
        'books': books,
        'my_borrowed': my_borrowed,
    })


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.available_stock <= 0:
        messages.error(request, '该书库存不足！')
        return redirect('borrow_manage')

    user_borrowed = BorrowRecord.objects.filter(user=request.user, status='借阅中').count()
    if user_borrowed >= 5:
        messages.error(request, '您已达到最大借阅数量！')
        return redirect('borrow_manage')

    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        due_date=date.today() + timedelta(days=30)
    )
    book.available_stock -= 1
    book.save()
    messages.success(request, f'成功借阅《{book.title}》！')
    return redirect('borrow_manage')


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)
    if record.status == '已归还':
        messages.error(request, '该书已归还！')
        return redirect('borrow_manage')

    record.status = '已归还'
    record.return_date = date.today()
    record.save()

    book = record.book
    book.available_stock += 1
    book.save()
    messages.success(request, f'成功归还《{book.title}》！')
    return redirect('borrow_manage')


@login_required
def my_records(request):
    records = BorrowRecord.objects.filter(user=request.user)
    overdue_count = records.filter(status='借阅中', due_date__lt=date.today()).count()
    for record in records:
        if record.status == '借阅中' and record.due_date < date.today():
            record.status = '已逾期'
            record.save()
    return render(request, 'my_records.html', {
        'records': records,
        'overdue_count': overdue_count,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, '无权限访问！')
        return redirect('index')
    books = Book.objects.all()
    users = User.objects.all()
    records = BorrowRecord.objects.all()
    return render(request, 'admin_dashboard.html', {
        'books': books,
        'users': users,
        'records': records,
    })


@login_required
def admin_book_add(request):
    if not request.user.is_staff:
        return redirect('index')
    if request.method == 'POST':
        book = Book.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            isbn=request.POST.get('isbn'),
            category=request.POST.get('category'),
            description=request.POST.get('description', ''),
            total_stock=int(request.POST.get('total_stock', 5)),
            available_stock=int(request.POST.get('total_stock', 5)),
            publish_year=int(request.POST.get('publish_year', 2024)),
            publisher=request.POST.get('publisher', '未知出版社'),
        )
        messages.success(request, '图书添加成功！')
        return redirect('admin_dashboard')
    categories = dict(Book.CATEGORY_CHOICES).keys()
    return render(request, 'admin_book_form.html', {'categories': categories})


@login_required
def admin_book_edit(request, book_id):
    if not request.user.is_staff:
        return redirect('index')
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.category = request.POST.get('category')
        book.description = request.POST.get('description', '')
        new_total = int(request.POST.get('total_stock', 5))
        diff = new_total - book.total_stock
        book.total_stock = new_total
        book.available_stock += diff
        book.publish_year = int(request.POST.get('publish_year', 2024))
        book.publisher = request.POST.get('publisher', '未知出版社')
        book.save()
        messages.success(request, '图书更新成功！')
        return redirect('admin_dashboard')
    categories = dict(Book.CATEGORY_CHOICES).keys()
    return render(request, 'admin_book_form.html', {'book': book, 'categories': categories})


@login_required
def admin_book_delete(request, book_id):
    if not request.user.is_staff:
        return redirect('index')
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, '图书删除成功！')
    return redirect('admin_dashboard')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        messages.error(request, '用户名或密码错误！')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('index')


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, '两次密码不一致！')
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在！')
            return render(request, 'register.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        messages.success(request, '注册成功，请登录！')
        return redirect('login')
    return render(request, 'register.html')
