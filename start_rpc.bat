@echo off
:: Проверка наличия прав администратора
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    :: Если прав нет, перезапускаем сами себя от имени администратора
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~dpnx0\"' -Verb RunAs"
    exit /b
)

:run
:: Переходим в директорию, где находится этот батник
cd /d "%~dp0"

:: Активируем виртуальное окружение
call .venv\Scripts\activate.bat

:: Запускаем скрипт (используем pythonw, чтобы скрыть лишнее черное окно консоли, если нужно)
python main.py