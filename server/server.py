# =============================================================================
# LANKAMAR TTS — Servidor de Síntesis de Voz v2
# =============================================================================
# Autor     : Marcelo Omar Lancry k. (Lankamar)
# Proyecto  : xtts-voz-clonada
# Puerto    : 5001
# Motor     : XTTS v2 (Coqui TTS — fork Idiap)
#
# Novedades v2:
#   - Soporte de múltiples fragmentos de voz para mejor clonación de acento
#   - Parser SSML básico: respeta pausas (<break>) y velocidad (<prosody rate>)
#   - La lista de fragmentos permite que XTTS construya un embedding de voz
#     más robusto, reduciendo la deriva hacia el acento inglés del modelo base
#
# Uso:
#   python server.py
#   Luego abrir: http://127.0.0.1:5001
# =============================================================================

import io
import os
import re
import traceback
import xml.etree.ElementTree as ET

import numpy as np
import soundfile as sf
from flask import Flask, render_template, request, send_file
from TTS.api import TTS

# -----------------------------------------------------------------------------
# Configuración
# -----------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOZ_DIR  = os.path.join(BASE_DIR, "speakers")

# Lista de fragmentos de voz para clonación.
# XTTS v2 acepta una lista de archivos WAV: construye un embedding promedio
# de todos ellos, lo que da mayor estabilidad al acento y al timbre.
SPEAKER_WAVS = [
    os.path.join(VOZ_DIR, "muestra_01.wav"),
    os.path.join(VOZ_DIR, "muestra_02.wav"),
    os.path.join(VOZ_DIR, "muestra_03.wav"),
    os.path.join(VOZ_DIR, "muestra_04.wav"),
]

# Si no hay fragmentos, fallback a la muestra completa
FALLBACK_WAV = os.path.join(VOZ_DIR, "muestra.wav")

LANGUAGE = "es"
PORT     = 5001

# Frecuencia de muestreo de salida de XTTS v2
SAMPLE_RATE = 24000

# -----------------------------------------------------------------------------
# Parser SSML básico
# -----------------------------------------------------------------------------

def parsear_ssml(texto_entrada):
    """
    Convierte SSML a una lista de segmentos procesables.

    Cada segmento es un dict con:
        - 'type': 'text' | 'silence'
        - 'content': texto a sintetizar (si es 'text')
        - 'duration_ms': milisegundos de silencio (si es 'silence')
        - 'speed': factor de velocidad (0.5 a 2.0, default 1.0)

    Etiquetas SSML soportadas:
        <speak>         — contenedor raíz, ignorado
        <break>         — inserta silencio. Atributo: time="400ms"
        <prosody rate>  — velocidad. Valores: "slow"|"fast"|"95%"|"1.2"
        <emphasis>      — ignorada (XTTS no tiene control de énfasis)
        <sub alias>     — usa el alias como texto
        <p>, <s>        — añaden pausa natural (como <break time="500ms">)

    Si el texto de entrada NO contiene etiquetas XML, se devuelve el texto
    tal cual como un único segmento de texto con velocidad normal.
    """
    if "<" not in texto_entrada:
        return [{"type": "text", "content": texto_entrada, "speed": 1.0}]

    segmentos = []

    try:
        xml_str = texto_entrada.strip()
        if not xml_str.startswith("<speak"):
            xml_str = f"<speak>{xml_str}</speak>"

        raiz = ET.fromstring(xml_str)
        _extraer_segmentos(raiz, segmentos, speed_actual=1.0)

    except ET.ParseError:
        texto_limpio = re.sub(r"<[^>]+>", " ", texto_entrada)
        texto_limpio = " ".join(texto_limpio.split())
        return [{"type": "text", "content": texto_limpio, "speed": 1.0}]

    return segmentos


def _extraer_segmentos(elemento, segmentos, speed_actual):
    """Recorre el árbol XML recursivamente extrayendo texto y silencios."""

    if elemento.text and elemento.text.strip():
        segmentos.append({
            "type": "text",
            "content": elemento.text.strip(),
            "speed": speed_actual
        })

    for hijo in elemento:
        tag = hijo.tag.lower()

        if tag == "break":
            time_str = hijo.get("time", "250ms")
            ms = _parsear_tiempo(time_str)
            segmentos.append({"type": "silence", "duration_ms": ms})

        elif tag == "prosody":
            rate_attr = hijo.get("rate", "")
            nueva_speed = _parsear_rate(rate_attr, speed_actual)
            _extraer_segmentos(hijo, segmentos, nueva_speed)

        elif tag == "sub":
            alias = hijo.get("alias", "")
            if alias:
                segmentos.append({
                    "type": "text",
                    "content": alias,
                    "speed": speed_actual
                })

        elif tag in ("p", "s"):
            _extraer_segmentos(hijo, segmentos, speed_actual)
            segmentos.append({"type": "silence", "duration_ms": 400})

        else:
            _extraer_segmentos(hijo, segmentos, speed_actual)

        if hijo.tail and hijo.tail.strip():
            segmentos.append({
                "type": "text",
                "content": hijo.tail.strip(),
                "speed": speed_actual
            })


