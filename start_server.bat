@echo off
REM =============================================================
REM start_server.bat - Levanta el servidor XTTS en Windows
REM =============================================================

call venv\Scripts\activate.bat

echo.
echo ============================================
echo   Iniciando servidor XTTS en :5051
echo ============================================
echo.
echo   API:      http://localhost:5051
echo   Docs:     http://localhost:5051/docs
echo   Frontend: http://localhost:8080
echo.
echo   Presiona Ctrl+C para detener
echo ============================================
echo.

python -m xtts_api_server ^
  --host 0.0.0.0 ^
  --port 5051 ^
  --speakers-folder server\speakers ^
  --output output ^
  --cors

REM Agregar --use-cpu si no tenes GPU NVIDIA
pause
