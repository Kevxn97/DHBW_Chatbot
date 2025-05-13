#!/bin/bash

# Definiere den Pfad zum Backend-Skript
BACKEND_SCRIPT="index copy.js"
# Definiere das Verzeichnis für das Frontend
FRONTEND_DIR="Frontend"
# Standard-URL für Streamlit
FRONTEND_URL="http://localhost:8501"

echo "========================================"
echo " Starte Backend & Frontend Chatbot"
echo "========================================"
echo ""

# --- Backend starten ---
echo "[1/2] Starte Backend-Server (Node)..."
# Wechsle ins Backend-Verzeichnis (optional, da wir schon drin sind)
# cd "$(dirname "$0")" || exit
node "$BACKEND_SCRIPT" &
BACKEND_PID=$!
echo "    Backend gestartet (PID: $BACKEND_PID)"
echo ""

# --- Frontend starten ---
echo "[2/2] Starte Frontend-Server (Streamlit)..."
# Wechsle ins Frontend-Verzeichnis
cd "$FRONTEND_DIR" || { echo "Fehler: Frontend-Verzeichnis nicht gefunden: $FRONTEND_DIR"; exit 1; }
streamlit run app.py &
FRONTEND_PID=$!
echo "    Frontend gestartet (PID: $FRONTEND_PID)"
echo ""

# Gehe zurück zum ursprünglichen Verzeichnis
cd ..

# --- Warte kurz und zeige Link ---
echo "Warte kurz, bis die Server bereit sind..."
sleep 5 # Kleine Pause, damit die Server hochfahren können

echo ""
echo "----------------------------------------"
echo "Server sollten jetzt laufen."
echo "Hier zum Chatbot: $FRONTEND_URL"
echo "----------------------------------------"
echo ""
echo "Hinweis: Beide Server laufen im Hintergrund."
echo "         Schließe dieses Terminal, um beide zu beenden,"
echo "         oder beende sie manuell mit:"
echo "         kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Funktion zum Aufräumen beim Beenden des Skripts (z.B. mit Strg+C)
cleanup() {
    echo ""
    echo "Beende Server..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null # Unterdrücke Fehler, falls schon beendet
    echo "Server beendet."
    exit 0
}

# Fange das Beenden-Signal ab (Strg+C)
trap cleanup SIGINT SIGTERM

# Warte, bis das Skript manuell beendet wird, damit die Hintergrundprozesse nicht sofort verschwinden
wait $BACKEND_PID $FRONTEND_PID 