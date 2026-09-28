@echo off
chcp 65001 > nul
echo Запуск скрипта, содержащего неверную команду...
py src/emulatur.py --vfs ./archive.zip --script ./error.txt
pause
