# JobSpeed

Sistema automático de búsqueda y análisis de compatibilidad de ofertas de empleo.

## 📋 Descripción

JobSpeed automatiza la búsqueda de ofertas laborales, extrae datos relevantes y calcula la compatibilidad con el perfil del usuario, optimizando tiempo y precisión en la búsqueda de empleo.

## 🛠️ Tecnologías

### Lenguaje Principal
- **Python** - Procesamiento de datos, scraping, análisis de texto y automatización

### Módulo Collector (Búsqueda)
- **Requests** - Obtención de páginas web
- **BeautifulSoup** - Extracción de HTML
- **Playwright** - Páginas dinámicas (futuro)

### Módulo Parser (Extracción)
- **BeautifulSoup** - Análisis HTML
- **Regex** - Extracción de patrones
- **Python** - Normalización de datos

### Módulo Matcher (Compatibilidad)
- **Python** - Lógica de comparación
- **JSON** - Almacenamiento de skills

### Almacenamiento
- **CSV** - Base de datos inicial
- **SQLite/PostgreSQL** - Almacenamiento persistente (futuro)

### Futuro
- **FastAPI** - Backend REST API
- **React** - Frontend web
- **SMTP/Gmail API** - Envío automático de postulaciones

## ⚙️ Ejecución

El sistema se ejecuta mediante tareas programadas (cron jobs) para actualización automática diaria del catálogo de ofertas.

---

**Versión:** 1.0 (Sprint Inicial)  
**Estado:** En desarrollo
