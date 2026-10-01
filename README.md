# Inglés diagnóstico para bachillerato

Material educativo del Instituto Fernando Ramírez para consultar y practicar contenidos básicos de inglés en bachillerato.

## Sitios del proyecto

- Aplicación principal: <https://ingles-bachillerato-diagnostico.vercel.app/>
- Actividad del 2 de julio de 2026: <https://ingles-bachillerato-diagnostico.vercel.app/Actividad%202-julio-2026/Actividad.html>
- Repositorio: <https://github.com/raulmormen75/ingles_bachillerato_diagnostico>

## Contenido

- `index.html`: aplicación principal con los 13 temas de inglés diagnóstico.
- `Actividad 2-julio-2026/Actividad.html`: actividad independiente para estudiantes.
- `Contenido de clase diagnóstico.txt`: contenido académico de apoyo.
- `Temario de inglés.txt`: estructura temática del curso.
- `parse_content.py`: auxiliar para procesar el contenido.
- Archivos SVG y JPG: recursos visuales institucionales.

La aplicación conserva 13 temas. El contenido de apoyo y el temario tienen 17 apartados: la aplicación reúne los apartados 5 a 9 en el tema de presentaciones. No se debe regenerar `index.html` automáticamente con `parse_content.py`, porque se perdería esta organización y los ajustes de la aplicación.

## Audio

La voz es Heart (`af_heart`), generada localmente con Kokoro v1.0, idioma `en-us` y velocidad de generación `0.9`. Los archivos WAV de `assets/audio/` son mono, 24 000 Hz y PCM16. No se necesita una API ni una voz instalada en el dispositivo. Se reproduce solo el texto inglés asociado, no su traducción ni la guía de pronunciación.

`assets/heart-player.js` comparte un único reproductor para evitar superposiciones. Permite detener, repetir y cambiar la velocidad sin modificar el tono. Se detiene al cambiar de tema o abandonar la página. Los ejercicios de deletreo, secuencias y contrastes de letras individuales no tienen controles de reproducción; se conservan sus textos para trabajar con el profesor. La actividad de julio utiliza el mismo reproductor.

Para actualizar audios después de editar contenido:

1. Servir la raíz por HTTP en `127.0.0.1:8765` y abrir una sesión de Playwright CLI llamada `heart`.
2. Ejecutar `node scripts/collect-heart-jobs.cjs` para inventariar los botones de ambas páginas.
3. Ejecutar `scripts/generate_heart.py` con el entorno local de Python que contiene `kokoro-onnx`, `onnxruntime`, `numpy` y `soundfile`. Indicar `--model-dir` con la carpeta de `kokoro-v1.0.onnx` y `voices-v1.0.bin`. `--limit 1` permite generar una muestra.
4. Comprobar que `assets/audio/manifest.json` indique `complete: true`, validar la reproducción y publicar los WAV junto con ambos manifiestos. El generador reutiliza archivos solo si coinciden texto, configuración y SHA-256; cada URL de audio incorpora su hash para evitar copias anteriores en caché.

Los modelos y el entorno de generación no se publican. El manifiesto conserva texto, configuración, duración y hash de cada audio. Las pruebas con una ventana estrecha no sustituyen una prueba en un teléfono físico.

## Actualización y publicación

1. Realizar los cambios en la copia local del repositorio.
2. Revisar la aplicación en computadora y celular.
3. Registrar los cambios y enviarlos a la rama `main` de GitHub.
4. Vercel publica automáticamente la versión de producción.
5. Confirmar que las direcciones públicas funcionen y correspondan al cambio enviado.

Los archivos temporales de comprobación, la configuración local de Vercel y los programas auxiliares descartables permanecen fuera del repositorio mediante `.gitignore`.
