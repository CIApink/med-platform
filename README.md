# MED 环境数据平台

## 项目简介

MED 环境健康数据平台（Metrics of Environmental Data）是一个基于Django的环境数据展示和管理平台，为用户提供专业的全球环境数据与专题资料。

## 功能特性

- 用户注册、登录、注销功能
- 环境数据展示和下载
- 数据可视化图表
- 响应式设计，支持移动端
- 基于Django的后端管理

## 项目结构

```
med-platform/
├── manage.py                 # Django管理脚本
├── requirements.txt          # Python依赖包
├── README.md                # 项目说明文档
├── fonts/                   # 字体文件
│   ├── MiSans-Normal.woff2
│   ├── MiSans-Semibold.woff2
│   └── ...
├── image/                   # 图片资源
│   ├── indeximage1.jpg
│   ├── indeximage2.jpg
│   └── ...
├── med_platform/            # Django项目配置
│   ├── __init__.py
│   ├── settings.py          # 项目设置
│   ├── urls.py              # 主URL配置
│   ├── wsgi.py              # WSGI配置
│   └── templates/           # 模板文件
│       ├── index.html
│       ├── sign_in.html
│       ├── sign_up.html
│       ├── data_download.html
│       └── ...
└── main_app/                # 主应用
    ├── __init__.py
    ├── admin.py             # 管理后台配置
    ├── apps.py              # 应用配置
    ├── models.py            # 数据模型
    ├── views.py             # 视图函数
    ├── urls.py              # 应用URL配置
    └── tests.py             # 测试用例
```

## 安装和运行

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv med_env

# 激活虚拟环境
# Windows:
med_env\Scripts\activate
# macOS/Linux:
source med_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000 查看网站

### 6. 访问管理后台（可选）

访问 http://127.0.0.1:8000/admin 进入管理后台

## 页面说明

### 前端页面

- **主页** (`/`) - 平台介绍和数据产品展示
- **登录** (`/sign-in/`) - 用户登录页面
- **注册** (`/sign-up/`) - 用户注册页面
- **数据下载** (`/data-download/`) - 数据浏览和下载
- **数据地图** (`/data-echart/`) - 数据可视化展示
- **用户状态** (`/user-status/`) - 用户信息查看

### 后端功能

- 用户认证和授权
- 数据模型管理
- 静态文件服务
- 管理后台界面

## 技术栈

- **后端**: Django 4.2+
- **前端**: HTML5, CSS3, JavaScript
- **数据库**: SQLite（开发环境）
- **字体**: MiSans
- **样式**: 响应式CSS设计

## 开发说明

### 添加新页面

1. 在 `main_app/views.py` 中添加视图函数
2. 在 `main_app/urls.py` 中添加URL路由
3. 在 `med_platform/templates/` 中创建模板文件

### 修改样式

- 所有页面使用统一的CSS变量定义颜色
- 采用MiSans字体系列
- 响应式设计适配移动端

### 数据库模型

- `UserProfile`: 用户扩展信息
- `DataDownload`: 数据下载记录

## 部署说明

### 生产环境配置

1. 修改 `settings.py` 中的配置：
   - 设置 `DEBUG = False`
   - 配置 `ALLOWED_HOSTS`
   - 使用生产数据库（PostgreSQL/MySQL）
   - 配置静态文件服务

2. 收集静态文件：
```bash
python manage.py collectstatic
```

3. 使用WSGI服务器（如Gunicorn）部署

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题，请通过以下方式联系：
- 项目GitHub仓库
- 邮箱：admin@med-platform.com
