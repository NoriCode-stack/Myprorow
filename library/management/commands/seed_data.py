from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from library.models import Book, UserProfile, BorrowRecord
from datetime import date, timedelta


class Command(BaseCommand):
    help = '生成模拟数据'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('开始生成模拟数据...')

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@library.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user)
        if created:
            self.stdout.write('创建管理员用户: admin / admin123')

        demo_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@library.com',
            }
        )
        if created:
            demo_user.set_password('user123')
            demo_user.save()
        UserProfile.objects.get_or_create(user=demo_user)
        if created:
            self.stdout.write('创建演示用户: user / user123')

        if not User.objects.filter(username='user').exists():
            self.stdout.write(self.style.WARNING('演示用户不存在，跳过借阅记录生成'))
            return

        books_data = [
            {'title': '三体', 'author': '刘慈欣', 'category': '科幻奇幻', 'isbn': '9787536692930', 'publisher': '重庆出版社', 'publish_year': 2008, 'total_stock': 10, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=three%20body%20book%20cover%20sci%20fi&image_size=square_hd'},
            {'title': '活着', 'author': '余华', 'category': '文学小说', 'isbn': '9787506365437', 'publisher': '作家出版社', 'publish_year': 2012, 'total_stock': 8, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=chinese%20literature%20book%20cover%20artistic&image_size=square_hd'},
            {'title': '百年孤独', 'author': '加西亚·马尔克斯', 'category': '文学小说', 'isbn': '9787544253994', 'publisher': '南海出版公司', 'publish_year': 2011, 'total_stock': 6, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=one%20hundred%20years%20of%20solitude%20book%20cover&image_size=square_hd'},
            {'title': 'Python编程从入门到实践', 'author': 'Eric Matthes', 'category': '科技编程', 'isbn': '9787115428028', 'publisher': '人民邮电出版社', 'publish_year': 2016, 'total_stock': 12, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=python%20programming%20book%20cover%20blue&image_size=square_hd'},
            {'title': '人类简史', 'author': '尤瓦尔·赫拉利', 'category': '历史人文', 'isbn': '9787508647357', 'publisher': '中信出版社', 'publish_year': 2014, 'total_stock': 7, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=sapiens%20book%20cover%20history&image_size=square_hd'},
            {'title': '经济学原理', 'author': '曼昆', 'category': '经济管理', 'isbn': '9787301150894', 'publisher': '北京大学出版社', 'publish_year': 2009, 'total_stock': 5, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=economics%20textbook%20cover%20professional&image_size=square_hd'},
            {'title': '心理学与生活', 'author': '理查德·格里格', 'category': '心理学', 'isbn': '9787115111302', 'publisher': '人民邮电出版社', 'publish_year': 2003, 'total_stock': 6, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=psychology%20book%20cover%20mind%20brain&image_size=square_hd'},
            {'title': '小王子', 'author': '圣埃克苏佩里', 'category': '少儿读物', 'isbn': '9787020042494', 'publisher': '人民文学出版社', 'publish_year': 2003, 'total_stock': 15, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=little%20prince%20book%20cover%20stars%20planet&image_size=square_hd'},
            {'title': '红楼梦', 'author': '曹雪芹', 'category': '文学小说', 'isbn': '9787020002207', 'publisher': '人民文学出版社', 'publish_year': 1996, 'total_stock': 8, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=chinese%20classical%20novel%20book%20cover&image_size=square_hd'},
            {'title': 'JavaScript高级程序设计', 'author': 'Nicholas C. Zakas', 'category': '科技编程', 'isbn': '9787115275790', 'publisher': '人民邮电出版社', 'publish_year': 2012, 'total_stock': 9, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=javascript%20programming%20book%20cover%20code&image_size=square_hd'},
            {'title': '明朝那些事儿', 'author': '当年明月', 'category': '历史人文', 'isbn': '9787505722460', 'publisher': '中国友谊出版公司', 'publish_year': 2006, 'total_stock': 10, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=ming%20dynasty%20history%20book%20cover&image_size=square_hd'},
            {'title': '国富论', 'author': '亚当·斯密', 'category': '经济管理', 'isbn': '9787100011518', 'publisher': '商务印书馆', 'publish_year': 2015, 'total_stock': 4, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=wealth%20of%20nations%20book%20cover%20classic&image_size=square_hd'},
            {'title': '梦的解析', 'author': '弗洛伊德', 'category': '心理学', 'isbn': '9787511708654', 'publisher': '中央编译出版社', 'publish_year': 2011, 'total_stock': 5, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=dream%20interpretation%20book%20cover%20psychology&image_size=square_hd'},
            {'title': '哈利波特与魔法石', 'author': 'J.K.罗琳', 'category': '科幻奇幻', 'isbn': '9787020033430', 'publisher': '人民文学出版社', 'publish_year': 2000, 'total_stock': 12, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=harry%20potter%20book%20cover%20magic%20castle&image_size=square_hd'},
            {'title': '数据结构与算法分析', 'author': 'Mark Allen Weiss', 'category': '科技编程', 'isbn': '9787111379486', 'publisher': '机械工业出版社', 'publish_year': 2012, 'total_stock': 7, 'cover': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=data%20structures%20algorithm%20book%20cover&image_size=square_hd'},
        ]

        books = []
        for book_data in books_data:
            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults=book_data
            )
            if created:
                self.stdout.write(f'创建图书: {book.title}')
            books.append(book)

        for book in books:
            borrowing_count = BorrowRecord.objects.filter(
                book=book,
                status__in=['借阅中', '已逾期']
            ).count()
            book.available_stock = book.total_stock - borrowing_count
            book.save()
        self.stdout.write('已修复所有图书可借库存')

        if BorrowRecord.objects.filter(user=demo_user).exists():
            self.stdout.write(self.style.WARNING('已存在借阅记录，跳过生成'))
        else:
            BorrowRecord.objects.create(
                user=demo_user,
                book=books[0],
                borrow_date=date.today() - timedelta(days=5),
                due_date=date.today() + timedelta(days=25),
                status='借阅中'
            )
            books[0].available_stock -= 1
            books[0].save()
            self.stdout.write(f'创建借阅记录: {demo_user.username} 借阅 {books[0].title}')

            BorrowRecord.objects.create(
                user=demo_user,
                book=books[1],
                borrow_date=date.today() - timedelta(days=40),
                due_date=date.today() - timedelta(days=10),
                status='已逾期'
            )
            books[1].available_stock -= 1
            books[1].save()
            self.stdout.write(f'创建逾期记录: {demo_user.username} 借阅 {books[1].title} 已逾期')

            BorrowRecord.objects.create(
                user=demo_user,
                book=books[2],
                borrow_date=date.today() - timedelta(days=50),
                due_date=date.today() - timedelta(days=20),
                return_date=date.today() - timedelta(days=25),
                status='已归还'
            )
            self.stdout.write(f'创建归还记录: {demo_user.username} 归还 {books[2].title}')

            BorrowRecord.objects.create(
                user=demo_user,
                book=books[3],
                borrow_date=date.today() - timedelta(days=3),
                due_date=date.today() + timedelta(days=27),
                status='借阅中'
            )
            books[3].available_stock -= 1
            books[3].save()
            self.stdout.write(f'创建借阅记录: {demo_user.username} 借阅 {books[3].title}')

        self.stdout.write(self.style.SUCCESS('模拟数据生成完成！'))
