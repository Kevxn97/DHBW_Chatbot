@echo off
setlocal EnableDelayedExpansion

rem Definiere den Pfad zum Backend-Skript
set BACKEND_SCRIPT=index copy.js
rem Definiere das Verzeichnis für das Frontend
set FRONTEND_DIR=Frontend
rem Standard-URL für Streamlit
set FRONTEND_URL=http://localhost:8501

echo ========================================
echo  Starte Backend ^& Frontend Chatbot
echo ========================================
echo.

rem --- Backend starten ---
echo [1/2] Starte Backend-Server (Node)...

rem Starten des Node.js-Backends im Hintergrund mit eigenem Fenster
start "Node.js Backend" cmd /c "node "!BACKEND_SCRIPT!" & pause"
rem Wir verwenden den Fenstertitel, um den Prozess später zu identifizieren
set "BACKEND_TITLE=Node.js Backend"
echo     Backend gestartet
echo.

rem --- Frontend starten ---
echo [2/2] Starte Frontend-Server (Streamlit)...
rem Wechsle ins Frontend-Verzeichnis
if not exist "!FRONTEND_DIR!" (
    echo Fehler: Frontend-Verzeichnis nicht gefunden: !FRONTEND_DIR!
    exit /b 1
)
cd "!FRONTEND_DIR!"

rem Starte Streamlit im Hintergrund
start "Streamlit Frontend" cmd /c "streamlit run app.py & pause"
rem Wir verwenden den Fenstertitel, um den Prozess später zu identifizieren
set "FRONTEND_TITLE=Streamlit Frontend"
echo     Frontend gestartet
echo.

rem Gehe zurück zum ursprünglichen Verzeichnis
cd ..

rem --- Warte kurz und zeige Link ---
echo Warte kurz, bis die Server bereit sind...
timeout /t 5 /nobreak >nul

rem Öffne den Browser automatisch
start "" "!FRONTEND_URL!"

echo.
echo ----------------------------------------
echo Server sollten jetzt laufen.
echo Frontend wurde automatisch im Browser geöffnet.
echo Falls nicht, gehe zu: !FRONTEND_URL!
echo ----------------------------------------
echo.
echo Hinweis: Beide Server laufen in minimierten Fenstern.
echo          Sie können über die Taskleiste geschlossen werden.
echo          Oder drücken Sie eine Taste, um beide Prozesse zu beenden.
echo.

rem Warten auf Benutzereingabe
pause

rem Beenden der Server durch Schließen der Fenster
echo.
echo Beende Server...
taskkill /FI "WINDOWTITLE eq !BACKEND_TITLE!*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq !FRONTEND_TITLE!*" /F >nul 2>&1
echo Server beendet.

endlocal 