@echo off
REM Set the path to your Python 3.12 installation
set PYTHON312=C:\Python312\python.exe

REM Change to the project directory
cd /d %~dp0


REM Install requirements if requirements.txt exists
if exist requirements.txt %PYTHON312% -m pip install -r requirements.txt

REM Install PyInstaller if not already installed
%PYTHON312% -m pip install pyinstaller

REM Build the executable with hidden imports for common modules
%PYTHON312% -m PyInstaller --onefile sisou.py --hidden-import=requests --hidden-import=PyYAML

REM Notify user of result
echo Build complete! The results are available in: dist\sisou.exe
pause