def _parsear_tiempo(time_str):
    """Convierte '400ms' o '0.4s' a milisegundos enteros."""
    time_str = time_str.strip().lower()
    if time_str.endswith("ms"):
        return int(float(time_str[:-2]))
    elif time_str.endswith("s"):
        return int(float(time_str[:-1]) * 1000)
    return 250


def _parsear_rate(rate_str, speed_actual):
    """
    Convierte el atributo rate de <prosody> a un factor numérico.
    Ejemplos: "slow" -> 0.75 | "fast" -> 1.25 | "95%" -> 0.95 | "1.2" -> 1.2
    """
    rate_str = rate_str.strip().lower()
    mapa = {"x-slow": 0.5, "slow": 0.75, "medium": 1.0,
            "fast": 1.25, "x-fast": 1.5}
    if rate_str in mapa:
        return mapa[rate_str]
    if rate_str.endswith("%"):
        try:
            return float(rate_str[:-1]) / 100
        except ValueError:
            pass
    try:
        return float(rate_str)
    except ValueError:
        return speed_actual


# -----------------------------------------------------------------------------
# Inicialización del modelo
# -----------------------------------------------------------------------------

print("=" * 60)
print("  LANKAMAR TTS v2 — Iniciando...")
print("=" * 60)

wavs_disponibles = [w for w in SPEAKER_WAVS if os.path.exists(w)]
if not wavs_disponibles:
    if os.path.exists(FALLBACK_WAV):
        wavs_disponibles = [FALLBACK_WAV]
        print(f"[VOZ] Usando muestra unica: {FALLBACK_WAV}")
    else:
        print("[ADVERTENCIA] No se encontro ningun archivo de muestra de voz.")
else:
    print(f"[VOZ] Usando {len(wavs_disponibles)} fragmentos de voz para clonacion.")

print("[1/2] Cargando modelo XTTS v2...")

tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    progress_bar=False
)

print("[2/2] Modelo listo.")
print()

# -----------------------------------------------------------------------------
# Aplicación Flask
# -----------------------------------------------------------------------------

app = Flask(__name__, template_folder="../frontend")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tts", methods=["POST"])
def sintetizar():
    """
    Sintetiza texto plano o SSML a audio WAV.

    Entrada JSON: { "text": "texto o <speak>SSML</speak>" }
    Salida: archivo WAV con la voz clonada.

    Flujo:
      1. Deteccion automatica de SSML vs texto plano
      2. Sintesis segmento por segmento
      3. Insercion de silencios reales para <break>
      4. Concatenacion y devolucion del WAV final
    """
    try:
        data  = request.get_json(silent=True) or {}
        texto = data.get("text", "").strip()

        if not texto:
            return "Error: campo 'text' vacio.", 400

        if not wavs_disponibles:
            return "Error: no hay archivos de muestra de voz configurados.", 500

        print(f"[TTS] Input: \"{texto[:70]}{'...' if len(texto) > 70 else ''}\"")

        segmentos = parsear_ssml(texto)
        print(f"[TTS] {len(segmentos)} segmentos detectados.")

        audio_total = np.array([], dtype=np.float32)

        for i, seg in enumerate(segmentos):
            if seg["type"] == "silence":
                ms       = seg["duration_ms"]
                samples  = int(SAMPLE_RATE * ms / 1000)
                silencio = np.zeros(samples, dtype=np.float32)
                audio_total = np.concatenate([audio_total, silencio])
                print(f"  [{i+1}] Silencio: {ms}ms")

            elif seg["type"] == "text":
                contenido = seg["content"]
                speed     = seg.get("speed", 1.0)

                if not contenido:
                    continue

                print(f"  [{i+1}] Texto (speed={speed:.2f}): \"{contenido[:50]}\"")

                wavs_input = wavs_disponibles if len(wavs_disponibles) > 1 else wavs_disponibles[0]

                muestras = tts.tts(
                    text=contenido,
                    speaker_wav=wavs_input,
                    language=LANGUAGE,
                    speed=speed
                )

                audio_total = np.concatenate([audio_total, np.array(muestras, dtype=np.float32)])

        buffer = io.BytesIO()
        sf.write(buffer, audio_total, samplerate=SAMPLE_RATE,
                 format="WAV", subtype="PCM_16")
        buffer.seek(0)

        print("[TTS] Audio generado correctamente.")
        return send_file(buffer, mimetype="audio/wav")

    except Exception as e:
        error_msg = f"Error interno: {str(e)}\n\n{traceback.format_exc()}"
        print(f"[ERROR] {error_msg}")
        return error_msg, 500


# -----------------------------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Servidor disponible en: http://127.0.0.1:{PORT}")
    print("Abri esa URL en tu navegador.")
    print("Para detener: Ctrl + C")
    print()
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
