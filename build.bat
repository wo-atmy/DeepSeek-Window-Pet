@echo off
rem ===========================================================================
rem  Build a CLEAN, RELOCATABLE portable folder.
rem
rem  Output:
rem    dist\WhalePet-Portable\        <- copy THIS folder anywhere; it just works
rem        WhalePet.exe / _internal\      the app + Qt/Python runtime
rem        assets\ lines.json             character images, sounds, editable lines
rem        README.txt LICENSE.txt         user readme + MIT notice
rem        THIRD-PARTY-NOTICES.txt        attribution / asset licensing
rem    dist\Whale-Pet-Portable.zip   <- the thing you hand over
rem
rem  Layout rules:
rem    * The exe must sit at the ROOT of the portable folder: the app resolves
rem      assets/ and lines.json relative to its own directory, so anything in a
rem      parent folder would NOT be found.
rem    * assets/ stays OUTSIDE the exe so art/sounds can be swapped without a
rem      rebuild.
rem    * Nothing else goes in there - no build logs, no dev README, no caches.
rem
rem  ASCII-ONLY ON PURPOSE. cmd.exe reads .bat using the OEM codepage (GBK on a
rem  Chinese Windows), so Chinese literals in this file turn into mojibake and
rem  the copy fails. All Chinese user-facing text lives in docs\*.txt instead.
rem ===========================================================================

setlocal
cd /d "%~dp0"

echo [1/4] Building with PyInstaller ...
python -m PyInstaller --noconfirm --clean --windowed --onedir ^
  --name WhalePet ^
  --icon app.ico ^
  --exclude-module PySide6.QtQml ^
  --exclude-module PySide6.QtQuick ^
  --exclude-module PySide6.QtQuickWidgets ^
  --exclude-module PySide6.QtNetwork ^
  --exclude-module PySide6.QtWebSockets ^
  --exclude-module PySide6.QtSql ^
  --exclude-module PySide6.QtTest ^
  --exclude-module PySide6.QtPrintSupport ^
  --exclude-module PySide6.QtOpenGL ^
  --exclude-module PySide6.QtOpenGLWidgets ^
  --exclude-module tkinter ^
  --exclude-module numpy ^
  --exclude-module PIL ^
  --exclude-module pytest ^
  --exclude-module pygame ^
  whale_pet.py
if errorlevel 1 goto :fail

echo [2/4] Assembling clean portable folder ...
set OUT=dist\WhalePet-Portable
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"
rem exe + _internal go to the ROOT (not into a subfolder)
xcopy /e /i /q /y "dist\WhalePet\*" "%OUT%\" >nul
if errorlevel 1 goto :fail
xcopy /e /i /q /y "assets" "%OUT%\assets" >nul
copy /y "lines.json" "%OUT%\lines.json" >nul

rem [3/4] user-facing readme + licensing files.
rem The Chinese readme ships as README.txt (ASCII filename) so it stays safe to
rem copy on any codepage: a Chinese filename literal cannot live in this file,
rem because cmd.exe reads .bat with the OEM codepage (GBK) and the name would
rem turn into mojibake, silently failing the copy. To ship a Chinese filename,
rem rename it AFTER building with PowerShell, which is codepage-safe:
rem   Rename-Item "dist\WhalePet-Portable\README.txt" "<chinese name>.txt"
rem
rem LICENSE and THIRD-PARTY-NOTICES MUST travel with the binary: MIT requires the
rem notice to be included in all copies, and the asset licensing story needs to
rem stay visible to whoever receives the folder.
if exist "docs\portable-readme.txt" copy /y "docs\portable-readme.txt" "%OUT%\README.txt" >nul
if exist "LICENSE" copy /y "LICENSE" "%OUT%\LICENSE.txt" >nul
if exist "THIRD-PARTY-NOTICES.md" copy /y "THIRD-PARTY-NOTICES.md" "%OUT%\THIRD-PARTY-NOTICES.txt" >nul

echo [4/4] Cleaning + zipping ...
rem strip anything that would make the package dirty
rem   - runtime files (config.json / pet.pid) must NOT ship: the app treats a
rem     missing config.json as "first run". Testing the exe out of the portable
rem     folder creates them, so this also protects a rebuild after testing.
for /d /r "%OUT%" %%D in (__pycache__) do if exist "%%D" rmdir /s /q "%%D"
del /s /q "%OUT%\*.pyc" >nul 2>nul
del /s /q "%OUT%\*.pyo" >nul 2>nul
del /q "%OUT%\config.json" >nul 2>nul
del /q "%OUT%\pet.pid" >nul 2>nul
del /q "%OUT%\*.log" >nul 2>nul
rem Qt ships ~7 MB of translations we never use
if exist "%OUT%\_internal\PySide6\translations" rmdir /s /q "%OUT%\_internal\PySide6\translations"

