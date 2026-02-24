# BITÁCORA — Proyecto LANKAMAR TTS

> *Versión 1.0 · Documentación Oficial del Repositorio*

---

## Contexto y Motivación

Marcelo Omar Lancry Kamycki, conocido en el ecosistema digital bajo la marca **Lankamar**, es estudiante de la Especialización en Diseño de la Enseñanza con Tecnologías, enfermero con más de tres décadas de experiencia clínica y autodidacta en inteligencia artificial y Procesamiento del Lenguaje Natural (PLN). No proviene de la programación tradicional; viene de los hospitales, de los protocolos clínicos y de la escucha atenta que exige el trato humano. Fue precisamente esa necesidad de "escucha" la que originó este desarrollo.

El problema a resolver era concreto: Lankamar interactúa intensamente con Modelos de Lenguaje Grande (LLMs) como su principal herramienta de estudio e investigación. Sin embargo, la lectura en pantalla durante horas impone un techo cognitivo. La asimilación oral posee una profundidad diferente, vital para su proceso de aprendizaje continuo.

La misión del proyecto se definió con claridad: crear un sistema de Texto a Voz (TTS) 100% offline, privado y libre de dependencias de la nube, que le permitiera escuchar las respuestas de sus LLMs. La visión a largo plazo es aún más ambiciosa: construir una voz propia e integrarla orgánicamente en su flujo de trabajo agéntico, logrando que el sistema, eventualmente, suene como él mismo.

---

## El Desarrollo Empírico

El camino hacia el producto funcional estuvo marcado por el método heurístico de ensayo y error. El primer intento fue directo: instalar Coqui TTS, la librería de síntesis de voz de código abierto más reconocida en el entorno Python. El resultado fue un muro técnico. El proyecto original había sido abandonado por sus mantenedores, y la combinación con versiones recientes de PyTorch (2.6+) generaba conflictos que se multiplicaban en cascada.

Fueron días de errores de compilación y diagnósticos exhaustivos hasta dar con un hallazgo clave: existía un fork activo mantenido por el instituto de investigación Idiap (`coqui-tts 0.25.3`), que devolvía la viabilidad al sistema. Aún así, la arquitectura presentó una nueva fricción. La librería `transformers` introducía un conflicto de dependencias adicional que obligó a realizar un downgrade táctico, fijando la versión en la `4.46.2`. Solo entonces el entorno se estabilizó.

Superada la barrera del motor, surgió un obstáculo de formato. El archivo de muestra vocal de referencia estaba en `.m4a`, formato indigerible para el modelo. Una intervención directa mediante `ffmpeg` para convertir la muestra a `.wav` resolvió la incompatibilidad. Fue en ese momento cuando ocurrió el primer hito real: el sistema generó audio con la voz de Marcelo. Breve, imperfecto, pero inconfundiblemente propio.

Para volver la herramienta interactiva, se construyó un servidor Flask básico, diseñando endpoints para el motor de clonación de alta calidad XTTS v2. Se desarrolló una interfaz HTML minimalista y funcional.

Allí apareció el problema más sutil. Al abrir el archivo `index.html` directamente en el navegador (`file://`), el documento asumía un origen `null`. Los navegadores modernos, por estrictas políticas de seguridad, bloquean peticiones `fetch` salientes desde ese origen, resultando en un infranqueable error CORS (*Cross-Origin Resource Sharing*). Tras investigar la causa raíz, la solución definitiva no fue un parche de configuración, sino un rediseño arquitectónico: servir el propio archivo HTML desde el servidor Flask, unificando el origen y eliminando el bloqueo por diseño.

---

## Hitos Técnicos

Para garantizar la reproducibilidad del laboratorio local, se documentan las variables críticas que permitieron la sinergia del ecosistema:

**Entorno de ejecución:** Windows, Python 3.11, operando bajo un entorno virtual Conda denominado `coquitts`.

**Trinidad de dependencias (Crítico):** La compatibilidad no es trivial. El sistema exige exactamente `torch==2.5.1` y `torchaudio==2.5.1` (versión máxima tolerable), junto con `transformers==4.46.2`. El motor central debe ser innegociablemente `coqui-tts==0.25.3` (Idiap fork).

**Arquitectura de Red y Audio:** El servidor Flask opera en el puerto `5001`. El modelo requiere el archivo de clonación estrictamente en formato WAV (`server/speakers/muestra.wav`), y entrega una salida de audio con un sample rate de `24000 Hz` bajo codificación `PCM_16`.

**Afinación Empírica:** Se descubrió que la fidelidad de la clonación con XTTS mejora notablemente al proveer fragmentos de audio más extensos (10 a 20 segundos) grabados en ambiente silencioso.

**Solución de Red:** El navegador no es solo un visor, tiene reglas propias. Servir el frontend y el backend desde el mismo origen `http://127.0.0.1:5001` fue la maniobra definitiva para sortear las políticas de seguridad web.

---

## Estado Actual

El sistema opera hoy de manera estable. Un único servidor Flask (activado desde el entorno conda `coquitts`) sirve la interfaz y procesa las solicitudes, entregando síntesis con el timbre y la cadencia de Marcelo.

La hoja de ruta futura está clara: refinar la muestra de voz con grabaciones más extensas, optimizar la latencia de procesamiento mediante aceleración de hardware, y automatizar el arranque completo del sistema. El objetivo final —la integración directa y automática con los flujos de trabajo de los LLMs de estudio— se mantiene como la próxima gran meta.

---

## Reflexión

Para un profesional sin formación tradicional en ingeniería de software, construir una herramienta de síntesis de voz guiado por inteligencia artificial deja una lección que los manuales técnicos rara vez enseñan: los errores en la consola no son interrupciones del proceso; **son el proceso**. Cada reinstalación fallida acotó el espacio de soluciones posibles.

Lankamar no aprendió a "picar código" en el sentido clásico. Aprendió una habilidad superior: a leer los síntomas de un sistema que falla, a formular las preguntas correctas, y a discernir entre un parche temporal y la resolución de la causa raíz. Esa metodología diagnóstica, orientada al origen del problema, es exactamente lo que la disciplina de la enfermería enseña.

Representa la victoria del pensamiento metacognitivo sobre la barrera técnica. La voz que hoy habla desde el servidor local aún es perfectible. Pero es la suya. Y en el contexto de esta reinvención profesional, eso lo es todo.

---

*Proyecto:* [lankamar/xtts-voz-clonada](https://github.com/lankamar/xtts-voz-clonada) · *Autor:* Marcelo Omar Lancry k. — Lankamar
