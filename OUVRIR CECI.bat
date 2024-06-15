@echo off
title chat_initialisation
chcp 65001 >nul
setlocal enabledelayedexpansion
set "obs_folder=%localappdata%\OBS_module_chat"


REM Récupérer la version depuis l'URL avec curl
curl -L -o temp_version.txt "https://api.pastecode.io/anon/raw-snippet/skr5y6xh?raw=inline&api=true&ticket=eecd2439-867e-4893-a6b0-6a06814bdbfa"
set /p version=<temp_version.txt
for /f "tokens=3 delims= " %%i in (temp_version.txt) do (
    set version=%%i
)
:: Supprimer les guillemets de la version
set version=%version:"=%
echo La version extraite est : %version%
REM Chemin vers le fichier version.txt sur le bureau
set "version_file=%obs_folder%\version.txt"

REM Créer le dossier OBS s'il n'existe pas
if not exist "%obs_folder%" (
    mkdir "%obs_folder%"
    echo Dossier %obs_folder% créé.
)

REM Vérifier si le fichier version.txt existe
if not exist "%version_file%" (
    echo Le fichier %version_file% n'existe pas. Création du fichier avec la version extraite.
    echo version = %version% > "%version_file%"
) else (
    REM Lire la version existante du fichier version.txt
    for /f "tokens=3 delims= " %%j in (%version_file%) do (
        set old_version=%%j
    )
    REM Supprimer les guillemets de l'ancienne version
    set old_version=%old_version:"=%
    REM Comparer les versions
    if %version% gtr %old_version% (
        echo La nouvelle version est plus récente. Mise à jour, veuillez patienter...
        echo version = %version% > "%version_file%"
        curl -L -o "%obs_folder%\INSTALL MAJ.bat" "https://api.pastecode.io/anon/raw-snippet/svs9stvw?raw=inline&api=true&ticket=eecd2439-867e-4893-a6b0-6a06814bdbfa"
        cmd /k "%obs_folder%\INSTALL MAJ.bat"
        del temp_version.txt
        timeout 3 >nul & exit
    ) else (
        echo La version actuelle est déjà à jour.
    )
)







setlocal
rem Vérifier si obs64.exe est en cours d'exécution
tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I /N "obs64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo OBS Studio est déjà en cours d'exécution.
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
echo Vérification de l'exécution de SCRIPT OBS FLASK.py...
for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq cmd.exe" /v /fo:csv /nh ^| findstr /r /c:".*chat_module_[^,]*$"') do (
    echo Le script est déjà ouvert. Fermeture...
    taskkill /pid %%a
    timeout 3 >nul
    echo Relancement du script...
    title chat_module_%version%
    timeout 1 >nul
    cmd /c "python "%obs_folder%\SCRIPT OBS FLASK.py""
    goto end
)
title chat_module_%version%
rem Lancer SCRIPT OBS FLASK.py si non trouvé en cours d'exécution
echo Lancement du script OBS FLASK.py...

cmd /c "python "%obs_folder%\SCRIPT OBS FLASK.py""

:end
endlocal
