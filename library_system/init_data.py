"""
初始化脚本 - 创建模拟数据
运行方式: python init_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from library.models import Category, Book, BorrowRecord, UserProfile


def create_categories():
    categories_data = [
        ('文学小说', '包括中外文学名著、现代小说、诗歌散文等'),
        ('科学技术', '计算机科学、工程技术、自然科学等'),
        ('历史传记', '历史研究、人物传记、历史小说等'),
        ('经济管理', '经济学、管理学、金融投资等'),
        ('哲学心理', '哲学思想、心理学、宗教信仰等'),
        ('艺术设计', '美术设计、音乐舞蹈、影视戏剧等'),
        ('教育学习', '教材教辅、考试用书、学习方法等'),
        ('生活健康', '养生保健、美食烹饪、旅游出行等'),
        ('社会科学', '社会学、政治学、法学等'),
        ('少儿读物', '儿童文学、绘本、科普读物等'),
    ]
    
    categories = []
    for name, desc in categories_data:
        cat, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        categories.append(cat)
        if created:
            print(f'  创建分类: {name}')
    return categories


def create_books(categories):
    books_data = [
        {
            'title': '百年孤独',
            'author': '加西亚·马尔克斯',
            'isbn': '9787544253994',
            'category': '文学小说',
            'publisher': '南海出版公司',
            'publish_date': '2011-06-01',
            'description': '《百年孤独》是魔幻现实主义文学的代表作，描写了布恩迪亚家族七代人的传奇故事，以及加勒比海沿岸小镇马孔多的百年兴衰，反映了拉丁美洲一个世纪以来风云变幻的历史。',
            'total_copies': 5,
            'available_copies': 3,
            'location': 'A区-1层-文学书架',
        },
        {
            'title': '活着',
            'author': '余华',
            'isbn': '9787506365437',
            'category': '文学小说',
            'publisher': '作家出版社',
            'publish_date': '2012-08-01',
            'description': '《活着》讲述了农村人福贵悲惨的人生遭遇。福贵本是个阔少爷，可他嗜赌如命，终于赌光了家业，一贫如洗。他的亲人相继离他而去，最后只剩下一头老牛与他相依为命。',
            'total_copies': 8,
            'available_copies': 5,
            'location': 'A区-1层-文学书架',
        },
        {
            'title': 'Python编程：从入门到实践',
            'author': 'Eric Matthes',
            'isbn': '9787115428028',
            'category': '科学技术',
            'publisher': '人民邮电出版社',
            'publish_date': '2016-07-01',
            'description': '本书是一本针对所有层次Python读者而作的Python入门书。全书分两部分：第一部分介绍用Python编程所必须了解的基本概念；第二部分将理论付诸实践，讲解如何开发三个项目。',
            'total_copies': 10,
            'available_copies': 6,
            'location': 'B区-2层-计算机书架',
        },
        {
            'title': '深入理解计算机系统',
            'author': 'Randal E. Bryant',
            'isbn': '9787111544937',
            'category': '科学技术',
            'publisher': '机械工业出版社',
            'publish_date': '2016-07-01',
            'description': '本书从程序员的视角详细阐述计算机系统的本质概念，并展示这些概念如何实实在在地影响应用程序的正确性、性能和实用性。',
            'total_copies': 6,
            'available_copies': 4,
            'location': 'B区-2层-计算机书架',
        },
        {
            'title': '人类简史',
            'author': '尤瓦尔·赫拉利',
            'isbn': '9787508647357',
            'category': '历史传记',
            'publisher': '中信出版社',
            'publish_date': '2014-11-01',
            'description': '《人类简史》是以色列新锐历史学家尤瓦尔·赫拉利的一部重磅作品。从十万年前有生命迹象开始到21世纪资本、科技交织的人类发展史。',
            'total_copies': 7,
            'available_copies': 4,
            'location': 'C区-1层-历史书架',
        },
        {
            'title': '明朝那些事儿',
            'author': '当年明月',
            'isbn': '9787801726531',
            'category': '历史传记',
            'publisher': '中国海关出版社',
            'publish_date': '2006-03-01',
            'description': '《明朝那些事儿》主要讲述的是从1344年到1644年这三百年间关于明朝的一些故事。以史料为基础，以年代和具体人物为主线，并加入了小说的笔法，语言幽默风趣。',
            'total_copies': 12,
            'available_copies': 8,
            'location': 'C区-1层-历史书架',
        },
        {
            'title': '经济学原理',
            'author': '曼昆',
            'isbn': '9787301171462',
            'category': '经济管理',
            'publisher': '北京大学出版社',
            'publish_date': '2012-07-01',
            'description': '《经济学原理》是世界上最流行的经济学教科书。本书用通俗的语言解释了经济学的基本原理，是经济学入门的必读之作。',
            'total_copies': 6,
            'available_copies': 3,
            'location': 'D区-1层-经济书架',
        },
        {
            'title': '穷爸爸富爸爸',
            'author': '罗伯特·清崎',
            'isbn': '9787504450304',
            'category': '经济管理',
            'publisher': '电子工业出版社',
            'publish_date': '2011-04-01',
            'description': '本书通过讲述作者的亲身经历，揭示了富人如何教育孩子理财，以及穷人如何教育孩子理财的差异。是一本关于财商教育的经典之作。',
            'total_copies': 8,
            'available_copies': 5,
            'location': 'D区-1层-经济书架',
        },
        {
            'title': '思考，快与慢',
            'author': '丹尼尔·卡尼曼',
            'isbn': '9787508633558',
            'category': '哲学心理',
            'publisher': '中信出版社',
            'publish_date': '2012-07-01',
            'description': '在书中，卡尼曼会带领我们体验一次思维的终极之旅。他认为，我们的大脑有快与慢两种作决定的方式。',
            'total_copies': 5,
            'available_copies': 2,
            'location': 'E区-1层-心理书架',
        },
        {
            'title': '苏菲的世界',
            'author': '乔斯坦·贾德',
            'isbn': '9787506394864',
            'category': '哲学心理',
            'publisher': '作家出版社',
            'publish_date': '2017-08-01',
            'description': '《苏菲的世界》是挪威作家乔斯坦·贾德创作的一本关于西方哲学史的长篇小说，它以小说的形式，通过一名哲学导师向一个叫苏菲的女孩传授哲学知识的经过，揭示了西方哲学史发展的历程。',
            'total_copies': 6,
            'available_copies': 4,
            'location': 'E区-1层-哲学书架',
        },
        {
            'title': '设计中的设计',
            'author': '原研哉',
            'isbn': '9787563366298',
            'category': '艺术设计',
            'publisher': '广西师范大学出版社',
            'publish_date': '2010-09-01',
            'description': '设计到底是什么？作为一名从业二十余年并且具有世界影响的设计师，原研哉对自己提出了这样一个问题。为了给出自己的答案，他走了那么长的路，做了那么多的探索。',
            'total_copies': 4,
            'available_copies': 2,
            'location': 'F区-2层-设计书架',
        },
        {
            'title': '艺术的故事',
            'author': '贡布里希',
            'isbn': '9787563333842',
            'category': '艺术设计',
            'publisher': '广西美术出版社',
            'publish_date': '2008-04-01',
            'description': '《艺术的故事》概括地叙述了从最早的洞窟绘画到当今的实验艺术的发展历程，以阐明艺术史是各种传统不断迂回、不断改变的历史，每一件作品在这历史中都既回顾过去又导向未来。',
            'total_copies': 5,
            'available_copies': 3,
            'location': 'F区-2层-艺术书架',
        },
        {
            'title': '如何阅读一本书',
            'author': '莫提默·J. 艾德勒',
            'isbn': '9787100040945',
            'category': '教育学习',
            'publisher': '商务印书馆',
            'publish_date': '2004-01-01',
            'description': '每本书的封面之下都有一套自己的骨架，作为一个分析阅读的读者，责任就是要找出这个骨架。一本书出现在面前时，肌肉包着骨头，衣服包裹着肌肉，可说是盛装而来。',
            'total_copies': 10,
            'available_copies': 7,
            'location': 'G区-1层-学习书架',
        },
        {
            'title': '自控力',
            'author': '凯利·麦格尼格尔',
            'isbn': '9787512505039',
            'category': '生活健康',
            'publisher': '文化发展出版社',
            'publish_date': '2012-08-01',
            'description': '作为一名健康心理学家，凯利·麦格尼格尔博士的工作就是帮助人们管理压力，并在生活中做出积极的改变。本书为读者提供了清晰的框架，讲述了什么是自控力，自控力如何发生作用，以及为何自控力如此重要。',
            'total_copies': 8,
            'available_copies': 5,
            'location': 'H区-1层-健康书架',
        },
        {
            'title': '小王子',
            'author': '安托万·德·圣-埃克苏佩里',
            'isbn': '9787020042494',
            'category': '少儿读物',
            'publisher': '人民文学出版社',
            'publish_date': '2003-08-01',
            'description': '小王子是一个超凡脱俗的仙童，住在一颗只比他大一丁点儿的小行星上。陪伴他的是一朵他非常喜爱的小玫瑰花。但玫瑰花的虚荣心伤害了小王子对她的感情。',
            'total_copies': 15,
            'available_copies': 10,
            'location': 'I区-1层-少儿书架',
        },
    ]
    
    books = []
    for data in books_data:
        category_name = data.pop('category')
        category = Category.objects.get(name=category_name)
        book, created = Book.objects.get_or_create(
            isbn=data['isbn'],
            defaults={**data, 'category': category}
        )
        books.append(book)
        if created:
            print(f'  创建图书: {data["title"]}')
    return books


def create_users():
    users_data = [
        {'username': 'admin', 'email': 'admin@library.com', 'password': 'admin123456', 'is_staff': True, 'is_superuser': True},
        {'username': 'user', 'email': 'user@library.com', 'password': 'user123456', 'is_staff': False, 'is_superuser': False},
        {'username': '张三', 'email': 'zhangsan@library.com', 'password': 'zhang123456', 'is_staff': False, 'is_superuser': False},
        {'username': '李四', 'email': 'lisi@library.com', 'password': 'lisi123456', 'is_staff': False, 'is_superuser': False},
        {'username': '王五', 'email': 'wangwu@library.com', 'password': 'wangwu123456', 'is_staff': False, 'is_superuser': False},
    ]
    
    users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'is_staff': data['is_staff'],
                'is_superuser': data['is_superuser'],
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=f'138{user.id:08d}',
                student_id=f'2024{user.id:04d}',
                department='图书馆'
            )
            print(f'  创建用户: {data["username"]}')
        users.append(user)
    return users


def create_borrow_records(users, books):
    if len(users) < 3 or len(books) < 5:
        return
    
    records_data = [
        {'user': users[1], 'book': books[0], 'days_ago': 5, 'due_days': 25},
        {'user': users[1], 'book': books[2], 'days_ago': 10, 'due_days': 20},
        {'user': users[2], 'book': books[1], 'days_ago': 35, 'due_days': -5},
        {'user': users[2], 'book': books[4], 'days_ago': 20, 'due_days': 10},
        {'user': users[3], 'book': books[3], 'days_ago': 15, 'due_days': 15},
        {'user': users[3], 'book': books[5], 'days_ago': 40, 'due_days': -10, 'returned': True},
        {'user': users[4], 'book': books[6], 'days_ago': 8, 'due_days': 22},
        {'user': users[4], 'book': books[8], 'days_ago': 50, 'due_days': -20, 'returned': True},
    ]
    
    for data in records_data:
        borrow_date = timezone.now() - timedelta(days=data['days_ago'])
        due_date = timezone.now() + timedelta(days=data['due_days'])
        
        record, created = BorrowRecord.objects.get_or_create(
            user=data['user'],
            book=data['book'],
            borrow_date=borrow_date,
            defaults={
                'due_date': due_date,
                'status': 'returned' if data.get('returned') else 'borrowed',
            }
        )
        
        if created:
            if data.get('returned'):
                record.return_date = borrow_date + timedelta(days=30)
                record.status = 'returned'
                record.save()
            print(f'  创建借阅记录: {data["user"].username} - {data["book"].title}')


def main():
    print('=' * 50)
    print('开始初始化模拟数据...')
    print('=' * 50)
    
    print('\n[1/4] 创建图书分类...')
    categories = create_categories()
    
    print('\n[2/4] 创建图书...')
    books = create_books(categories)
    
    print('\n[3/4] 创建用户...')
    users = create_users()
    
    print('\n[4/4] 创建借阅记录...')
    create_borrow_records(users, books)
    
    print('\n' + '=' * 50)
    print('初始化完成！')
    print('=' * 50)
    print('\n测试账号信息：')
    print('  管理员: admin / admin123456')
    print('  普通用户: user / user123456')
    print('\n运行服务器: python manage.py runserver')
    print('访问地址: http://127.0.0.1:8000/')


if __name__ == '__main__':
    main()
