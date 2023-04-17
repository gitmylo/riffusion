@echo off
call setup.bat
call activate.bat
echo starting gui...
python gui.py
call deactivate.bat