@echo off
chcp 65001 >nul
echo 正在配置pip镜像源和安装Django...
echo.

:: 方法1：临时使用镜像源安装Django
echo [方法1] 使用清华源安装Django...
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Django==4.2.16 --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% equ 0 goto install_success

echo [方法2] 使用阿里云源安装Django...
pip install -i https://mirrors.aliyun.com/pypi/simple/ Django==4.2.16 --trusted-host mirrors.aliyun.com
if %errorlevel% equ 0 goto install_success

echo [方法3] 使用腾讯云源安装Django...
pip install -i https://mirrors.cloud.tencent.com/pypi/simple/ Django==4.2.16 --trusted-host mirrors.cloud.tencent.com
if %errorlevel% equ 0 goto install_success

echo [方法4] 使用豆瓣源安装Django...
pip install -i https://pypi.douban.com/simple/ Django==4.2.16 --trusted-host pypi.douban.com
if %errorlevel% equ 0 goto install_success

echo [方法5] 使用华为云源安装Django...
pip install -i https://mirrors.huaweicloud.com/repository/pypi/simple/ Django==4.2.16 --trusted-host mirrors.huaweicloud.com
if %errorlevel% equ 0 goto install_success

echo [ERROR] 所有镜像源都无法访问，请检查网络连接
goto end

:install_success
echo [SUCCESS] Django安装成功！
echo.

:: 验证Django安装
echo [INFO] 验证Django版本...
python -c "import django; print(f'Django version: {django.get_version()}')"
echo.

:: 配置永久镜像源
echo [INFO] 配置永久pip镜像源...
if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip"

:: 创建pip配置文件
echo [global] > "%APPDATA%\pip\pip.ini"
echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple >> "%APPDATA%\pip\pip.ini"
echo trusted-host = pypi.tuna.tsinghua.edu.cn >> "%APPDATA%\pip\pip.ini"
echo timeout = 120 >> "%APPDATA%\pip\pip.ini"
echo. >> "%APPDATA%\pip\pip.ini"
echo [install] >> "%APPDATA%\pip\pip.ini"
echo trusted-host = pypi.tuna.tsinghua.edu.cn >> "%APPDATA%\pip\pip.ini"

echo [SUCCESS] pip镜像源配置完成！
echo.

:: 进入Django项目目录
if exist "med_platform" (
    cd med_platform
    echo [INFO] 执行数据库迁移...
    python manage.py migrate
    echo.
    echo [INFO] 收集静态文件...
    python manage.py collectstatic --noinput
    echo.
    echo [SUCCESS] Django项目配置完成！
    echo.
    echo 使用以下命令启动开发服务器：
    echo   python manage.py runserver
    echo.
    echo 然后在浏览器中访问：http://127.0.0.1:8000
    echo.
    echo 要创建管理员账户，请运行：
    echo   python manage.py createsuperuser
) else (
    echo [WARNING] 未找到Django项目目录 med_platform
    echo 请确保已运行项目初始化脚本
)

:end
echo.
echo 按任意键继续...
pause >nul
