if ! [ -e "venv" ]; then
  echo Creating venv, please wait...
  if [[ $OSTYPE == "msys" || $OSTYPE == "win32" ]]; then
    py -m venv venv --upgrade-deps > /dev/null
  else
    python3 -m venv venv --upgrade-deps > /dev/null
  fi
  echo Created venv!
fi
