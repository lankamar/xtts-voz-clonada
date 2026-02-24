# =============================================================================
# LANKAMAR TTS — Servidor de Síntesis de Voz
# =============================================================================
# Autor     : Marcelo Omar Lancry k. (Lankamar)
# Proyecto  : xtts-voz-clonada
# Puerto    : 5001
# Motor     : XTTS v2 (Coqui TTS — fork Idiap)
#
# Descripción:
#   Servidor Flask que expone un endpoint HTTP para convertir texto en audio
#   usando el modelo XTTS v2 con capacidad de clonación de voz desde una
#   muestra de audio WAV.
#
#   El servidor sirve también la interfaz web directamente, eliminando
#   los conflictos de CORS que ocurren al abrir HTML desde file://.
#
# Requisitos previos:
#   - Entorno conda "coquitts" activado
#   - Archivo de muestra de voz en la carpeta: speakers/muestra.wav
#   - Modelo XTTS descargado (se hace automáticamente al primer uso)
#
# Uso:
#   python server.py
#   Luego abrir: http://127.0.0.1:5001
# =============================================================================

import io
import os
import traceback

import numpy as np
import soundfile as sf
from flask import Flask, render_template, request, send_file
from TTS.api import TTS

# -----------------------------------------------------------------------------
# Configuración
# -----------------------------------------------------------------------------

# Ruta base del proyecto (la carpeta donde está este script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta al archivo WAV de muestra de voz para clonación.
# XTTS v2 usa este audio para "aprender" el timbre y reproducirlo.
SPEAKER_WAV = os.path.join(BASE_DIR, "speakers", "muestra.wav")

# Idioma de síntesis. XTTS v2 soporta español nativo.
LANGUAGE = "es"

# Puerto del servidor
PORT = 5001

# -----------------------------------------------------------------------------
# Inicialización del modelo
# -----------------------------------------------------------------------------

print("=" * 60)
print("  LANKAMAR TTS — Iniciando...")
print("=" * 60)

# Verificación temprana: si no existe el archivo de muestra, avisamos
# antes de cargar el modelo (que tarda varios segundos).
if not os.path.exists(SPEAKER_WAV):
    print(f"[ADVERTENCIA] No se encontró la muestra de voz en:")
    print(f"  {SPEAKER_WAV}")
    print("  El servidor arrancará pero las síntesis fallarán.")
    print("  Colocá tu archivo WAV en server/speakers/muestra.wav")
    print()

print("[1/2] Cargando modelo XTTS v2 (puede tardar 15-30 segundos)...")

# TTS carga el modelo XTTS v2 multilingual.
# progress_bar=False evita que llene la consola con barras de progreso.
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    progress_bar=False
)

print("[2/2] Modelo listo.")
print()

# -----------------------------------------------------------------------------
# Aplicación Flask
# -----------------------------------------------------------------------------

# Flask busca templates en la carpeta "templates/" relativa a este script.
app = Flask(__name__, template_folder="../frontend")


@app.route("/")
def home():
    """
    Sirve la interfaz web principal.
    Al servirla desde el mismo servidor (mismo origen que /tts),
    el navegador no aplica restricciones CORS.
    """
    return render_template("index.html")


@app.route("/tts", methods=["POST"])
def sintetizar():
    """
    Endpoint principal de síntesis de voz.

    Recibe un JSON con el texto a sintetizar:
        { "text": "Hola, este es el texto que quiero escuchar." }

    Devuelve un archivo WAV con la voz generada.
    Si ocurre un error, devuelve un texto descriptivo con HTTP 500.
    """
    try:
        # --- Leer y validar la entrada ---
        data = request.get_json(silent=True) or {}
        texto = data.get("text", "").strip()

        if not texto:
            return "Error: el campo 'text' está vacío o no fue enviado.", 400

        # --- Verificar que la muestra de voz esté disponible ---
        if not os.path.exists(SPEAKER_WAV):
            return (
                f"Error: no se encontró el archivo de muestra de voz.\n"
                f"Ruta esperada: {SPEAKER_WAV}\n"
                f"Colocá tu archivo WAV en la carpeta server/speakers/",
                500
            )

        print(f"[TTS] Sintetizando: \"{texto[:60]}{'...' if len(texto) > 60 else ''}\"")

        # --- Síntesis de voz ---
        # tts.tts() devuelve una lista de floats (muestras de audio)
        # speaker_wav: indica el archivo de referencia para clonar el timbre
        # language: idioma del texto de entrada
        muestras = tts.tts(
            text=texto,
            speaker_wav=SPEAKER_WAV,
            language=LANGUAGE
        )

        # --- Convertir a WAV en memoria ---
        # Usamos un buffer en RAM (BytesIO) en lugar de escribir al disco.
        # XTTS v2 genera audio a 24000 Hz. PCM_16 es compatible con todos
        # los navegadores y reproductores.
        buffer = io.BytesIO()
        sf.write(
            buffer,
            np.array(muestras),
            samplerate=24000,
            format="WAV",
            subtype="PCM_16"
        )
        buffer.seek(0)

        print("[TTS] Audio generado correctamente.")

        # send_file transmite el buffer como respuesta HTTP con tipo audio/wav
        return send_file(buffer, mimetype="audio/wav")

    except Exception as e:
        # Capturamos cualquier error inesperado y lo devolvemos legible
        mensaje_error = f"Error interno: {str(e)}\n\n{traceback.format_exc()}"
        print(f"[ERROR] {mensaje_error}")
        return mensaje_error, 500


# -----------------------------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Servidor disponible en: http://127.0.0.1:{PORT}")
    print("Abrí esa URL en tu navegador.")
    print("Para detener el servidor: Ctrl + C")
    print()

    # debug=False: en producción nunca se usa modo debug
    # threaded=True permite atender múltiples requests sin bloquear
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
