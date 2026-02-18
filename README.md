# JobSpeed

Sistema automático de búsqueda y análisis de compatibilidad de ofertas de empleo.

## 📋 Descripción

JobSpeed automatiza la búsqueda de ofertas laborales, extrae datos relevantes y calcula la compatibilidad con el perfil del usuario, optimizando tiempo y precisión en la búsqueda de empleo.

## 🛠️ Tecnologías

### Lenguaje Principal
- **Python** - Procesamiento de datos, scraping, análisis de texto y automatización

### Módulo Collector (Búsqueda) - Sprint 1 ✅
- **Requests** - Obtención de páginas web
- **BeautifulSoup** - Extracción de HTML
- **Selenium** - Páginas dinámicas (LinkedIn)

### Módulo Parser (Extracción) - Sprint 1 ✅
- **BeautifulSoup** - Análisis HTML
- **Regex** - Extracción de patrones
- **Python** - Normalización de datos

### Módulo Database (Persistencia) - Sprint 2 ✅
- **SQLite** - Base de datos relacional
- 6 tablas normalizadas (Usuario, Skills, Certificados, etc)

### Módulo Matcher (Compatibilidad) - Sprint 2 ✅
- **Python** - Matching inteligente de skills
- **Difflib** - Búsqueda difusa similar
- Análisis automático de compatibilidad

### Almacenamiento
- **CSV** - Base de datos inicial (Sprint 1)
- **SQLite** - Almacenamiento persistente (Sprint 2) ✅

### Futuro
- **FastAPI** - Backend REST API (Sprint 3)
- **React** - Frontend web (Sprint 3)
- **SMTP/Gmail API** - Envío automático de postulaciones

## ⚙️ Ejecución

El sistema se ejecuta mediante tareas programadas (cron jobs) para actualización automática diaria del catálogo de ofertas.

---

**Versión:** 2.0 (Sprint 2)  
**Estado:** En desarrollo (Database & Matcher completado ✅)
