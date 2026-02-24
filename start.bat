@echo off
:: =============================================================================
:: LANKAMAR TTS v2 — Iniciador de un solo clic
:: =============================================================================
:: Lanza el servidor usando el Python del entorno venv "coquitts".
:: No requiere conda ni activacion manual.
::
:: Uso: doble clic desde el Explorador de Windows.
::
:: Estructura esperada:
::   C:\tts-extension\
::   |-- coquitts\Scripts\python.exe   <- entorno venv con coqui-tts
::   |-- server\server.py              <- servidor Flask v2
::   |-- server\speakers\              <- fragmentos de voz WAV
::   |-- frontend\index.html           <- interfaz web
:: =============================================================================

title LANKAMAR TTS v2 — Motor de Voz

cd /d "%~dp0"

echo.
echo  =====================================================
echo   LANKAMAR TTS v2 — Iniciando motor de sintesis
echo  =====================================================
echo.
echo  Cargando modelo XTTS v2 (20-40 segundos la primera vez)...
echo.
echo  Cuando aparezca "Servidor disponible en: http://127.0.0.1:5001"
echo  abre tu navegador en esa URL.
echo.
echo  Podés pegar texto plano O scripts SSML directamente.
echo  Para detener: cerrá esta ventana o Ctrl+C
echo.

"%~dp0coquitts\Scripts\python.exe" "%~dp0server\server.py"

echo.
echo  El servidor se detuvo.
pause
