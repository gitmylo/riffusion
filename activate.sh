source createvenv.sh
if [[ $OSTYPE == "msys" || $OSTYPE == "win32" ]]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi
