@echo off
REM Use python from PATH
set PYTHON_CMD=python

REM Change to the project directory
cd /d %~dp0

REM Detect if Python is installed
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
	echo ERROR: Python was not found in PATH.
	echo Please install Python 3 and ensure it's in your PATH.
    echo chocolatey.org is one option: choco install python
	pause
	exit /b 1
)

REM Check Python version is 3.x
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Using Python version: %PYTHON_VERSION%

REM Install requirements if requirements.txt exists
if exist requirements.txt %PYTHON_CMD% -m pip install -r requirements.txt

REM Install PyInstaller if not already installed
%PYTHON_CMD% -m pip install pyinstaller

REM Build the executable with hidden imports for common modules
%PYTHON_CMD% -m PyInstaller --onefile sisou.py --hidden-import=requests --hidden-import=PyYAML

REM Notify user of result
echo Build complete! The results are available in: dist\sisou.exe
pause
