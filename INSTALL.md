# MED环境数据平台 - 快速安装指南

## 🚀 快速开始

### 第一步：环境准备
确保您的系统已安装Python 3.8或更高版本：
```bash
python --version
```

### 第二步：项目设置

1. **创建虚拟环境**
```bash
cd e:\med-platform
python -m venv med_env
```

2. **激活虚拟环境**
```bash
# Windows
med_env\Scripts\activate

# macOS/Linux
source med_env/bin/activate
```

3. **安装Django**
```bash
pip install Django==4.2.16
```

### 第三步：数据库设置

1. **创建数据库迁移**
```bash
python manage.py makemigrations
```

2. **执行数据库迁移**
```bash
python manage.py migrate
```

3. **创建超级用户（可选）**
```bash
python manage.py createsuperuser
```

### 第四步：启动服务器

```bash
python manage.py runserver
```

服务器启动后，在浏览器中访问：http://127.0.0.1:8000

## 🎯 功能页面

- **主页**: http://127.0.0.1:8000/
- **用户登录**: http://127.0.0.1:8000/sign-in/
- **用户注册**: http://127.0.0.1:8000/sign-up/
- **数据下载**: http://127.0.0.1:8000/data-download/
- **数据地图**: http://127.0.0.1:8000/data-echart/
- **管理后台**: http://127.0.0.1:8000/admin/

## 🛠️ 故障排除

### 问题1：ModuleNotFoundError: No module named 'django'
**解决方案**: 确保已激活虚拟环境并安装了Django
```bash
med_env\Scripts\activate
pip install Django==4.2.16
```

### 问题2：静态文件无法加载
**解决方案**: 确保在开发模式下，Django会自动处理静态文件

### 问题3：数据库错误
**解决方案**: 运行数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📁 项目结构说明

```
med-platform/
├── manage.py              # Django命令行工具
├── med_platform/          # 项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py           # URL路由
│   └── templates/        # HTML模板
└── main_app/             # 主要应用
    ├── models.py         # 数据模型
    ├── views.py          # 视图函数
    └── urls.py           # 应用URL
```

## 🎨 页面特性

✅ 响应式设计，支持移动端
✅ MiSans字体优化显示
✅ 用户认证系统
✅ 数据展示界面
✅ 管理后台功能

## 📊 下一步开发

1. 完善数据模型
2. 添加数据上传功能
3. 集成数据可视化库
4. 添加API接口
5. 部署到生产环境

## 📞 技术支持

如遇到问题，请检查：
1. Python版本是否正确
2. 虚拟环境是否激活
3. Django是否正确安装
4. 数据库迁移是否完成

祝您使用愉快！🎉
