# Declaración de Uso de Inteligencia Artificial

## 1. Propósito

Durante el desarrollo de SmartBancs App se utilizaron herramientas de inteligencia artificial como apoyo para diferentes actividades de análisis, diseño, programación, generación de datos de prueba, documentación y revisión.

Las herramientas de IA fueron utilizadas como asistentes durante el desarrollo. La arquitectura, las decisiones técnicas, la implementación final, las pruebas, la validación de resultados y la gestión del repositorio fueron realizadas y revisadas por el autor.

---

## 2. Herramientas utilizadas

### ChatGPT

ChatGPT fue utilizado como apoyo durante diferentes etapas del desarrollo del proyecto:

* Análisis e interpretación del reto técnico.
* Análisis y comparación de alternativas de arquitectura.
* Diseño y organización de la estructura de la base de datos.
* Explicación de conceptos técnicos como PostgreSQL, concurrencia, `SELECT FOR UPDATE`, Transactional Outbox y Workers.
* Definición y revisión del flujo de integración con Bancs.
* Diseño de pruebas y análisis de sus resultados.
* Apoyo en observabilidad, métricas y diagnóstico de incidentes.
* Revisión de errores encontrados durante el desarrollo.
* Elaboración y revisión de diagramas de arquitectura y modelo entidad-relación.
* Apoyo en la redacción y organización de la documentación técnica.
* Sugerencias para presentar los resultados y evidencias del proyecto.

La documentación generada con este apoyo fue redactada a partir de las decisiones técnicas, implementaciones y resultados reales obtenidos durante el desarrollo. El contenido fue revisado por el autor antes de incorporarlo al proyecto.

### GitHub Copilot

GitHub Copilot fue utilizado como asistente de programación, principalmente para el desarrollo en Python.

Su uso incluyó:

* Autocompletado y generación de código.
* Creación de funciones y estructuras auxiliares.
* Apoyo en la implementación de lógica para los diferentes componentes.
* Sugerencias para mejorar la legibilidad y organización del código.
* Apoyo en criterios de Clean Code.
* Sugerencias relacionadas con validaciones y prácticas básicas de seguridad.

El código sugerido por Copilot no fue incorporado de forma automática sin revisión. El autor comprendió la lógica utilizada, revisó las sugerencias, realizó modificaciones cuando fue necesario y ejecutó pruebas para validar su funcionamiento.

Copilot fue utilizado principalmente como una herramienta para acelerar la programación, manteniendo el control sobre el código y su comportamiento.

### Claude

Claude fue utilizado para generar datos transaccionales simulados utilizados en las pruebas del proceso ETL y también para generar el diagrama entidad-relación de la base de datos a partir del script SQL.

Boceto y diseño inicial de la presentación.

Los datos generados representan información ficticia creada específicamente para probar y demostrar el flujo:

`RAW → ETL → datos limpios/rechazados → análisis`

Los datos fueron revisados antes de ser utilizados y no corresponden a información financiera real.

### Gemini API

Gemini forma parte de la implementación funcional del proyecto y no solamente del proceso de desarrollo.

Se utiliza mediante un AI Worker independiente para generar recomendaciones de forma asíncrona.

El flujo implementado es:

`Base de datos → AI Worker → Gemini API → ai_recommendations`

El procesamiento de IA se encuentra fuera del flujo crítico de las transferencias. Por esta razón, una falla, indisponibilidad o límite de cuota de Gemini no impide la confirmación de una transferencia en la base de datos.

---

## 3. Áreas en las que se utilizó IA

Las herramientas de IA fueron utilizadas como apoyo en las siguientes áreas:

* Análisis del requerimiento.
* Diseño y evaluación de arquitectura.
* Diseño de base de datos.
* Desarrollo de código Python.
* Revisión y mejora de código.
* Generación de datos simulados para pruebas.
* Diseño de diagramas.
* Diseño y análisis de pruebas.
* Análisis de errores.
* Observabilidad y métricas.
* Diagnóstico de problemas de concurrencia y base de datos.
* Redacción y organización de documentación técnica.

La utilización de IA estuvo orientada principalmente a acelerar tareas de desarrollo y facilitar el análisis de alternativas. Las decisiones finales se tomaron considerando las necesidades del reto, el alcance del MVP y los resultados obtenidos durante las pruebas.

