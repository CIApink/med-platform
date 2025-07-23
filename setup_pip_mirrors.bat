@echo off
chcp 65001 >nul
echo 正在配置pip使用清华镜像源...
echo.

:: 创建pip配置目录（如果不存在）
if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip"

:: 复制pip配置文件到用户配置目录
copy /Y "pip.conf" "%APPDATA%\pip\pip.ini" >nul

:: 验证配置
echo [INFO] pip配置文件已更新，当前镜像源配置：
echo   - 清华大学镜像：https://pypi.tuna.tsinghua.edu.cn/simple
echo   - 阿里云镜像：https://mirrors.aliyun.com/pypi/simple/
echo   - 腾讯云镜像：https://mirrors.cloud.tencent.com/pypi/simple/
echo.

:: 测试pip配置
echo [INFO] 测试pip配置...
pip config list
echo.

:: 升级pip
echo [INFO] 升级pip...
python -m pip install --upgrade pip
echo.

:: 安装Django
echo [INFO] 开始安装Django 4.2.16...
pip install Django==4.2.16
if %errorlevel% neq 0 (
    echo [ERROR] Django安装失败，尝试备用镜像源...
    pip install -i https://mirrors.aliyun.com/pypi/simple/ Django==4.2.16
    if %errorlevel% neq 0 (
        echo [ERROR] 使用阿里云镜像也安装失败，尝试腾讯云镜像...
        pip install -i https://mirrors.cloud.tencent.com/pypi/simple/ Django==4.2.16
    )
)

:: 验证Django安装
echo.
echo [INFO] 验证Django安装...
python -c "import django; print(f'Django version: {django.get_version()}')"
if %errorlevel% equ 0 (
    echo [SUCCESS] Django安装成功！
    echo.
    echo [INFO] 初始化Django项目...
    cd med_platform
    python manage.py migrate
    echo.
    echo [INFO] 创建超级用户...
    echo 请输入管理员用户信息：
    python manage.py createsuperuser
    echo.
    echo [SUCCESS] 项目配置完成！
    echo.
    echo 使用以下命令启动开发服务器：
    echo   cd med_platform
    echo   python manage.py runserver
    echo.
    echo 然后在浏览器中访问：http://127.0.0.1:8000
) else (
    echo [ERROR] Django安装验证失败
)

echo.
echo 按任意键继续...
pause >nul
