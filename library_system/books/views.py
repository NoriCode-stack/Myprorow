from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from .models import Book, Category, BorrowRecord, UserProfile


def home(request):
    """首页"""
    context = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(status='available').count(),
        'total_borrows': BorrowRecord.objects.count(),
        'new_books': Book.objects.order_by('-created_at')[:6],
        'hot_books': Book.objects.annotate(borrow_count=Count('borrowrecord')).order_by('-borrow_count')[:6],
    }
    return render(request, 'books/home.html', context)


def book_list(request):
    """图书列表与检索"""
    books = Book.objects.all()
    categories = Category.objects.all()
    
    # 搜索功能
    search_query = request.GET.get('q', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # 分类筛选
    category_id = request.GET.get('category', '')
    if category_id:
        books = books.filter(category_id=category_id)
    
    # 状态筛选
    status = request.GET.get('status', '')
    if status:
        books = books.filter(status=status)
    
    # 分页
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_status': status,
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, pk):
    """图书详情"""
    book = get_object_or_404(Book, pk=pk)
    
    # 检查当前用户是否已借阅
    user_borrowed = False
    if request.user.is_authenticated:
        user_borrowed = BorrowRecord.objects.filter(
            user=request.user,
            book=book,
            status__in=['borrowed', 'overdue']
        ).exists()
    
    context = {
        'book': book,
        'user_borrowed': user_borrowed,
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def borrow_book(request, pk):
    """借阅图书"""
    book = get_object_or_404(Book, pk=pk)
    
    # 检查用户资料
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.can_borrow():
        messages.error(request, f'您已达到最大借阅数量限制（{profile.max_books}本）')
        return redirect('book_detail', pk=pk)
    
    if book.available_copies <= 0:
        messages.error(request, '该图书暂无可借副本')
        return redirect('book_detail', pk=pk)
    
    # 检查是否已借阅
    existing = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        status__in=['borrowed', 'overdue']
    ).exists()
    
    if existing:
        messages.warning(request, '您已借阅该图书，请勿重复借阅')
        return redirect('book_detail', pk=pk)
    
    # 创建借阅记录
    due_date = timezone.now() + timedelta(days=30)
    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        due_date=due_date
    )
    
    # 更新图书可借数量
    book.available_copies -= 1
    book.save()
    
    messages.success(request, f'成功借阅《{book.title}》，请于 {due_date.strftime("%Y-%m-%d")} 前归还')
    return redirect('my_borrows')


@login_required
def return_book(request, borrow_id):
    """归还图书"""
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_id, user=request.user)
    
    if borrow_record.status == 'returned':
        messages.warning(request, '该图书已归还')
        return redirect('my_borrows')
    
    # 更新借阅记录
    borrow_record.status = 'returned'
    borrow_record.return_date = timezone.now()
    borrow_record.save()
    
    # 更新图书可借数量
    book = borrow_record.book
    book.available_copies += 1
    book.save()
    
    messages.success(request, f'成功归还《{book.title}》')
    return redirect('my_borrows')


@login_required
def my_borrows(request):
    """我的借阅记录"""
    current_borrows = BorrowRecord.objects.filter(
        user=request.user,
        status__in=['borrowed', 'overdue']
    ).order_by('-borrow_date')
    
    history_borrows = BorrowRecord.objects.filter(
        user=request.user,
        status='returned'
    ).order_by('-return_date')[:10]
    
    # 计算逾期提醒
    overdue_count = current_borrows.filter(status='overdue').count()
    
    # 即将到期（3天内）
    soon_due = current_borrows.filter(
        status='borrowed',
        due_date__lte=timezone.now() + timedelta(days=3)
    )
    
    context = {
        'current_borrows': current_borrows,
        'history_borrows': history_borrows,
        'overdue_count': overdue_count,
        'soon_due': soon_due,
    }
    return render(request, 'books/my_borrows.html', context)


@login_required
def admin_dashboard(request):
    """后台管理首页"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问管理后台')
        return redirect('home')
    
    context = {
        'total_books': Book.objects.count(),
        'total_users': UserProfile.objects.count(),
        'active_borrows': BorrowRecord.objects.filter(status__in=['borrowed', 'overdue']).count(),
        'overdue_borrows': BorrowRecord.objects.filter(status='overdue').count(),
        'recent_borrows': BorrowRecord.objects.order_by('-borrow_date')[:10],
    }
    return render(request, 'books/admin/dashboard.html', context)


@login_required
def admin_book_list(request):
    """图书管理"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问')
        return redirect('home')
    
    books = Book.objects.all().order_by('-created_at')
    
    # 搜索
    search_query = request.GET.get('q', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    paginator = Paginator(books, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'books/admin/book_list.html', context)


@login_required
def admin_book_create(request):
    """添加图书"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限')
        return redirect('home')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        publisher = request.POST.get('publisher')
        category_id = request.POST.get('category')
        total_copies = request.POST.get('total_copies', 1)
        description = request.POST.get('description')
        location = request.POST.get('location')
        
        category = Category.objects.get(id=category_id) if category_id else None
        
        Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            publisher=publisher,
            category=category,
            total_copies=total_copies,
            available_copies=total_copies,
            description=description,
            location=location,
        )
        
        messages.success(request, '图书添加成功')
        return redirect('admin_book_list')
    
    context = {
        'categories': categories,
    }
    return render(request, 'books/admin/book_form.html', context)


@login_required
def admin_book_edit(request, pk):
    """编辑图书"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限')
        return redirect('home')
    
    book = get_object_or_404(Book, pk=pk)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.publisher = request.POST.get('publisher')
        category_id = request.POST.get('category')
        book.category = Category.objects.get(id=category_id) if category_id else None
        book.total_copies = request.POST.get('total_copies', 1)
        book.description = request.POST.get('description')
        book.location = request.POST.get('location')
        book.save()
        
        messages.success(request, '图书更新成功')
        return redirect('admin_book_list')
    
    context = {
        'book': book,
        'categories': categories,
    }
    return render(request, 'books/admin/book_form.html', context)


@login_required
def admin_book_delete(request, pk):
    """删除图书"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限')
        return redirect('home')
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, '图书删除成功')
        return redirect('admin_book_list')
    
    context = {
        'book': book,
    }
    return render(request, 'books/admin/book_delete.html', context)


@login_required
def admin_user_list(request):
    """用户管理"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限')
        return redirect('home')
    
    profiles = UserProfile.objects.select_related('user').all()
    
    # 搜索
    search_query = request.GET.get('q', '')
    if search_query:
        profiles = profiles.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(profiles, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'books/admin/user_list.html', context)


@login_required
def admin_borrow_list(request):
    """借阅记录管理"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限')
        return redirect('home')
    
    borrows = BorrowRecord.objects.select_related('user', 'book').all().order_by('-borrow_date')
    
    # 筛选
    status = request.GET.get('status', '')
    if status:
        borrows = borrows.filter(status=status)
    
    paginator = Paginator(borrows, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'selected_status': status,
    }
    return render(request, 'books/admin/borrow_list.html', context)


def user_login(request):
    """用户登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # 创建用户资料
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f'欢迎回来，{user.username}！')
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'books/login.html')


def user_logout(request):
    """用户登出"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('home')


def user_register(request):
    """用户注册"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'books/register.html')
        
        from django.contrib.auth.models import User
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'books/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'books/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        
        messages.success(request, '注册成功，请登录')
        return redirect('login')
    
    return render(request, 'books/register.html')
