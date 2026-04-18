from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from books.models import Category, Book, UserProfile


class Command(BaseCommand):
    help = '初始化图书借阅系统的测试数据'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始初始化数据...')

        # 创建分类
        categories_data = [
            {'name': '文学小说', 'description': '各类文学小说作品'},
            {'name': '计算机科学', 'description': '编程、算法、计算机技术'},
            {'name': '历史人文', 'description': '历史、文化、人文社科'},
            {'name': '自然科学', 'description': '物理、化学、生物等自然科学'},
            {'name': '经济管理', 'description': '经济、管理、商业'},
            {'name': '艺术设计', 'description': '艺术、设计、美学'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'创建分类: {cat.name}')

        # 创建测试用户
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            UserProfile.objects.get_or_create(user=admin_user, defaults={'is_vip': True})
            self.stdout.write('创建管理员用户: admin / admin123')

        if not User.objects.filter(username='user').exists():
            normal_user = User.objects.create_user(
                username='user',
                email='user@example.com',
                password='user123'
            )
            UserProfile.objects.get_or_create(user=normal_user)
            self.stdout.write('创建普通用户: user / user123')

        # 创建图书数据
        books_data = [
            {
                'title': '三体',
                'author': '刘慈欣',
                'isbn': '9787536692930',
                'publisher': '重庆出版社',
                'category': '文学小说',
                'total_copies': 5,
                'description': '文化大革命如火如荼进行的同时，军方探寻外星文明的绝秘计划"红岸工程"取得了突破性进展。但在按下发射键的那一刻，历经劫难的叶文洁没有意识到，她彻底改变了人类的命运。'
            },
            {
                'title': '百年孤独',
                'author': '加西亚·马尔克斯',
                'isbn': '9787544253994',
                'publisher': '南海出版公司',
                'category': '文学小说',
                'total_copies': 3,
                'description': '《百年孤独》是魔幻现实主义文学的代表作，描写了布恩迪亚家族七代人的传奇故事，以及加勒比海沿岸小镇马孔多的百年兴衰。'
            },
            {
                'title': 'Python编程：从入门到实践',
                'author': '埃里克·马瑟斯',
                'isbn': '9787115428028',
                'publisher': '人民邮电出版社',
                'category': '计算机科学',
                'total_copies': 8,
                'description': '本书是一本针对所有层次的Python读者而作的Python入门书。全书分两部分：第一部分介绍用Python编程所必须了解的基本概念。'
            },
            {
                'title': '算法导论',
                'author': 'Thomas H. Cormen',
                'isbn': '9787111407010',
                'publisher': '机械工业出版社',
                'category': '计算机科学',
                'total_copies': 4,
                'description': '《算法导论》自第一版出版以来，已经成为世界范围内广泛使用的大学教材和专业人员的标准参考书。'
            },
            {
                'title': '人类简史',
                'author': '尤瓦尔·赫拉利',
                'isbn': '9787508647357',
                'publisher': '中信出版社',
                'category': '历史人文',
                'total_copies': 6,
                'description': '十万年前，地球上至少有六种不同的人，但今日，世界舞台为什么只剩下了我们自己？'
            },
            {
                'title': '明朝那些事儿',
                'author': '当年明月',
                'isbn': '9787505722460',
                'publisher': '中国友谊出版公司',
                'category': '历史人文',
                'total_copies': 5,
                'description': '这篇文主要讲述的是从1344年到1644年这三百年间关于明朝的一些事情，以史料为基础，以年代和具体人物为主线。'
            },
            {
                'title': '时间简史',
                'author': '史蒂芬·霍金',
                'isbn': '9787535732309',
                'publisher': '湖南科学技术出版社',
                'category': '自然科学',
                'total_copies': 4,
                'description': '《时间简史》是英国物理学家史蒂芬·霍金创作的科学著作，讲述了关于宇宙本性的最前沿知识。'
            },
            {
                'title': '物种起源',
                'author': '查尔斯·达尔文',
                'isbn': '9787100012977',
                'publisher': '商务印书馆',
                'category': '自然科学',
                'total_copies': 3,
                'description': '《物种起源》是达尔文论述生物进化的重要著作，出版于1859年11月24日。'
            },
            {
                'title': '经济学原理',
                'author': '曼昆',
                'isbn': '9787301256909',
                'publisher': '北京大学出版社',
                'category': '经济管理',
                'total_copies': 6,
                'description': '曼昆的《经济学原理》是世界上最流行的初级经济学教材，也被众多院校列为经济类专业考研参考书目。'
            },
            {
                'title': '从0到1',
                'author': '彼得·蒂尔',
                'isbn': '9787508646718',
                'publisher': '中信出版社',
                'category': '经济管理',
                'total_copies': 5,
                'description': '硅谷创投教父、PayPal创始人彼得·蒂尔作品，斯坦福大学改变未来的一堂课，为世界创造价值的商业哲学。'
            },
            {
                'title': '设计心理学',
                'author': '唐纳德·诺曼',
                'isbn': '9787508645353',
                'publisher': '中信出版社',
                'category': '艺术设计',
                'total_copies': 4,
                'description': '诺曼博士用诙谐的语言讲述了许多我们日常生活中常常会遇到的挫折和危险，帮我们找到了这些问题的症结。'
            },
            {
                'title': '艺术的故事',
                'author': '贡布里希',
                'isbn': '9787547413357',
                'publisher': '广西美术出版社',
                'category': '艺术设计',
                'total_copies': 3,
                'description': '概括地叙述了从最早的洞窟绘画到当今的实验艺术的发展历程，以阐明艺术史是"各种传统不断迂回、不断改变的历史"。'
            },
            {
                'title': '活着',
                'author': '余华',
                'isbn': '9787506365437',
                'publisher': '作家出版社',
                'category': '文学小说',
                'total_copies': 7,
                'description': '《活着》讲述了农村人福贵悲惨的人生遭遇。福贵本是个阔少爷，可他嗜赌如命，终于赌光了家业，一贫如洗。'
            },
            {
                'title': '深入理解计算机系统',
                'author': 'Randal E. Bryant',
                'isbn': '9787111544937',
                'publisher': '机械工业出版社',
                'category': '计算机科学',
                'total_copies': 4,
                'description': '本书主要介绍了计算机系统的基本概念，包括最底层的内存中的数据表示、流水线指令的构成、虚拟存储器等。'
            },
            {
                'title': '万历十五年',
                'author': '黄仁宇',
                'isbn': '9787101052039',
                'publisher': '中华书局',
                'category': '历史人文',
                'total_copies': 5,
                'description': '万历十五年，亦即公元1587年，在西欧历史上为西班牙舰队全部出动征英的前一年；而在中国，这平平淡淡的一年中，发生了若干为历史学家所易于忽视的事件。'
            },
            {
                'title': '自私的基因',
                'author': '理查德·道金斯',
                'isbn': '9787508644776',
                'publisher': '中信出版社',
                'category': '自然科学',
                'total_copies': 4,
                'description': '道金斯在《自私的基因》中的突破性贡献在于，把根据自然选择的社会学说的这一重要部分，用简明通俗的形式，妙趣横生的语言介绍给大家。'
            },
            {
                'title': '穷查理宝典',
                'author': '查理·芒格',
                'isbn': '9787508664316',
                'publisher': '中信出版社',
                'category': '经济管理',
                'total_copies': 5,
                'description': '《穷查理宝典》完整收录了查理·芒格的个人传记与投资哲学，以及过去20年来芒格主要的公开演讲和媒体访谈。'
            },
            {
                'title': '写给大家看的设计书',
                'author': 'Robin Williams',
                'isbn': '9787115244925',
                'publisher': '人民邮电出版社',
                'category': '艺术设计',
                'total_copies': 6,
                'description': '本书出自一位世界级设计师之手。将优秀设计的秘诀归纳为对比、重复、对齐和亲密性四条基本原则。'
            },
        ]

        created_count = 0
        for book_data in books_data:
            if not Book.objects.filter(isbn=book_data['isbn']).exists():
                category_name = book_data.pop('category')
                category = categories.get(category_name)
                
                Book.objects.create(
                    **book_data,
                    category=category,
                    available_copies=book_data['total_copies']
                )
                created_count += 1
                self.stdout.write(f'创建图书: {book_data["title"]}')

        self.stdout.write(self.style.SUCCESS(
            f'\n数据初始化完成！\n'
            f'- 创建了 {len(categories)} 个分类\n'
            f'- 创建了 {created_count} 本图书\n'
            f'- 创建了 2 个测试用户（admin/admin123, user/user123）'
        ))
