@echo off
chcp 65001 >nul
if "%~2"=="" (
    echo Usage: calistir.bat baslangic.json komutlar.jsonl
    exit /b 1
)

uv run yazilim-lab-project "%~1" "%~2"
