@echo off
REM =============================================================
REM setup.bat - Instalacion automatica XTTS Voz Clonada
REM Compatible: Windows 10/11
REM Requisito: Python 3.10 en PATH
REM =============================================================

echo.
echo ============================================
echo   XTTS Voz Clonada - Setup Windows
echo ============================================
echo.

REM Verificar Python 3.10
python --version 2>nul | findstr /C:"3.10" >nul
if errorlevel 1 (
    echo ERROR: Python 3.10 no encontrado en PATH.
    echo Descargalo de https://www.python.org/downloads/release/python-31011/
    pause
    exit /b 1
)

REM Crear entorno virtual
echo [1/4] Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate.bat

REM Actualizar pip
echo [2/4] Actualizando pip...
python -m pip install --upgrade pip --quiet

REM Instalar PyTorch CUDA 11.8 (cambiar cu118 por cpu si no hay GPU)
echo [3/4] Instalando PyTorch...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet

REM Instalar dependencias
echo [4/4] Instalando dependencias XTTS...
pip install -r requirements.txt --quiet

REM Crear carpetas
if not exist "server\speakers" mkdir server\speakers
if not exist "output" mkdir output

echo.
echo ============================================
echo   Instalacion completada exitosamente!
echo ============================================
echo.
echo PROXIMO PASO:
echo   1. Copia tu audio a: server\speakers\TU_NOMBRE.wav
echo      (minimo 6 segundos, mono, 22050 Hz)
echo   2. Ejecuta: start_server.bat
echo   3. Abre: frontend\index.html desde http://localhost:8080
echo.
pause
