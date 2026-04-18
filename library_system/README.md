# 图书借阅管理系统

一个基于 Django + Bootstrap 5 的全栈 Web 图书借阅管理应用。

## 功能特性

### 用户功能
- **图书浏览与检索**：支持按书名、作者、ISBN 搜索，分类筛选
- **图书详情**：查看图书详细信息、借阅状态
- **借阅与归还**：在线借阅图书，一键归还
- **个人中心**：查看借阅历史、当前借阅、逾期提醒

### 管理功能
- **仪表盘**：统计图书、用户、借阅数据
- **图书管理**：添加、编辑、删除图书，库存管理
- **用户管理**：查看用户信息、借阅情况
- **借阅记录**：查看所有借阅记录，筛选状态

## 技术栈

- **后端**：Django 6.0+
- **前端**：Bootstrap 5 + Bootstrap Icons
- **数据库**：SQLite（默认，可更换为 MySQL/PostgreSQL）
- **模板引擎**：Django Template Language

## 快速开始

### 1. 安装依赖

```bash
pip install django
```

### 2. 数据库迁移

```bash
python manage.py migrate
```

### 3. 初始化测试数据

```bash
python manage.py init_data
```

### 4. 启动服务器

```bash
python manage.py runserver
```

### 5. 访问应用

打开浏览器访问：http://127.0.0.1:8000

## 测试账号

| 账号类型 | 用户名 | 密码 |
|---------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 项目结构

```
library_system/
├── library_system/          # 项目配置
│   ├── settings.py          # 项目设置
│   ├── urls.py              # URL 路由
│   └── ...
├── books/                   # 图书应用
│   ├── models.py            # 数据模型
│   ├── views.py             # 视图函数
│   ├── admin.py             # 后台管理
│   ├── management/          # 管理命令
│   │   └── commands/
│   │       └── init_data.py # 初始化数据
│   └── ...
├── templates/               # HTML 模板
│   ├── base.html            # 基础模板
│   └── books/               # 应用模板
│       ├── home.html
│       ├── book_list.html
│       ├── book_detail.html
│       ├── my_borrows.html
│       ├── login.html
│       ├── register.html
│       └── admin/           # 后台模板
├── static/                  # 静态文件
│   ├── css/
│   └── js/
└── manage.py                # 管理脚本
```

## 数据模型

### Category（图书分类）
- name: 分类名称
- description: 分类描述

### Book（图书）
- title: 书名
- author: 作者
- isbn: ISBN
- publisher: 出版社
- category: 分类（外键）
- description: 简介
- cover_image: 封面图片
- total_copies: 总库存
- available_copies: 可借数量
- status: 状态（可借阅/已借出/维护中）

### BorrowRecord（借阅记录）
- user: 用户（外键）
- book: 图书（外键）
- borrow_date: 借阅日期
- due_date: 应还日期
- return_date: 归还日期
- status: 状态（借阅中/已归还/已逾期）
- fine_amount: 罚款金额

### UserProfile（用户资料）
- user: 用户（一对一）
- phone: 手机号
- max_books: 最大借阅数量
- is_vip: VIP 标识

## 界面预览

- **首页**：展示统计数据、新书上架、热门借阅
- **图书列表**：网格展示、搜索筛选、分页
- **图书详情**：详细信息、借阅按钮
- **我的借阅**：当前借阅、历史记录、逾期提醒
- **后台管理**：仪表盘、图书/用户/借阅管理

## 响应式设计

应用采用 Bootstrap 5 响应式布局，支持：
- 桌面端（>992px）
- 平板端（768px-992px）
- 移动端（<768px）

## 许可证

MIT License
