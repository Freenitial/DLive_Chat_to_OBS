@echo off
title chat_initialisation
chcp 65001 >nul

REM Récupérer la version depuis l'URL avec curl
curl -s -o temp_version.txt https://pastebin.ai/raw/4fn0dgngwj

REM Lire le contenu du fichier temporaire dans une variable
set /p version=<temp_version.txt

REM Supprimer le fichier temporaire
del temp_version.txt

echo Version récupérée : %version%



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
    cmd /c "python "%~dp0\SCRIPT OBS FLASK.py""
    goto end
)
title chat_module_%version%
rem Lancer SCRIPT OBS FLASK.py si non trouvé en cours d'exécution
echo Lancement du script OBS FLASK.py...

cmd /c "python "%~dp0\SCRIPT OBS FLASK.py""

:end
endlocal
