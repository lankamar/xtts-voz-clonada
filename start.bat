@echo off
:: =============================================================================
:: LANKAMAR TTS — Iniciador de un solo clic
:: =============================================================================
:: Activa el entorno conda "coquitts" y lanza el servidor Flask.
:: Luego abre el navegador automáticamente en la URL correcta.
::
:: Cómo usar:
::   Doble clic en este archivo desde el Explorador de Windows.
::
:: Requisito:
::   El entorno conda "coquitts" debe estar en la carpeta del proyecto.
::   Si usás una ruta diferente, modificá la línea de python.exe abajo.
:: =============================================================================

title LANKAMAR TTS — Servidor de Voz

:: Nos ubicamos en la carpeta del proyecto (donde está este .bat)
cd /d "%~dp0"

echo.
echo  =====================================================
echo   LANKAMAR TTS — Iniciando motor de sintesis de voz
echo  =====================================================
echo.
echo  Cargando modelo XTTS v2...
echo  Esto puede tardar 20-30 segundos la primera vez.
echo.
echo  Cuando veas "Servidor disponible en: http://127.0.0.1:5001"
echo  abrí tu navegador en esa URL.
echo.
echo  Para detener: cerrá esta ventana o presioná Ctrl+C
echo.

:: Ejecutar con el Python del entorno coquitts directamente
:: (sin necesitar "conda activate" que puede fallar en PowerShell)
"%~dp0coquitts\python.exe" "%~dp0server\server.py"

echo.
echo  El servidor se detuvo.
pause
