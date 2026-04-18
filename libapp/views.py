from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Category, Book, BorrowRecord


def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()

    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search)
        )

    if category_id:
        books = books.filter(category_id=category_id)

    context = {
        'books': books,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
    }
    return render(request, 'book_list.html', context)


@login_required
def borrow_manage(request):
    books = Book.objects.filter(available_copies__gt=0)
    my_borrowed = BorrowRecord.objects.filter(
        user=request.user,
        status__in=['borrowed', 'overdue']
    ).select_related('book')

    context = {
        'books': books,
        'my_borrowed': my_borrowed,
    }
    return render(request, 'borrow_manage.html', context)


@login_required
def my_records(request):
    records = BorrowRecord.objects.filter(
        user=request.user
    ).select_related('book').order_by('-borrow_date')

    overdue_count = records.filter(status='overdue').count()

    context = {
        'records': records,
        'overdue_count': overdue_count,
    }
    return render(request, 'my_records.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_manage(request):
    books = Book.objects.all().select_related('category')
    categories = Category.objects.all()
    borrow_records = BorrowRecord.objects.all().select_related('user', 'book').order_by('-borrow_date')[:50]

    context = {
        'books': books,
        'categories': categories,
        'borrow_records': borrow_records,
    }
    return render(request, 'admin_manage.html', context)


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.available_copies <= 0:
        messages.error(request, '该书已无库存！')
        return redirect('borrow_manage')

    existing = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        status__in=['borrowed', 'overdue']
    ).exists()

    if existing:
        messages.warning(request, '您已借阅该书，尚未归还！')
        return redirect('borrow_manage')

    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        due_date=timezone.now() + timezone.timedelta(days=30)
    )

    book.available_copies -= 1
    book.save()

    messages.success(request, f'成功借阅《{book.title}》！')
    return redirect('borrow_manage')


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)

    if record.status == 'returned':
        messages.warning(request, '该书已归还！')
        return redirect('borrow_manage')

    record.return_date = timezone.now()
    record.status = 'returned'
    record.save()

    book = record.book
    book.available_copies += 1
    book.save()

    messages.success(request, f'成功归还《{book.title}》！')
    return redirect('borrow_manage')


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        publication_date = request.POST.get('publication_date')
        publisher = request.POST.get('publisher')
        total_copies = int(request.POST.get('total_copies', 1))

        category = get_object_or_404(Category, id=category_id)

        Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            cover=f'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=book%20cover%20{title}&image_size=square',
            description=description,
            publication_date=publication_date,
            publisher=publisher,
            total_copies=total_copies,
            available_copies=total_copies,
        )
        messages.success(request, '图书添加成功！')
        return redirect('admin_manage')

    categories = Category.objects.all()
    return render(request, 'book_form.html', {'categories': categories})


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.category_id = request.POST.get('category')
        book.description = request.POST.get('description')
        book.publication_date = request.POST.get('publication_date')
        book.publisher = request.POST.get('publisher')
        new_total = int(request.POST.get('total_copies', 1))

        diff = new_total - book.total_copies
        book.total_copies = new_total
        book.available_copies += diff
        book.save()

        messages.success(request, '图书信息更新成功！')
        return redirect('admin_manage')

    categories = Category.objects.all()
    return render(request, 'book_form.html', {'book': book, 'categories': categories})


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, '图书删除成功！')
    return redirect('admin_manage')
