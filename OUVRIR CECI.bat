chcp 1252 >nul
@echo off
title chat_initialisation

setlocal

set "APP_DIR="%localappdata%\OBS_module_chat"
set "REPO_DIR="C:\temp\OBS_module_chat"


REM Créer le dossier temporaire s'il n'existe pas
if not exist "C:\temp" (
    mkdir "C:\temp"
    echo Dossier C:\temp créé.
)

REM Créer le dossier temporaire s'il n'existe pas
if not exist "C:\temp\OBS_module_chat" (
    mkdir "C:\temp\OBS_module_chat"
    echo Dossier C:\temp\OBS_module_chat créé.
)

REM Créer le dossier OBS s'il n'existe pas
if not exist "%localappdata%\OBS_module_chat" (
    mkdir "%localappdata%\OBS_module_chat"
    echo Dossier %localappdata%\OBS_module_chat créé.
)



setlocal

:: Définir les chemins
set "TARGET_PATH=%localappdata%\OBS_module_chat"
set "SHORTCUT_PATH="%userprofile%\Desktop\OBS_module_chat.lnk"

:: Créer un fichier temporaire VBS
set "VBS_FILE=C:\Users\Public\Documents\CreateShortcut.vbs"
(
    echo Set WshShell = CreateObject^(^"WScript.Shell^"^)
    echo Set Shortcut = WshShell.CreateShortcut(^%SHORTCUT_PATH%")
    echo Shortcut.TargetPath = "%TARGET_PATH%"
    echo Shortcut.Save
) > "%VBS_FILE%"

:: Afficher le contenu du fichier VBS pour débogage
type "%VBS_FILE%"

:: Vérifier si le fichier VBS a été créé
if exist "%VBS_FILE%" (
    :: Exécuter le script VBS
    cscript //nologo "%VBS_FILE%"
    :: Supprimer le script VBS temporaire
    del "%VBS_FILE%"
) else (
    echo Erreur: Impossible de créer le fichier VBS temporaire.
)


endlocal













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
    echo. & echo   Vérifiez LA BARRE DES TACHES si une application CLIGNOTE ORANGE, 
    echo    il faut ACCORDER LES DROITS D'ADMIN ![0m
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
    echo. & echo python.exe n'a pas été trouvé dans les chemins spécifiés dans PATH.
    echo le script va se relancer tout seul....
    timeout 3 > nul
    start "" /d "%~dp0" "%~nx0"
    exit
)
python --version
::----------------------------------------------------
:after_python


