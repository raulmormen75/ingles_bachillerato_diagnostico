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

Se conserva la selección de voz anterior: primero se buscan las voces femeninas preferidas, como Jenny; si no están disponibles, se utilizan las alternativas en inglés que ofrece el navegador. No se bloquea la reproducción por el nombre de la voz. La voz concreta depende del navegador y de las voces disponibles en el dispositivo. Los botones deben reproducir el texto inglés que tienen asociado, no la traducción ni la ayuda de pronunciación.

## Actualización y publicación

1. Realizar los cambios en la copia local del repositorio.
2. Revisar la aplicación en computadora y celular.
3. Registrar los cambios y enviarlos a la rama `main` de GitHub.
4. Vercel publica automáticamente la versión de producción.
5. Confirmar que las direcciones públicas funcionen y correspondan al cambio enviado.

Los archivos temporales de comprobación, la configuración local de Vercel y los programas auxiliares descartables permanecen fuera del repositorio mediante `.gitignore`.
