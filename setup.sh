source activate.sh
echo Installing all requirements, please wait...
pip install -r requirements_all.txt > /dev/null
echo Installing torch with CUDA, please wait...
pip install torch==2.0.0+cu117 torchvision==0.15.0+cu117 --index-url https://download.pytorch.org/whl/cu117
echo Finished installing requirements!
deactivate
