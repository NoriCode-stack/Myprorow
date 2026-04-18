@echo off
chcp 65001 >nul
echo ========================================
echo    图书馆管理系统 - 一键启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.9+
    pause
    exit /b 1
)
echo Python环境检测成功！

echo.
echo [2/4] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [警告] 依赖安装可能有问题，继续尝试运行...
) else (
    echo 依赖安装成功！
)

echo.
echo [3/4] 初始化数据库...
if not exist "db.sqlite3" (
    python manage.py migrate
    python init_data.py
) else (
    echo 数据库已存在，跳过初始化
)

echo.
echo [4/4] 启动开发服务器...
echo.
echo ========================================
echo    服务启动成功！
echo ========================================
echo.
echo    访问地址: http://127.0.0.1:8000/
echo.
echo    测试账号:
echo      管理员: admin / admin123456
echo      普通用户: user / user123456
echo.
echo    按 Ctrl+C 停止服务器
echo ========================================
echo.

python manage.py runserver
