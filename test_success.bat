@echo off
chcp 65001 > nul
echo Запуск эмулятора со всеми параметрами...
py src/emulatur.py --vfs ./archive.zip --script ./start.txt
pause