@echo off
chcp 65001 >nul
setlocal

set VENV_NAME="__venv__"

echo Checking for Python...
echo.

cd src

python --version >nul 2>&1

if %errorlevel% == 0 (
    echo Python is installed!

    python --version

    goto :pip
) else (
    echo Python is not installed!
)



:pip
    echo.
    pip --version >nul 2>&1

    if %errorlevel% == 0 (
        echo PIP is avaliable!

        pip --version

        goto :env
    ) else (
        echo PIP is not avaliable!
    )
:end

:env
    if exist "%VENV_NAME%\Scripts\activate.bat" (
        echo.
        echo Founded existing virtual environment, activiting...
        
        goto :activateEnv

        
    ) else (
        echo.
        echo Virtual environment was not found, creating...
        goto :createEnv
    )
:end

:createEnv
    python -m venv %VENV_NAME%

    if %errorlevel% neq 0 (
        echo.
        echo Can not create virtual environment!
        
        exit
    )
:end

:activateEnv
    echo.

    call "%VENV_NAME%\Scripts\activate.bat"

    goto :prepEnv
:end

:prepEnv
    echo.
    python -m pip install --upgrade pip

    if exist "requirements.txt" (
        echo.

        pip install -r requirements.txt

        goto :finalize
    ) else (
        echo requirements.txt was not found!

        exit
    )
:end

:finalize
    python main.py
:end

echo.
pause