if ! [ -e "venv" ]; then
  echo Creating venv, please wait...
  if [[ $OSTYPE == "msys" || $OSTYPE == "win32" ]]; then
    py -m venv venv
  else
    python -m venv venv
  fi
  echo Created venv!
fi