---

## 4. Documentación y fuentes técnicas

Durante el desarrollo también se consultaron documentación técnica y fuentes oficiales relacionadas con las tecnologías utilizadas.

Entre ellas:

* Docker Hub para consultar imágenes y configuraciones de contenedores.
* Documentación de Python.
* Documentación de FastAPI.
* Documentación de PostgreSQL.
* Documentación de Pandas.
* Documentación de Prometheus.
* Documentación de Grafana.
* Documentación relacionada con la API de Gemini.

Estas fuentes fueron utilizadas como referencia técnica para comprender el funcionamiento, configuración y buenas prácticas de las tecnologías empleadas.

La consulta de documentación técnica fue complementaria al uso de herramientas de IA.

---

## 5. Responsabilidad y validación

El autor fue responsable de la implementación, configuración, ejecución y validación final del proyecto.

Esto incluyó:

* Seleccionar la arquitectura y las tecnologías utilizadas.
* Definir la estructura de la base de datos.
* Implementar e integrar los diferentes servicios.
* Configurar Docker Compose.
* Ejecutar los servicios.
* Realizar consultas y validaciones en PostgreSQL.
* Ejecutar las pruebas de concurrencia.
* Ejecutar las pruebas de carga.
* Implementar y validar el flujo Transactional Outbox.
* Implementar y validar el Worker de integración con Bancs Mock.
* Implementar y validar el proceso ETL.
* Configurar y revisar Prometheus y Grafana.
* Realizar la prueba controlada de bloqueo y timeout de PostgreSQL.
* Revisar y adaptar el código generado o sugerido por herramientas de IA.
* Revisar la estructura, ortografía y contenido de la documentación.
* Validar que las evidencias presentadas correspondieran con el comportamiento real del sistema.

---

## 6. Git y GitHub

Todo el trabajo relacionado con el control de versiones y la gestión del repositorio fue realizado por el autor.

Esto incluyó:

* Creación y gestión de ramas.
* Realización de commits.
* Uso de merges.
* Resolución de cambios y conflictos cuando fue necesario.
* Organización de la estructura del repositorio.
* Configuración de archivos del proyecto.
* Publicación del código mediante `push`.
* Revisión del contenido publicado.
* Preparación de la entrega final en GitHub.

Las herramientas de IA pudieron ser consultadas para aclarar comandos, convenciones o buenas prácticas de Git cuando fue necesario, pero las operaciones sobre el repositorio fueron ejecutadas y controladas por el autor.

---

## 7. Documentación del proyecto

ChatGPT también fue utilizado como apoyo para redactar y organizar parte de la documentación del proyecto.

La redacción se realizó tomando como base las decisiones, implementaciones y resultados obtenidos durante el desarrollo. El autor proporcionó la información del proyecto, revisó el contenido generado y realizó las modificaciones necesarias para que la documentación representara correctamente la solución implementada.

La documentación no se utilizó para reemplazar la comprensión de la solución, sino como apoyo para expresar de manera clara las decisiones y resultados técnicos.

---

## 8. Control sobre las decisiones técnicas

Las herramientas de IA fueron utilizadas para explicar conceptos, analizar alternativas, sugerir implementaciones y acelerar determinadas tareas.

Sin embargo, las decisiones finales sobre:

* Arquitectura.
* Tecnologías.
* Modelo de datos.
* Flujo transaccional.
* Uso de Transactional Outbox.
* Integración asíncrona con Bancs.
* Separación del AI Worker.
* Estrategia de observabilidad.
* Pruebas realizadas.
* Alcance del MVP.

fueron tomadas por el autor.

El autor revisó y validó las propuestas antes de incorporarlas al proyecto.

---

## 9. Declaración final

La inteligencia artificial fue utilizada como herramienta de apoyo durante el desarrollo de SmartBancs App, principalmente para facilitar el análisis, acelerar la programación, generar datos de prueba y apoyar la documentación.

El autor mantuvo el control sobre el desarrollo del proyecto, comprendiendo y revisando el código utilizado, tomando las decisiones técnicas, ejecutando las pruebas, validando los resultados y realizando directamente la gestión del repositorio y la entrega final.

La solución presentada corresponde a la implementación y validación realizadas por el autor con apoyo de las herramientas y fuentes técnicas descritas en este documento.
