@echo off
title chat_initialisation

setlocal
chcp 65001 >nul
set "APP_DIR="%localappdata%\OBS_module_chat"
set "REPO_DIR="C:\temp\OBS_module_chat"


REM Créer le dossier temporaire s'il n'existe pas
if not exist "C:\temp" (
    mkdir "C:\temp"
    echo Dossier C:\temp créé.
)

REM Créer le dossier OBS s'il n'existe pas
if not exist "%localappdata%\OBS_module_chat" (
    mkdir "%localappdata%\OBS_module_chat"
    echo Dossier %localappdata%\OBS_module_chat créé.
)

PowerShell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'OBS_module_chat.lnk')); $Shortcut.TargetPath = '%localappdata%\OBS_module_chat'; $Shortcut.Save()"

REM Vérifier si git est installé
git --version >nul 2>&1
if %errorlevel% neq 0 (
    
    echo Git n'est pas installé. Installation de Git...
    echo [33;1mDetection des droits administrateur...[0m
    :: Vérifier si le script a été relancé avec des droits d'administrateur
    if exist "C:\temp\OBS_module_chat\admin_check.tmp" (
        del "C:\temp\OBS_module_chat\admin_check.tmp"
        goto hasAdminRights
    )
    net session 
    if %errorLevel% neq 0 (
        echo [33mVérifiez la barre des tâches si une application clignote orange, il faut accorder les droits d'admin ![0m
        PowerShell -Command "Start-Process '%~f0' -Verb RunAs; Add-Content -Path 'C:\temp\OBS_module_chat\admin_check.tmp' -Value 'Admin'"
        exit
    )
    :hasAdminRights
    echo Vous avez les droits d'administrateur.
    REM Définir l'URL du programme d'installation de Git
    set "GIT_INSTALLER_URL=https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe"
    REM Définir le chemin du programme d'installation téléchargé
    set "GIT_INSTALLER="C:\temp\OBS_module_chat\git-installer.exe"
    REM Télécharger le programme d'installation de Git
    curl -L https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe -o "C:\temp\OBS_module_chat\git-installer.exe" 
    REM Vérifier si le téléchargement a réussi
    if %errorlevel% neq 0 (
        echo Échec du téléchargement du programme d'installation de Git.
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
    del "%GIT_INSTALLER%" /f /q
    :checkGitInstallation
    git --version >nul 2>&1
    if "%ERRORLEVEL%"=="0" (
        echo Git a été installé avec succès.
    ) else (
        echo L'installation de Git n'est pas encore détectée, Nouvel essai dans quelques secondes...
        timeout 3 >nul
        curl -L https://api.pastecode.io/anon/raw-snippet/p5miwe0u?raw=inline&api=true&ticket=eecd2439-867e-4893-a6b0-6a06814bdbfa -o "C:\temp\OBS_module_chat\refrenv.bat"
        call "C:\temp\OBS_module_chat\refrenv.bat"
        timeout 3 >nul
        goto checkGitInstallation
    )
    
) else (
    echo Git est déjà installé.
)

endlocal
setlocal
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


cd /d "C:\temp\OBS_module_chat"
REM Vérifier si le répertoire est un dépôt Git
if exist .git (
    echo "Mise à jour de C:\temp\OBS_module_chat..."
    git pull origin main
    if %errorlevel% neq 1 (set "need_update=False")
) else (
    echo "Suppression du répertoire et re-clonage..."
    cd ..
    rmdir /s /q "C:\temp\OBS_module_chat"
    git clone https://github.com/djleo70/obs_python_flask.git "C:\temp\OBS_module_chat"
    set "need_update=True"
)



if %need_update%==True (
start "" "cmd /k "C:\temp\OBS_module_chat\UPDATE.bat"
exit
)




endlocal







setlocal
rem Vérifier si obs64.exe est en cours d'exécution
tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I /N "obs64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo OBS Studio est ouvert...
) else (
    echo Lancement de OBS Studio...
    rem Lancer OBS Studio (64bit) depuis shell:appsfolder
    start "" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OBS Studio\OBS Studio (64bit).lnk"
    rem Attendre que la fenêtre de obs64.exe soit prête
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

rem Vérifier et relancer SCRIPT OBS FLASK.py si nécessaire
echo Lancement SCRIPT OBS FLASK.py...
for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq cmd.exe" /v /fo:csv /nh ^| findstr /r /c:".*chat_module[^,]*$"') do (
    echo Le script est déjà ouvert. Fermeture...
    taskkill /pid %%a
    timeout 3 >nul
    echo Relancement du script...
    title chat_module
    timeout 1 >nul
    cmd /c "python "%localappdata%\OBS_module_chat\SCRIPT OBS FLASK.py""
    goto end
)
title chat_module
rem Lancer SCRIPT OBS FLASK.py si non trouvé en cours d'exécution
echo Lancement du script OBS FLASK.py...

cmd /c "python "%localappdata%\OBS_module_chat\SCRIPT OBS FLASK.py""

:end
endlocal