echo  vérifier pip
:: Vérifier et installer/mettre à jour les paquets PIP
echo [33;1mVérification des paquets PIP...[0m
"pip" install --upgrade pip
echo on vient de upgrade pip, on passe aux paquets
"pip" install --upgrade selenium obs-websocket-py flask flask-cors flask-socketio pillow requests
echo.













set "needed_git=False"
REM Vérifier si git est installé
git --version >nul 2>&1
if %errorlevel% neq 0 (
    set "needed_git=True"
    echo Git n'est pas installé. Installation de Git...
    REM Télécharger le programme d'installation de Git
    curl -L https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe -o "C:\temp\OBS_module_chat\git-installer.exe"
    echo Patientez...
    REM Vérifier si le téléchargement a réussi
    if %errorlevel% neq 0 (
        echo Échec du téléchargement du programme d'installation de Git.
        pause
        exit /b 1
    )
    REM Exécuter le programme d'installation de Git en mode silencieux
    start "" /wait "C:\temp\OBS_module_chat\git-installer.exe" /VERYSILENT /NORESTART
    :waitForInstaller
    timeout 5 >nul
    tasklist /FI "IMAGENAME eq git-installer.exe" 2>NUL | find /I "git-installer.exe" >NUL
    if "%ERRORLEVEL%"=="0" (
        goto waitForInstaller
    )
    echo suppression de l'installateur
    del "C:\temp\OBS_module_chat\git-installer.exe" /f /q
    timeout 2 >nul
    
) else (
    echo Git est installé.
)


echo avant refrenv
if "!needed_git!"=="False" goto after_git
::------------------ENV REFRESH------------------
taskkill /f /im explorer.exe && start "" explorer.exe
echo patientez...
timeout 9 >nul
endlocal
timeout 2 >nul
setlocal EnableDelayedExpansion
chcp 65001 >nul
curl -L "https://api.pastecode.io/anon/raw-snippet/p5miwe0u?raw=attachment&api=true&ticket=eecd2439-867e-4893-a6b0-6a06814bdbfa" -o "C:\temp\OBS_module_chat\refrenv.bat"
call "C:\temp\OBS_module_chat\refrenv.bat"
::C:\temp\OBS_module_chat\nircmd.exe sysrefresh environment
timeout 6 >nul
REM Rechercher le chemin complet de git.exe
for /f "tokens=*" %%i in ('where git') do set "GIT_PATH=%%i"
REM Vérifier si git.exe a été trouvé
if defined GIT_PATH (
    echo Le chemin complet de git.exe est: %GIT_PATH%
) else (
    echo. & echo GIT.exe n'a pas été trouvé dans les chemins spécifiés dans PATH.
    echo le script va se relancer tout seul....
    timeout 3 > nul
    start "" /d "%~dp0" "%~nx0"
)
git --version
::----------------------------------------------------

echo juste avant after_git
:after_git

echo. & echo après refrenv
timeout 2 >nul

set "need_update=False"
REM Vérifier si le REPO existe déjà
if exist "C:\temp\OBS_module_chat" (
    REM Changer de répertoire vers le répertoire existant
    cd /d "C:\temp\OBS_module_chat"
) else (
    mkdir "C:\temp\OBS_module_chat"
    echo Dossier C:\temp\OBS_module_chat créé.
    REM Cloner le dépôt
    git clone https://github.com/djleo70/obs_python_flask.git "C:\temp\OBS_module_chat"
    set "need_update=True"
)

echo juste avant need1
if "%need_update%"=="True" (
    if exist "C:\temp\OBS_module_chat\UPDATE.bat" (
        start "" cmd /k "C:\temp\OBS_module_chat\UPDATE.bat"
        echo started UPDATE
        exit
    ) else (
        echo Le fichier UPDATE.bat n'existe pas encore
    )
)
echo après need1
git config --global --add safe.directory C:/temp/OBS_module_chat
cd /d "C:\temp\OBS_module_chat"
REM Vérifier si le répertoire est un dépôt Git
if exist .git (
    echo "Mise à jour de C:\temp\OBS_module_chat..."
    for /f %%i in ('git rev-parse HEAD') do set "old_head=%%i"
    git pull origin main
    for /f %%i in ('git rev-parse HEAD') do set "new_head=%%i"
    if "!old_head!"=="!new_head!" (
        set "need_update=False"
    ) else (
        set "need_update=True"
    )
) else (
    echo "Suppression du répertoire et re-clonage..."
    cd ..
    rmdir /s /q "C:\temp\OBS_module_chat"
    git clone https://github.com/djleo70/obs_python_flask.git "C:\temp\OBS_module_chat"
    set "need_update=True"
)


python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas installé.
    set "need_update=True"
) else (
    echo Python est installé.
)

if not exist "%localappdata%\OBS_module_chat\SCRIPT OBS FLASK.py" (
    echo Il manque le script.
    set "need_update=True"
)


echo juste avant need2
echo need update : !need_update!
if "!need_update!"=="True" (
    echo starting update...
    start "" cmd /k "C:\temp\OBS_module_chat\UPDATE.bat"
    timeout 2 >nul
    exit
)




























echo avant de lancer obs
rem Vérifier si obs64.exe est en cours d'exécution
tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I /N "obs64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo OBS Studio est ouvert...
) else (
    echo juste avant de lancer obs
    echo Lancement de OBS Studio...
    echo juste avant de lancer obs
    start "" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OBS Studio\OBS Studio (64bit).lnk"
    rem Attendre que la fenêtre de obs64.exe soit prête
    echo obs lancé
    :waitForOBS
    timeout 5 >NUL
    tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I /N "obs64.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo OBS Studio est maintenant en cours d'exécution.
    ) else (
        echo Attente de OBS Studio...
        goto waitForOBS
    )
)
chcp 1252 >nul
echo fin de boucle
rem Vérifier et relancer SCRIPT OBS FLASK.py si nécessaire
echo Lancement SCRIPT OBS FLASK.py...
for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq cmd.exe" /v /fo:csv /nh ^| findstr /r /c:".*chat_module[^,]*$"') do (
    
    taskkill /pid %%a
    echo Le script est deja ouvert. Fermeture...
    timeout 3 >nul
    echo Relancement du script...
    timeout 1 >nul
    title chat_module
    cmd /c "python "%localappdata%\OBS_module_chat\SCRIPT OBS FLASK.py""
    goto end
)
title chat_module
rem Lancer SCRIPT OBS FLASK.py si non trouvé en cours d'exécution
echo Lancement du script OBS FLASK.py...

cmd /c "python "%localappdata%\OBS_module_chat\SCRIPT OBS FLASK.py""
:end
pause
endlocal
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
