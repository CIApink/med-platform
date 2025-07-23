#!/usr/bin/env python3
"""
MED环境数据平台项目结构验证脚本
"""

import os
import sys

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (文件不存在)")
        return False

def check_directory_exists(dirpath, description):
    """检查目录是否存在"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} (目录不存在)")
        return False

def main():
    print("🚀 MED环境数据平台项目结构检查")
    print("=" * 50)
    
    # 检查项目根目录文件
    print("\n📁 项目根目录文件检查:")
    root_files = [
        ("manage.py", "Django管理脚本"),
        ("requirements.txt", "依赖包列表"),
        ("README.md", "项目说明文档"),
        ("run.bat", "Windows运行脚本"),
    ]
    
    for filepath, desc in root_files:
        check_file_exists(filepath, desc)
    
    # 检查目录结构
    print("\n📂 目录结构检查:")
    directories = [
        ("med_platform", "Django项目目录"),
        ("med_platform/templates", "模板文件目录"),
        ("main_app", "主应用目录"),
        ("fonts", "字体文件目录"),
        ("image", "图片资源目录"),
    ]
    
    for dirpath, desc in directories:
        check_directory_exists(dirpath, desc)
    
    # 检查Django项目文件
    print("\n⚙️ Django项目文件检查:")
    django_files = [
        ("med_platform/__init__.py", "项目初始化文件"),
        ("med_platform/settings.py", "项目设置文件"),
        ("med_platform/urls.py", "主URL配置"),
        ("med_platform/wsgi.py", "WSGI配置"),
    ]
    
    for filepath, desc in django_files:
        check_file_exists(filepath, desc)
    
    # 检查应用文件
    print("\n📱 主应用文件检查:")
    app_files = [
        ("main_app/__init__.py", "应用初始化文件"),
        ("main_app/models.py", "数据模型"),
        ("main_app/views.py", "视图函数"),
        ("main_app/urls.py", "应用URL配置"),
        ("main_app/admin.py", "管理后台配置"),
        ("main_app/apps.py", "应用配置"),
        ("main_app/tests.py", "测试用例"),
    ]
    
    for filepath, desc in app_files:
        check_file_exists(filepath, desc)
    
    # 检查模板文件
    print("\n🎨 模板文件检查:")
    template_files = [
        ("med_platform/templates/index.html", "主页模板"),
        ("med_platform/templates/sign_in.html", "登录页模板"),
        ("med_platform/templates/sign_up.html", "注册页模板"),
        ("med_platform/templates/data_download.html", "数据下载模板"),
        ("med_platform/templates/data_echart.html", "数据图表模板"),
        ("med_platform/templates/user_status.html", "用户状态模板"),
    ]
    
    for filepath, desc in template_files:
        check_file_exists(filepath, desc)
    
    # 检查静态资源
    print("\n🎯 静态资源检查:")
    
    # 检查字体文件
    font_files = [
        "MiSans-Normal.woff2",
        "MiSans-Semibold.woff2",
        "MiSans-Medium.woff2",
    ]
    
    for font_file in font_files:
        check_file_exists(f"fonts/{font_file}", f"字体文件 {font_file}")
    
    # 检查图片文件
    if os.path.exists("image"):
        image_files = [f for f in os.listdir("image") if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"📸 找到 {len(image_files)} 个图片文件")
        for img_file in image_files[:5]:  # 只显示前5个
            print(f"   - {img_file}")
        if len(image_files) > 5:
            print(f"   ... 还有 {len(image_files) - 5} 个文件")
    
    print("\n" + "=" * 50)
    print("✨ 项目结构检查完成！")
    print("\n📋 下一步操作:")
    print("1. 安装Python 3.8+")
    print("2. 创建虚拟环境: python -m venv med_env")
    print("3. 激活虚拟环境: med_env\\Scripts\\activate (Windows)")
    print("4. 安装Django: pip install Django==4.2.16")
    print("5. 运行迁移: python manage.py migrate")
    print("6. 启动服务器: python manage.py runserver")
    print("7. 访问: http://127.0.0.1:8000")

if __name__ == "__main__":
    main()