rem ---------------------------------------------------------------------------
rem Slim the Qt runtime. PyInstaller's dependency analysis is name-based and
rem pulls in far more than this app touches. Every removal below was verified by
rem launching the built exe from a clean folder afterwards.
rem
rem   opengl32sw.dll   ~20 MB  Qt's SOFTWARE OpenGL fallback, used only when the
rem                            GPU driver has no usable OpenGL. This app renders
rem                            with QPainter (raster) into a layered window and
rem                            never requests an OpenGL surface, so it is dead
rem                            weight - and by far the biggest single win here.
rem   Qt6Network.dll   ~1.7 MB QNetwork is already in --exclude-module, but the
rem                            DLL still shipped. The app makes no network calls.
rem   qdirect2d.dll    ~1.0 MB alternative platform backend; qwindows is the one
rem                            actually loaded on every supported Windows.
rem   qminimal/qoffscreen        headless platform backends, not used at runtime.
rem   qtiff/qtga/qwbmp/qicns     image formats no skin or icon needs (PNG/JPG/
rem                            GIF/BMP/WebP/ICO/SVG are deliberately KEPT, since
rem                            users drop their own char.png / char.jpg skins in).
rem   qsvgicon.dll               SVG *icon engine*; the app loads its icon from
rem                            a PNG and draws the bubble from an inline SVG, so
rem                            this engine is never consulted. Qt6Svg.dll stays.
rem   libcrypto-3.dll  ~5.1 MB  OpenSSL, dragged in for Python's ssl/hashlib.
rem   _hashlib.pyd     + ssl     The app imports neither hashlib nor ssl nor
rem   _socket.pyd                socket (it is explicitly offline and its audio
rem                              goes through winmm), and PyInstaller no longer
rem                              ships _ssl.pyd at all - so libcrypto has no
rem                              consumer left. Removing these also drops the
rem                              TCP/HTTP surface entirely, which is consistent
rem                              with the "no network calls" guarantee.
rem
rem Net effect: portable folder ~83 MB -> ~55 MB, zip ~34 MB -> ~23 MB.
rem ---------------------------------------------------------------------------
del /q "%OUT%\_internal\PySide6\opengl32sw.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\Qt6Network.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\platforms\qdirect2d.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\platforms\qminimal.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\platforms\qoffscreen.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\imageformats\qtiff.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\imageformats\qtga.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\imageformats\qwbmp.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\imageformats\qicns.dll" >nul 2>nul
del /q "%OUT%\_internal\PySide6\plugins\iconengines\qsvgicon.dll" >nul 2>nul
if exist "%OUT%\_internal\PySide6\plugins\generic" rmdir /s /q "%OUT%\_internal\PySide6\plugins\generic"
del /q "%OUT%\_internal\libcrypto-3.dll" >nul 2>nul
del /q "%OUT%\_internal\_hashlib.pyd" >nul 2>nul
del /q "%OUT%\_internal\_socket.pyd" >nul 2>nul
del /q "%OUT%\_internal\_ssl.pyd" >nul 2>nul
if exist "%OUT%\_internal\PySide6\plugins\tls" rmdir /s /q "%OUT%\_internal\PySide6\plugins\tls"

if exist "dist\Whale-Pet-Portable.zip" del /q "dist\Whale-Pet-Portable.zip"
powershell -NoProfile -Command "Compress-Archive -Path 'dist\WhalePet-Portable\*' -DestinationPath 'dist\Whale-Pet-Portable.zip' -Force"
if errorlevel 1 goto :fail

rem Place a commit-ready copy at the REPO ROOT. .gitignore excludes dist/ but
rem explicitly re-includes /Whale-Pet-Portable.zip, so this copy is the one that
rem can be uploaded to the repo; the dist\ copy stays the local build artifact.
rem Delete it (or commit without it) if you prefer Releases-only distribution.
copy /y "dist\Whale-Pet-Portable.zip" "Whale-Pet-Portable.zip" >nul

rem leave the source tree clean: --clean rebuilds the cache every time anyway
if exist "build" rmdir /s /q "build"
if exist "WhalePet.spec" del /q "WhalePet.spec"
rem dist\WhalePet is the raw PyInstaller output, already copied into the
rem portable folder; keeping it just doubles the disk usage
if exist "dist\WhalePet" rmdir /s /q "dist\WhalePet"

echo.
echo Done.
echo   Folder : %CD%\%OUT%
echo   Zip    : %CD%\dist\Whale-Pet-Portable.zip
echo.
echo Copy the folder (or the zip) to any Windows PC and double-click WhalePet.exe
echo No Python / PySide6 / DSH plugin needed on the target machine.
goto :eof

:fail
echo.
echo BUILD FAILED.
exit /b 1
