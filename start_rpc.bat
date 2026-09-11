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
title YandexMusicRPC_Daemon
cd /d "%~dp0"

:: Активируем виртуальное окружение
call .venv\Scripts\activate.bat

:: Запускаем скрипт
python main.py