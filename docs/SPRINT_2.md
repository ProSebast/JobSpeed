# 📖 Guía Sprint 2 - JobSpeed Database & Matcher

## Resumen Sprint 2

El Sprint 2 introduce la funcionalidad principal del proyecto: una **base de datos de perfiles de usuarios** y un **sistema inteligente de matching** que compara las habilidades de los usuarios con las ofertas de empleo extraídas.

### ✅ Completado en Sprint 2

- ✅ **Módulo Database** - Gestión completa de BD SQLite con 6 tablas relacionadas
- ✅ **Módulo Matcher** - Sistema de compatibilidad de skills con análisis inteligente
- ✅ **Datos de Ejemplo** - 2 perfiles: Informática (5 certificados) y Pedagogía (4 certificados)
- ✅ **Sistema de Ranking** - Ordenamiento automático de ofertas por compatibilidad

---

## 📊 Arquitectura de Base de Datos

### Esquema Relacional

```
USUARIOS
├── id (PK)
├── nombre
├── carrera
└── fecha_creacion

SKILLS
├── id (PK)
├── nombre_skill (python, SQL, etc)
└── categoria (backend, databases, etc)

CERTIFICADOS
├── id (PK)
├── nombre_certificado
└── institucion

CERTIFICADO_SKILL (N:N)
├── id (PK)
├── certificado_id (FK)
└── skill_id (FK)

CERTIFICADOS_USUARIO
├── id (PK)
├── usuario_id (FK)
├── certificado_id (FK)
└── fecha_obtencion

SKILL_USUARIO
├── id (PK)
├── usuario_id (FK)
├── skill_id (FK)
├── nivel (junior|mid|senior)
├── años_experiencia
└── origen (certificado|experiencia|proyecto)
```

### Ventajas del Diseño

- **Normalización**: Evita redundancia de datos
- **Flexibilidad**: Se pueden agregar nuevos certificados/skills fácilmente
- **Tracking**: Registra el origen y nivel de cada skill
- **Escalabilidad**: Diseño listo para múltiples usuarios

---

## 🛠️ Módulos Creados

### 1. **src/database.py** - DatabaseManager

Gestor completo de la base de datos SQLite.

#### Operaciones Principales

```python
from src.database import DatabaseManager

db = DatabaseManager()  # Conecta a data/jobspeed.db

# USUARIOS
usuario_id = db.agregar_usuario("Juan Pérez", "Informática")
usuario = db.obtener_usuario(usuario_id)

# SKILLS
skill_id = db.agregar_skill("python", "Lenguajes")

# CERTIFICADOS
cert_id = db.agregar_certificado("Licenciatura en Informática", "Universidad")

# ASOCIACIONES
db.asociar_certificado_skill(cert_id, skill_id)
db.agregar_certificado_usuario(usuario_id, cert_id)
db.agregar_skill_usuario(usuario_id, skill_id, nivel='senior', años_experiencia=5)

# CONSULTAS
perfil = db.obtener_perfil_completo(usuario_id)  # Usuario + skills + certificados
skills = db.obtener_skills_usuario(usuario_id)
certificados = db.obtener_certificados_usuario(usuario_id)

db.cerrar()
```

**Métodos Disponibles:**
- `crear_tablas()` - Crea esquema inicial
- `agregar_usuario()` - Registra nuevo usuario
- `obtener_perfil_completo()` - Perfil integrado del usuario
- `obtener_skills_usuario()` - Lista de skills con detalles
- `obtener_certificados_usuario()` - Certificados obtenidos
- `limpiar_base_datos()` - Reinicia todo (testing)

---

### 2. **src/matcher.py** - Matcher

Sistema inteligente de matching entre usuarios y ofertas.

#### Operaciones Principales

```python
from src.database import DatabaseManager
from src.matcher import Matcher

db = DatabaseManager()
matcher = Matcher(db)

# Oferta de ejemplo
oferta = {
    "titulo": "Senior Python Developer",
    "empresa": "Tech Corp",
    "descripcion": "Buscamos Python, Docker, Kubernetes, SQL, REST API..."
}

# CALCULAR MATCH INDIVIDUAL
resultado = matcher.calcular_match(usuario_id=1, oferta=oferta)
print(resultado['match_score'])  # 75.5
print(resultado['nivel_recomendacion'])  # "ALTA ⭐⭐⭐"
print(resultado['skills_coincidentes'])  # ['python', 'sql', 'rest api']
print(resultado['skills_faltantes'])  # ['docker', 'kubernetes']

# ANALIZAR MÚLTIPLES OFERTAS (RANKING)
ofertas = [oferta1, oferta2, oferta3, ...]
ranking = matcher.analizar_multiples_ofertas(usuario_id=1, ofertas=ofertas)

for resultado in ranking:
    print(f"#{resultado['ranking']} - {resultado['titulo']}")
    print(f"   Match: {resultado['porcentaje']}")

# REPORTE FORMATEADO
reporte = matcher.reporte_match(usuario_id=1, oferta=oferta)
print(reporte)
```

