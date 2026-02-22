#!/bin/bash
# =============================================================
# start_server.sh - Levanta el servidor XTTS con CORS abierto
# =============================================================

source venv/bin/activate

echo ""
echo "============================================"
echo "  Iniciando servidor XTTS en :5051"
echo "============================================"
echo ""
echo "  API:      http://localhost:5051"
echo "  Docs:     http://localhost:5051/docs"
echo "  Frontend: http://localhost:8080"
echo ""
echo "  Presiona Ctrl+C para detener"
echo "============================================"
echo ""

python -m xtts_api_server \
  --host 0.0.0.0 \
  --port 5051 \
  --speakers-folder ./server/speakers \
  --output ./output \
  --cors

# Nota: agregar --deepspeed si tenes GPU compatible (acelera x3)
# Nota: agregar --use-cpu si NO tenes GPU NVIDIA
