@echo off 
chcp 65001 >nul
title MISE A JOUR
mode con lines=42
echo.


echo Detection des droits administrateur...
:: Vérifier si le script a été relancé avec des droits d'administrateur
if exist "C:\Users\Public\Documents\admin_check.tmp" (
del /Q "C:\Users\Public\Documents\admin_check.tmp"
goto hasAdminRights
)

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Vérifiez la barre des tâches si une application clignote orange, il faut accorder les droits d'admin !
    PowerShell -Command "Start-Process '%~f0' -Verb RunAs; Add-Content -Path 'C:\Users\Public\Documents\admin_check.tmp' -Value 'Admin'"
    exit
)

:hasAdminRights
:: Continuez le reste du script ici











:checkPython0
setlocal enabledelayedexpansion
set "needed_pyhton=False"
:checkPython
python --version >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo Python est installé.
) else (
    echo Python n'est pas installé.
    set "needed_pyhton=True"
    if not exist "C:\Python312" (
        mkdir "C:\Python312"
        echo Dossier C:\temp créé.
    )
    "bitsadmin.exe" /transfer "PythonInstaller" "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe" "C:\temp\OBS_module_chat\python-installer.exe"
    echo Lancement de l'installation de Python, patientez...
    echo echo [33mVérifiez la barre des tâches si une application clignote orange, il faut accorder les droits d'admin ![0m
    "C:\temp\OBS_module_chat\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 DefaultCustomInstall=1 DefaultPath=%installDir%
    :waitForInstaller
    timeout 5 >nul
    tasklist /FI "IMAGENAME eq python-installer.exe" 2>NUL | find /I "python-installer.exe" >NUL
    if "%ERRORLEVEL%"=="0" (
        goto waitForInstaller
    )
    del /Q "C:\temp\OBS_module_chat\python-installer.exe" /f /q
    timeout 5 >nul
    )
)
if "!needed_pyhton!"=="False" goto after_python
::------------------ENV REFRESH------------------
taskkill /f /im explorer.exe && start "" explorer.exe
echo patientez...
timeout 8 >nul
chcp 65001 >nul
curl -L "https://api.pastecode.io/anon/raw-snippet/p5miwe0u?raw=attachment&api=true&ticket=eecd2439-867e-4893-a6b0-6a06814bdbfa" -o "C:\temp\OBS_module_chat\refrenv.bat"
timeout 2>nul
call "C:\temp\OBS_module_chat\refrenv.bat"
timeout 6 >nul
for /f "tokens=*" %%i in ('where python') do set "PYTHON_PATH=%%i"
if defined PYTHON_PATH (
    echo Le chemin complet de git.exe est: %PYTHON_PATH%
) else (
    echo python.exe n'a pas été trouvé dans les chemins spécifiés dans PATH.
    echo relancez le script
    pause & exit
)
python --version
::----------------------------------------------------
:after_python


echo  vérifier pip

:: Vérifier et installer/mettre à jour les paquets PIP
echo [33;1mVérification des paquets PIP...[0m
"pip" install --upgrade pip
echo on vient de upgrade pip
echo.

endlocal




setlocal enabledelayedexpansion
:: Chemin des fichiers source et de destination
set "DEST_DIR=%localappdata%\OBS_module_chat"
set "SCRIPT_NAME=%~nx0"

:: Vérifier et copier les fichiers nécessaires
echo [33;1mVérification des fichiers nécessaires...[0m
echo.
:: Boucle pour chaque fichier .py et .bat dans %~dp0
for %%f in ("C:\temp\OBS_module_chat\*.py" "C:\temp\OBS_module_chat\*.bat" "C:\temp\OBS_module_chat\*.html" "C:\temp\OBS_module_chat\*.ini") do (
    echo Appel de :copy_if_newer "%%f" "%DEST_DIR%\%%~nxf"
    call :copy_if_newer "%%f" "%DEST_DIR%\%%~nxf"
    echo.
)







echo. & echo. & echo La mise à jour se termine... & timeout 5 >nul
endlocal
call "C:\temp\OBS_module_chat\OUVRIR CECI.bat"
exit





:copy_if_newer
setlocal enabledelayedexpansion
echo [33;1mVérification de la copie des fichiers...[0m
echo SRC_FILE: %1
echo DEST_FILE: %2
set SRC_FILE=%~1
set DEST_FILE=%~2

if not exist "%DEST_FILE%" (
    echo [31;1mFichier %DEST_FILE% n'existe pas. Copie du fichier...[0m
    copy "%SRC_FILE%" "%DEST_FILE%"
    echo [32;1mFichier copié.[0m
) else (
    echo [33;1mFichier %DEST_FILE% existe. Vérification des dates...[0m
    for %%i in ("%SRC_FILE%") do set "SRC_DATE=%%~ti"
    echo SRC_DATE: !SRC_DATE!
    for %%i in ("%DEST_FILE%") do set "DEST_DATE=%%~ti"
    echo DEST_DATE: !DEST_DATE!
    
    echo [33;1mComparaison des fichiers : source !SRC_DATE!, destination !DEST_DATE![0m
    if !SRC_DATE! GTR !DEST_DATE! (
        echo [31;1mMise à jour du fichier %DEST_FILE%...[0m
        copy /Y "%SRC_FILE%" "%DEST_FILE%"
        echo [32;1mFichier mis à jour.[0m
    ) else (
        echo [32;1mLe fichier %DEST_FILE% est à jour.[0m
    )
)
endlocal & exit /b
