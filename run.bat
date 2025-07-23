@echo off
echo 正在启动MED环境数据平台...
echo.

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 安装依赖包...
pip install Django==4.2.16

echo.
echo 执行数据库迁移...
python manage.py makemigrations
python manage.py migrate

echo.
echo 启动开发服务器...
echo 服务器将在 http://127.0.0.1:8000 运行
echo 按 Ctrl+C 停止服务器
echo.
python manage.py runserver
