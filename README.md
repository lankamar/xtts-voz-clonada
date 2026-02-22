# XTTS Voz Clonada

> Servidor **XTTS v2** con clonacion de voz local, API REST con CORS, frontend web dark mode y documentacion completa de instalacion paso a paso.

---

## Que hace este proyecto

- Clona tu voz desde un audio `.wav` de referencia
- Levanta un servidor local en el puerto `5051` con API REST
- Expone un frontend web para escribir texto y escuchar el audio generado con tu voz
- CORS completamente abierto para usarlo desde cualquier pagina o herramienta

---

## Requisitos

| Requisito | Version |
|---|---|
| Python | 3.10 (exactamente) |
| GPU NVIDIA | Recomendada (CUDA 11.8+) |
| RAM | 8 GB minimo, 16 GB recomendado |
| Espacio en disco | ~5 GB (modelo + dependencias) |

> Sin GPU funciona igual con `--use-cpu`, pero la generacion es mas lenta.

---

## Instalacion

### 1. Clonar el repo

```bash
git clone https://github.com/lankamar/xtts-voz-clonada.git
cd xtts-voz-clonada
```

### 2. Instalar dependencias

**Linux / Mac / WSL:**
```bash
chmod +x setup.sh start_server.sh
./setup.sh
```

**Windows:**
```batch
setup.bat
```

El script hace todo automaticamente:
- Crea entorno virtual `venv/` con Python 3.10
- Instala PyTorch con CUDA 11.8
- Instala `xtts-api-server` y todas las dependencias
- Crea las carpetas `server/speakers/` y `output/`

### 3. Agregar tu audio de referencia

Copia tu archivo de voz a:
```
server/speakers/TU_NOMBRE.wav
```

Requisitos del audio:
- Formato: WAV, PCM
- Canales: Mono
- Sample rate: 22050 Hz (o 44100 Hz)
- Duracion: **minimo 6 segundos**, idealmente 10-30 seg
- Sin ruido de fondo

> Podés convertir cualquier audio con [Audacity](https://www.audacityteam.org/) (gratis).

---

## Uso

### Levantar el servidor

**Linux / Mac / WSL:**
```bash
./start_server.sh
```

**Windows:**
```batch
start_server.bat
```

El servidor queda en:
- **API**: `http://localhost:5051`
- **Documentacion Swagger**: `http://localhost:5051/docs`

### Abrir el frontend

```bash
cd frontend
python -m http.server 8080
```

Entrar a `http://localhost:8080` en el navegador.

> Importante: abrir el frontend desde un servidor HTTP, NO desde `file://`, para evitar errores de CORS.

---

## Endpoints API

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/speakers` | Lista los archivos de voz disponibles |
| POST | `/tts_to_audio` | Genera WAV con voz clonada |
| POST | `/tts_stream` | Streaming de audio en tiempo real |
| POST | `/set_tts_settings` | Cambia configuracion (idioma, temperatura, etc) |

### Ejemplo de llamada

```javascript
fetch('http://127.0.0.1:5051/tts_to_audio', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hola, soy Marcelo.',
    speaker_wav: 'marcelo',  // nombre del .wav sin extension
    language: 'es'
  })
})
.then(r => r.blob())
.then(b => new Audio(URL.createObjectURL(b)).play());
```

---

## Idiomas soportados por XTTS v2

`es` `en` `pt` `fr` `de` `it` `pl` `ru` `nl` `cs` `ar` `zh-cn` `ja` `hu` `ko` `tr`

---

## Estructura del repositorio

```
extts-voz-clonada/
├── .gitignore              # Excluye venv, modelos, audios privados
├── LICENSE                 # MIT
├── README.md
├── requirements.txt        # Dependencias Python
├── setup.sh                # Instalacion Linux/Mac/WSL
├── setup.bat               # Instalacion Windows
├── start_server.sh         # Arranque del servidor Linux/Mac
├── start_server.bat        # Arranque del servidor Windows
├── server/
│   └── speakers/           # Tus archivos .wav de referencia (NO versionados)
├── output/                 # Audios generados (NO versionados)
└── frontend/
    └── index.html          # Interfaz web dark mode
```

---

## Flags utiles del servidor

```bash
# Sin GPU
--use-cpu

# Acelerar con DeepSpeed (GPU compatible)
--deepspeed

# Cambiar puerto
--port 5051

# Habilitar CORS (siempre incluirlo para uso desde browser)
--cors
```

---

## Autor

**Marcelo Omar Lancry Kamycki** (LANKAMAR)  
Licenciado en Enfermeria | IA aplicada a salud y educacion  
Hospital de Clinicas — Universidad de Buenos Aires  

[github.com/lankamar](https://github.com/lankamar)

---

## Licencia

MIT License — libre para uso personal y comercial.
