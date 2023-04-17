@echo off
call activate.bat
echo Installing all requirements, please wait...
pip install -r requirements_all.txt > nul
echo Installing torch with CUDA, please wait...
pip install torch==2.0.0+cu117 torchvision==0.15.0+cu117 --index-url https://download.pytorch.org/whl/cu117
echo Finished installing requirements!
call deactivate.bat