**Características:**
- Extrae automáticamente skills desde texto de ofertas
- Busca coincidencias exactas y parciales (difuso)
- Calcula score de compatibilidad 0-100%
- Genera niveles de recomendación: ALTA ⭐⭐⭐ / MEDIA ⭐⭐ / BAJA ⭐
- Crea reportes formateados

**Skills Soportados (50+):**
- Lenguajes: Python, Java, JavaScript, TypeScript, C++, C#, PHP, Ruby, Go, Rust
- BD: SQL, PostgreSQL, MySQL, MongoDB, Redis, Firebase, Elasticsearch
- Frontend: React, Vue, Angular, HTML, CSS, Bootstrap, Tailwind
- Backend: Django, Flask, Express, FastAPI, Spring, Laravel, Rails
- DevOps: Docker, Kubernetes, Git, CI/CD, AWS, Azure, GCP, Linux
- Arquitectura: Microservicios, REST API, GraphQL, Clean Code, Patrones
- Datos: Data Analysis, Dashboards, Power BI, Tableau, Excel
- Soft Skills: Comunicación, Inglés, Liderazgo, Teamwork, Problem Solving

---

## 📂 Scripts de Inicialización

### init_database.py - Crear Base de Datos

```bash
python init_database.py
```

**Crea:**
- Base de datos vacía con esquema
- Usuario: **Sebastian Barros** (Informática)
  - 5 certificados: Arquitectura, Programación, Inglés, BI, Modelos de Datos
  - 20+ skills técnicas
- Usuario: **Maria González** (Pedagogía)
  - 4 certificados: Licenciatura, Tecnología Educativa, Evaluación, Oratoria
  - 15+ skills educativas

**Salida:**
```
[INFO] Conectado a BD: data\jobspeed.db
[INFO] ✓ Tabla USUARIOS creada
[INFO] ✓ Tabla SKILLS creada
[INFO] ✓ Tabla CERTIFICADOS creada
...
[INFO] ✓ Usuario INFORMÁTICA creado (ID: 1)
[INFO] ✓ Usuario PEDAGOGÍA creado (ID: 2)
[INFO] ✓ BASE DE DATOS INICIALIZADA CORRECTAMENTE
```

---

## 🧪 Testing

### test_sprint2.py - Demostración Completa

```bash
python test_sprint2.py
```

**Pruebas:**
1. Carga perfiles de Informática y Pedagogía
2. Define 5 ofertas de ejemplo (variadas)
3. Calcula matching para cada usuario
4. Genera ranking de mejores ofertas
5. Muestra reporte detallado de top oferta

**Resultados para Sebastian Barros (Informática):**
```
[#1] Data Analyst - Analytics Plus
    Match: 42.9% → BAJA ⭐
    Skills: 3/7 (python, SQL, data analysis)

[#2] Docente de Educación Digital - Instituto Educativo
    Match: 33.3% → BAJA ⭐
    
[#3] Senior Python Developer - Tech Corp
    Match: 30.0% → BAJA ⭐
```

**Resultados para Maria González (Pedagogía):**
```
[#1] Capacitador Corporativo - Training Solutions
    Match: 100.0% → ALTA ⭐⭐⭐
    Skills: 2/2 (liderazgo, comunicación)

[#2] Docente de Educación Digital - Instituto Educativo
    Match: 66.7% → MEDIA ⭐⭐
```

---

## 🚀 Cómo Usar

### 1. Inicializar Base de Datos (Primera Ejecución)

```bash
python init_database.py
```

### 2. Crear tu Propio Usuario

```python
from src.database import DatabaseManager

db = DatabaseManager()

# Agregar usuario
usuario_id = db.agregar_usuario("Tu Nombre", "Tu Carrera")

# Agregar skills directamente
python_id = db.agregar_skill("python", "Lenguajes")
db.agregar_skill_usuario(usuario_id, python_id, nivel='senior', 
                         años_experiencia=5, origen='experiencia')

# Agregar certificado
cert_id = db.agregar_certificado("Mi Certificado", "Mi Instituto")
db.agregar_certificado_usuario(usuario_id, cert_id)

db.cerrar()
```

### 3. Analizar Ofertas

