#!/bin/bash
# =============================================================
# setup.sh — Instalacion automatica XTTS Voz Clonada
# Compatible: Linux / Mac / WSL (Windows Subsystem for Linux)
# Requisito: Python 3.10
# =============================================================

set -e

echo ""
echo "============================================"
echo "  XTTS Voz Clonada — Setup"
echo "============================================"
echo ""

# Verificar Python 3.10
if ! python3.10 --version &>/dev/null; then
  echo "ERROR: Python 3.10 no encontrado."
  echo "Instala con: sudo apt install python3.10 python3.10-venv"
  exit 1
fi

# Crear entorno virtual
echo "[1/4] Creando entorno virtual..."
python3.10 -m venv venv
source venv/bin/activate

# Actualizar pip
echo "[2/4] Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar PyTorch con CUDA 11.8 (cambia cu118 por cpu si no tenes GPU)
echo "[3/4] Instalando PyTorch..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet

# Instalar dependencias del proyecto
echo "[4/4] Instalando dependencias XTTS..."
pip install -r requirements.txt --quiet

# Crear carpetas necesarias
mkdir -p server/speakers output

echo ""
echo "============================================"
echo "  Instalacion completada exitosamente!"
echo "============================================"
echo ""
echo "PROXIMO PASO:"
echo "  1. Copia tu audio de referencia a:"
echo "     server/speakers/TU_NOMBRE.wav"
echo "     (minimo 6 segundos, mono, 22050 Hz)"
echo ""
echo "  2. Levanta el servidor:"
echo "     ./start_server.sh"
echo ""
echo "  3. Abre el frontend:"
echo "     cd frontend && python -m http.server 8080"
echo "     http://localhost:8080"
echo ""
