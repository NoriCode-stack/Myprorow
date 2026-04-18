from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta

from .models import Book, Category, BorrowRecord, UserProfile
from .forms import BookSearchForm, BookForm, BorrowForm


def home(request):
    categories = Category.objects.all()
    books = Book.objects.all().order_by('-created_at')[:8]
    popular_books = Book.objects.all().order_by('-total_copies')[:6]
    
    context = {
        'categories': categories,
        'books': books,
        'popular_books': popular_books,
    }
    return render(request, 'library/home.html', context)


def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    form = BookSearchForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        
        if search:
            books = books.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )
        if category:
            books = books.filter(category=category)
        if status:
            books = books.filter(status=status)
    
    books = books.order_by('-created_at')
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'form': form,
    }
    return render(request, 'library/book_list.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    related_books = Book.objects.filter(category=book.category).exclude(pk=book.pk)[:4]
    
    user_borrowed = False
    if request.user.is_authenticated:
        user_borrowed = BorrowRecord.objects.filter(
            user=request.user, 
            book=book, 
            status='borrowed'
        ).exists()
    
    context = {
        'book': book,
        'related_books': related_books,
        'user_borrowed': user_borrowed,
    }
    return render(request, 'library/book_detail.html', context)


@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if not book.is_available:
        messages.error(request, '该图书暂无可借副本')
        return redirect('book_detail', pk=pk)
    
    profile = request.user.profile
    
    if not profile.can_borrow:
        messages.error(request, f'您已达到最大借阅数量({profile.max_borrow_limit}本)，请先归还部分图书')
        return redirect('book_detail', pk=pk)
    
    existing_borrow = BorrowRecord.objects.filter(
        user=request.user, 
        book=book, 
        status='borrowed'
    ).exists()
    
    if existing_borrow:
        messages.warning(request, '您已借阅此书，请勿重复借阅')
        return redirect('book_detail', pk=pk)
    
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow_record = form.save(commit=False)
            borrow_record.user = request.user
            borrow_record.book = book
            borrow_record.save()
            
            book.available_copies -= 1
            if book.available_copies == 0:
                book.status = 'borrowed'
            book.save()
            
            messages.success(request, f'成功借阅《{book.title}》，请于{borrow_record.due_date.strftime("%Y-%m-%d")}前归还')
            return redirect('my_records')
    else:
        form = BorrowForm()
    
    context = {
        'book': book,
        'form': form,
    }
    return render(request, 'library/borrow_book.html', context)


@login_required
def return_book(request, pk):
    borrow_record = get_object_or_404(
        BorrowRecord, 
        pk=pk, 
        user=request.user, 
        status='borrowed'
    )
    
    if request.method == 'POST':
        borrow_record.return_date = timezone.now()
        borrow_record.status = 'returned'
        borrow_record.save()
        
        book = borrow_record.book
        book.available_copies += 1
        if book.status == 'borrowed' and book.available_copies > 0:
            book.status = 'available'
        book.save()
        
        messages.success(request, f'《{book.title}》已成功归还')
        return redirect('my_records')
    
    context = {
        'borrow_record': borrow_record,
    }
    return render(request, 'library/return_book.html', context)


@login_required
def my_records(request):
    records = BorrowRecord.objects.filter(user=request.user)
    
    status_filter = request.GET.get('status')
    if status_filter:
        records = records.filter(status=status_filter)
    
    records = records.order_by('-borrow_date')
    
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    overdue_count = BorrowRecord.objects.filter(
        user=request.user, 
        status='borrowed',
        due_date__lt=timezone.now()
    ).count()
    
    context = {
        'page_obj': page_obj,
        'overdue_count': overdue_count,
        'status_filter': status_filter,
    }
    return render(request, 'library/my_records.html', context)


@login_required
def overdue_alerts(request):
    overdue_records = BorrowRecord.objects.filter(
        user=request.user,
        status='borrowed',
        due_date__lt=timezone.now()
    ).order_by('due_date')
    
    upcoming_records = BorrowRecord.objects.filter(
        user=request.user,
        status='borrowed',
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timedelta(days=3)
    ).order_by('due_date')
    
    context = {
        'overdue_records': overdue_records,
        'upcoming_records': upcoming_records,
    }
    return render(request, 'library/overdue_alerts.html', context)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}！')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'library/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, '注册成功！欢迎加入图书馆')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'library/register.html', {'form': form})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    total_books = Book.objects.count()
    total_users = UserProfile.objects.count()
    active_borrows = BorrowRecord.objects.filter(status='borrowed').count()
    overdue_count = BorrowRecord.objects.filter(
        status='borrowed',
        due_date__lt=timezone.now()
    ).count()
    
    recent_borrows = BorrowRecord.objects.all().order_by('-borrow_date')[:10]
    
    context = {
        'total_books': total_books,
        'total_users': total_users,
        'active_borrows': active_borrows,
        'overdue_count': overdue_count,
        'recent_borrows': recent_borrows,
    }
    return render(request, 'library/admin/dashboard.html', context)


@login_required
def admin_books(request):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    books = Book.objects.all().order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search) | Q(isbn__icontains=search)
        )
    
    paginator = Paginator(books, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'library/admin/books.html', context)


@login_required
def admin_book_add(request):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'图书《{book.title}》添加成功')
            return redirect('admin_books')
    else:
        form = BookForm()
    
    context = {
        'form': form,
        'title': '添加图书',
    }
    return render(request, 'library/admin/book_form.html', context)


@login_required
def admin_book_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'图书《{book.title}》更新成功')
            return redirect('admin_books')
    else:
        form = BookForm(instance=book)
    
    context = {
        'form': form,
        'book': book,
        'title': '编辑图书',
    }
    return render(request, 'library/admin/book_form.html', context)


@login_required
def admin_book_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'图书《{title}》已删除')
        return redirect('admin_books')
    
    context = {
        'book': book,
    }
    return render(request, 'library/admin/book_confirm_delete.html', context)


@login_required
def admin_users(request):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    profiles = UserProfile.objects.all().select_related('user')
    
    search = request.GET.get('search')
    if search:
        profiles = profiles.filter(
            Q(user__username__icontains=search) | 
            Q(student_id__icontains=search)
        )
    
    paginator = Paginator(profiles, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'library/admin/users.html', context)


@login_required
def admin_borrow_records(request):
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
    
    records = BorrowRecord.objects.all().select_related('user', 'book')
    
    status = request.GET.get('status')
    if status:
        records = records.filter(status=status)
    
    records = records.order_by('-borrow_date')
    
    paginator = Paginator(records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
    }
    return render(request, 'library/admin/borrow_records.html', context)
