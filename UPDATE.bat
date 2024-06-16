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




set "webdriverVersion=126.0.6478.61"
if not exist "C:\WebDrivers" (
    echo [33;1mCréation du répertoire C:\WebDrivers...[0m
    mkdir "C:\WebDrivers"
    echo [32;1mRépertoire C:\WebDrivers créé.[0m
)
REM Naviguer vers le dossier source
cd /d "C:\temp\OBS_module_chat"
REM Télécharger le fichier zip
curl -o chromedriver-win64.zip -L https://storage.googleapis.com/chrome-for-testing-public/%webdriverVersion%/win64/chromedriver-win64.zip --retry 3 --retry-delay 5
REM Vérifier si le téléchargement a réussi
if %errorlevel% neq 0 (
    echo Échec du téléchargement.
    exit /b 1
)
REM Extraire le fichier zip et écraser les fichiers existants
tar -xf chromedriver-win64.zip -C "C:\temp\OBS_module_chat"
REM Déplacer les fichiers extraits vers le répertoire principal
xcopy "C:\temp\OBS_module_chat\chromedriver-win64\*" "C:\WebDrivers" /s /e /y
REM Supprimer le dossier temporaire
rmdir /s /q "C:\temp\OBS_module_chat\chromedriver-win64"

REM Vérifier si l'extraction a réussi
if %errorlevel% neq 0 (
    echo Échec de l'extraction.
    exit /b 1
)
echo Extraction terminée
echo.
REM Supprimer le fichier zip
del /Q /f /q chromedriver-win64.zip



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
