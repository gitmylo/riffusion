@echo off
call activate.bat
echo Installing all requirements, please wait...
pip install -r requirements_all.txt > nul
echo Finished installing requirements!
call deactivate.bat
