@echo off
echo ========================================
echo    MED环境数据平台 - 离线启动脚本
echo ========================================
echo.

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在检查Django是否已安装...
python -c "import django; print('Django版本:', django.get_version())" 2>nul
if %errorlevel% neq 0 (
    echo Django未安装，正在使用国内镜像源安装...
    echo.
    echo [尝试1/5] 使用清华大学镜像源...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Django==4.2.16 --trusted-host pypi.tuna.tsinghua.edu.cn
    if %errorlevel% neq 0 (
        echo [尝试2/5] 使用阿里云镜像源...
        pip install -i https://mirrors.aliyun.com/pypi/simple/ Django==4.2.16 --trusted-host mirrors.aliyun.com
        if %errorlevel% neq 0 (
            echo [尝试3/5] 使用腾讯云镜像源...
            pip install -i https://mirrors.cloud.tencent.com/pypi/simple/ Django==4.2.16 --trusted-host mirrors.cloud.tencent.com
            if %errorlevel% neq 0 (
                echo [尝试4/5] 使用豆瓣镜像源...
                pip install -i https://pypi.douban.com/simple/ Django==4.2.16 --trusted-host pypi.douban.com
                if %errorlevel% neq 0 (
                    echo [尝试5/5] 使用华为云镜像源...
                    pip install -i https://mirrors.huaweicloud.com/repository/pypi/simple/ Django==4.2.16 --trusted-host mirrors.huaweicloud.com
                    if %errorlevel% neq 0 (
                        echo.
                        echo 所有镜像源安装都失败，请检查网络连接
                        echo 建议手动安装Django：
                        echo   方法1: 运行 quick_install_django.bat
                        echo   方法2: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Django==4.2.16
                        pause
                        exit /b 1
                    )
                )
            )
        )
    )
    echo [成功] Django安装完成！
)

echo.
echo Django已安装，继续项目初始化...
echo.

echo 创建数据库迁移文件...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo 警告：创建迁移文件失败，但会继续尝试运行
)

echo.
echo 执行数据库迁移...
python manage.py migrate
if %errorlevel% neq 0 (
    echo 警告：数据库迁移失败，但会继续尝试运行
)

echo.
echo ========================================
echo 启动Django开发服务器...
echo 访问地址：http://127.0.0.1:8000
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

:: 检查是否存在虚拟环境
if exist "med_env\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call med_env\Scripts\activate.bat
    python manage.py runserver
) else if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
    python manage.py runserver
) else (
    echo 未找到虚拟环境，使用系统Python...
    python manage.py runserver
)

echo.
echo 服务器已停止
pause
