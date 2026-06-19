@echo off
:: Set UTF-8 BEFORE Python starts — fixes Bengali/Hindi charmap errors on Windows
set PYTHONUTF8=1
chcp 65001 >nul 2>&1

cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app.py
