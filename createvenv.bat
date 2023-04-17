@echo off
if not exist venv (
    echo Creating venv, please wait...
    py -m venv venv
    echo Created venv!
)
