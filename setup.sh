source activate.sh
echo Installing all requirements, please wait...
pip install -r requirements_all.txt > /dev/null
echo Finished installing requirements!
deactivate
