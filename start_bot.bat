@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════╗
echo ║         SMM BOT ISHGA TUSHISH       ║
echo ╚══════════════════════════════════════╝
echo.

REM Virtual muhitni faollashtirish
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual muhit topilmadi. install.bat ni avval ishga tushiring.
)

echo [*] Bot ishga tushmoqda...
echo [*] To'xtatish uchun: Ctrl+C
echo.
python bot.py

pause