```python
from src.database import DatabaseManager
from src.matcher import Matcher

db = DatabaseManager()
matcher = Matcher(db)

mis_ofertas = [
    {"titulo": "Python Dev", "empresa": "Google", "descripcion": "Python, Django, PostgreSQL..."},
    {"titulo": "Data Analyst", "empresa": "Facebook", "descripcion": "SQL, Excel, Power BI..."},
]

ranking = matcher.analizar_multiples_ofertas(usuario_id=1, ofertas=mis_ofertas)

for r in ranking:
    print(f"#{r['ranking']} - {r['titulo']} ({r['porcentaje']})")
    
db.cerrar()
```

---

## 📊 Datos de Ejemplo

### Perfil 1: Sebastian Barros (Informática)

#### Certificados
| Certificado | Instituto | Skills |
|-------------|-----------|--------|
| Arquitectura de Software | Universidad | arquitectura, diseño software, patrones, system design |
| Programación de Software | Universidad | python, java, programación, lógica |
| Inglés Intermedio | Instituto | english, inglés, communication |
| Inteligencia de Negocios | Institución | BI, data analysis, dashboards |
| Modelos de Datos | Universidad | SQL, bases de datos, data modeling |

#### Skills Totales
- **Lenguajes:** Python, Java, JavaScript, TypeScript, SQL, HTML, CSS
- **Arquitectura:** Arquitectura, Diseño Software, Patrones, System Design, Microservicios, Clean Code
- **BD:** SQL, PostgreSQL, MySQL, MongoDB, Redis
- **DevOps:** Git, Docker, Kubernetes, CI/CD, Linux, AWS, Azure
- **Otros:** Inglés, Comunicación, Problem Solving, Testing

---

### Perfil 2: Maria González (Pedagogía)

#### Certificados
| Certificado | Instituto | Skills |
|-------------|-----------|--------|
| Licenciatura en Educación | Universidad | enseñanza, educación, comunicación, liderazgo |
| Diplomado en Tecnología Educativa | Institución | e-learning, plataformas educativas, diseño instruccional |
| Certificado en Evaluación Educativa | Instituto | evaluación educativa, investigación, análisis |
| Curso de Oratoria | Academia | presentaciones, oratoria, comunicación |

#### Skills Totales
- **Educación:** Enseñanza, Educación, Didáctica, Capacitación, Tutorías, Evaluación
- **Comunicación:** Comunicación, Presentaciones, Escritura, Oratoria, Liderazgo
- **Tecnología:** E-learning, Plataformas Educativas, Diseño Instruccional, Multimedia
- **Gestión:** Gestión Educativa, Planificación, Organización, Coordinación

---

## 🔗 Integración con Sprint 1

El Sprint 2 amplia el Sprint 1:

```
Sprint 1 Pipeline (Collector → Parser → Storage):
  ofertas_raw → ofertas_procesadas → CSV

Sprint 2 Enhancement (+ Database & Matcher):
  ofertas_procesadas → Matcher → Usuario → Score + Recomendación
```

**Flujo Propuesto para Sprint 3:**
```
1. Collector extrae ofertas (de Indeed, LinkedIn, etc)
2. Parser procesa y normaliza
3. Storage guarda en CSV/BD
4. Matcher compara con perfiles de usuarios
5. Genera ranking de mejores ofertas por usuario
6. [Futuro] FastAPI expone API REST
7. [Futuro] React muestra dashboard
```

---

## ⚡ Próximos Pasos (Sprint 3+)

- [ ] **Integrar Matcher con Storage** - Guardar matching results
- [ ] **Soporte múltiples usuarios** - Búsqueda y gestión de perfiles
- [ ] **API REST (FastAPI)** - Endpoints para usuarios y análisis
- [ ] **Frontend React** - Dashboard de ofertas personalizadas
- [ ] **Notificaciones** - Alertar cuando hay match alto
- [ ] **Machine Learning** - Predicción de interés del usuario
- [ ] **Integración Gmail** - Envío automático de candidaturas

---

## 📚 Referencias de Uso

```python
# DATABASE
from src.database import DatabaseManager

db = DatabaseManager("data/jobspeed.db")
db.crear_tablas()
usuario_id = db.agregar_usuario("Nombre", "Carrera")
perfil = db.obtener_perfil_completo(usuario_id)
db.cerrar()

# MATCHER
from src.matcher import Matcher

matcher = Matcher(db)
match_data = matcher.calcular_match(usuario_id, oferta_dict)
ranking = matcher.analizar_multiples_ofertas(usuario_id, ofertas_lista)
reporte = matcher.reporte_match(usuario_id, oferta_dict)
```

---

**Versión:** 2.0 (Sprint 2)  
**Estado:** Completado  
**Fecha:** 7 Febrero 2026
