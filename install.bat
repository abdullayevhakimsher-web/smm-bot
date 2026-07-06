@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════╗
echo ║        SMM BOT O'RNATISH            ║
echo ╚══════════════════════════════════════╝
echo.

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] Python topilmadi! Python 3.10+ o'rnating.
    pause
    exit /b 1
)

echo [1/3] Virtual muhit yaratilmoqda...
python -m venv venv
if %errorlevel% neq 0 (
    echo [XATO] Virtual muhit yaratilamdi!
    pause
    exit /b 1
)

echo [2/3] Kutubxonalar o'rnatilmoqda...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo [3/3] .env fayli tekshirilmoqda...
if not exist .env (
    echo [XATO] .env fayli topilmadi!
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════╗
echo ║   ✅ O'RNATISH MUVAFFAQIYATLI!      ║
echo ╠══════════════════════════════════════╣
echo ║                                      ║
echo ║  Endi .env faylini oching va:        ║
echo ║  1. BOT_TOKEN ni kiriting            ║
echo ║  2. ADMIN_ID ni kiriting             ║
echo ║  3. Karta raqamlarini kiriting       ║
echo ║                                      ║
echo ║  Keyin: start_bot.bat ni ishga       ║
echo ║  tushiring!                          ║
echo ║                                      ║
echo ╚══════════════════════════════════════╝
echo.
pause
