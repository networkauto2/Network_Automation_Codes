@echo off
:loop
D:\CAC\TB1\Tasks_auto\.venv\Scripts\python.exe findmac_defV1.1.py
echo -----------------------------------
echo
timeout /t 0
goto loop
