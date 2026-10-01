@echo off
chcp 65001 > nul
title Avvio Vetrina Scarpe

echo ===================================================
echo   AVVIO VETRINA SCARPE (Backend + Frontend)
echo ===================================================
echo.

if not exist "frontend\node_modules\.bin\vite.cmd" (
    echo 📦 Prima installazione dipendenze in corso (richiede qualche secondo)...
    cd frontend
    call npm.cmd install
    cd ..
    echo ✅ Dipendenze installate con successo!
    echo.
)

echo 1. Avvio Backend FastAPI (Porta 8000)...
start "Backend FastAPI" cmd /k "python run_backend.py"

echo 2. Avvio Frontend React (Porta 5173)...
start "Frontend React" cmd /k "cd frontend && npm.cmd run dev"

echo.
echo ===================================================
echo  ✅ Server avviati correttamente!
echo  👉 Apri il tuo browser su: http://localhost:5173
echo ===================================================
echo.
pause
