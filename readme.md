# FarmaControl - Sistema de Gestión e Inventario para Farmacias

**FarmaControl** es una plataforma web diseñada para centralizar la gestión de inventario y optimizar el análisis de ventas en farmacias. El sistema automatiza la recolección, limpieza y consolidación de datos provenientes de archivos Excel y CSV, transformándolos en métricas clave y gráficos interactivos para facilitar la toma de decisiones.

<!-- Badges de Tecnologías y Estado -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Pandas-ETL-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" alt="Status">
</p>

---

## Índice de Contenidos
- [Objetivos del Proyecto](#objetivos-del-proyecto)
- [Características Principales](#características-principales)
- [Arquitectura Tecnológica](#arquitectura-tecnológica)
- [Autor](#autor)
  
---

## Objetivos del Proyecto

* **Centralización de datos:** Reunir la información de ventas y compras en un único almacén de datos.
* **Automatización ETL:** Eliminar el procesamiento manual de reportes mediante la carga automática de archivos de datos.
* **Análisis visual:** Ofrecer herramientas dinámicas para evaluar el rendimiento comercial y consultar historiales de precios.
* **Seguridad y eficiencia:** Garantizar un acceso protegido a la información sensible del negocio.

---

## Características Principales

### 1. Autenticación y Seguridad
* **Control de acceso:** Sistema de registro e inicio de sesión protegido mediante tokens JWT.
* **Protección de datos:** Cifrado seguro de contraseñas con la librería bcrypt.
* **Persistencia:** Gestión de sesiones de usuario en el navegador a través de localStorage.

### 2. Dashboard Analítico
* **Métricas comerciales:** Monitoreo del volumen de ventas agrupado por periodos diarios, mensuales y anuales.
* **Filtros avanzados:** Segmentación de reportes mediante rangos de fechas personalizables.
* **Gráficos interactivos:** Visualizaciones dinámicas integradas con Plotly.js.
* **Búsqueda inteligente:** Motor de consulta de productos y precios con autocompletado en tiempo real.

### 3. Automatización de Datos (Pipeline ETL)
* **Procesamiento asíncrono:** Tareas de fondo que se ejecutan al iniciar el servidor sin interrumpir la experiencia de usuario.
* **Ingesta de archivos:** Soporte para la extracción de información desde archivos en formato Excel y CSV.
* **Limpieza automatizada:** Normalización y filtrado de datos mediante la biblioteca pandas antes de su almacenamiento definitivo.

---

## Arquitectura Tecnológica

### Backend (Python 3.9+)
* **FastAPI:** Framework principal para la construcción de una API REST asíncrona de alto rendimiento.
* **PostgreSQL:** Base de datos relacional encargada del almacenamiento seguro del catálogo e historial.
* **SQLAlchemy:** Mapeo de objetos relacionales (ORM) para la comunicación eficiente con la base de datos.
* **Uvicorn:** Servidor ASGI para el despliegue de la aplicación en entornos de desarrollo y producción.

### Frontend (Desarrollo Nativo)
* **HTML5 y CSS3:** Estructura web y diseño adaptivo (responsive) para dispositivos móviles y de escritorio.
* **JavaScript (ES6+):** Lógica del cliente, manejo del estado de autenticación y llamadas asíncronas mediante Fetch API.
* **Plotly.js:** Biblioteca especializada para el renderizado de gráficos estadísticos en el dashboard.

---

## Autor

Desarrollado por **José Aníbal Modad**  
* **GitHub:** [@turkoModad](https://github.com/turkoModad)
* **Enfoque:** Desarrollo Full-Stack, Pipelines ETL, APIs de Alto Rendimiento y Analítica de Datos.
