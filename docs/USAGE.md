# 📖 Guía de Uso - JobSpeed Sprint 1

## Instalación

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes Python)

### Pasos de Instalación

1. **Navegar a la carpeta del proyecto:**
```bash
cd c:\Users\sebar\Desktop\Programacion\JobSpeed
```

2. **Crear entorno virtual (opcional pero recomendado):**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

---

## Ejecución

### Ejecución Principal

Para ejecutar el pipeline completo (Collector -> Parser -> Storage):

```bash
python main.py
```

**Salida esperada:**
```
======================================================================
INICIANDO JOBSPEED - SPRINT 1
Timestamp: 2026-02-06 XX:XX:XX
======================================================================
[1/3] Iniciando Collector...
✓ Ofertas extraídas y deduplicadas: 50
[2/3] Iniciando Parser...
✓ Ofertas procesadas: 50
[3/3] Iniciando Storage...
✓ CSV Actualizado. Estadísticas: {...}
======================================================================
PIPELINE EJECUTADO EXITOSAMENTE
Total de ofertas en BD: 50
Empresas únicas: 30
Ubicaciones únicas: 15
======================================================================
```

---

## Verificación de Resultados

### 1️⃣ Verificar CSV Generado

Abrir `data/ofertas.csv` o ejecutar:

```bash
python -c "import pandas as pd; df = pd.read_csv('data/ofertas.csv'); print(f'Registros: {len(df)}'); print(df.head())"
```

### 2️⃣ Revisar Logs

Los logs se guardan en `logs/execution.log`:

```bash
# Windows
type logs\execution.log

# Linux/Mac
cat logs/execution.log
```

### 3️⃣ Ver Estructura del CSV

```bash
python -c "import pandas as pd; df = pd.read_csv('data/ofertas.csv'); print(df.columns.tolist())"
```

---

## Uso de Módulos Individuales

### Collector (Extracción)

```python
from src.collector import Collector

collector = Collector()
ofertas = collector.buscar_ofertas(query="python", cantidad=30)
collector.deduplicar()
print(f"Total: {len(collector.obtener_ofertas())}")
```

### Parser (Procesamiento)

```python
from src.parser import Parser
from src.collector import Collector

collector = Collector()
ofertas_raw = collector.buscar_ofertas("python", 10)

parser = Parser()
ofertas_procesadas = parser.procesar_ofertas(ofertas_raw)
print(f"Procesadas: {len(ofertas_procesadas)}")
```

### Storage (Almacenamiento)

```python
from src.storage import Storage
import pandas as pd

storage = Storage()

# Leer datos
df = storage.leer_ofertas(limite=10)

# Obtener estadísticas
stats = storage.obtener_estadisticas()
print(stats)
```

---

## Estructura del CSV

| Campo | Ejemplo | Descripción |
|-------|---------|-------------|
| id | 1 | Identificador único |
| titulo | Senior Python Developer | Puesto de trabajo |
| empresa | Tech Company Inc | Nombre de la empresa |
| ubicacion | Remote / New York | Ubicación del trabajo |
| salario | $100k - $150k | Rango salarial |
| descripcion | Looking for experienced Python... | Descripción de 500 caracteres |
| url | https://indeed.com/viewjob?jk=... | Enlace a la oferta |
| fecha_extraccion | 2026-02-06 14:30:00 | Fecha de extracción |

---

## Solución de Problemas

### ❌ Error: "ModuleNotFoundError"
**Solución:** Asegúrese de instalar las dependencias:
```bash
pip install -r requirements.txt
```

### ❌ Error: "No se encontraron ofertas"
**Solución:** 
- Verificar conexión a Internet
- Aumentar timeout en `config.py`
- Cambiar query de búsqueda

### ❌ CSV vacío
**Solución:**
- Revisar `logs/execution.log` para errores
- Verificar selectores HTML de Indeed

---

## Próximos Pasos (Sprint 2+)

- [ ] Agregar módulo **Matcher** para compatibilidad
- [ ] Soporte para múltiples plataformas
- [ ] Mejoras en extracción de salario
- [ ] Filtrado avanzado de ofertas

---

## Contacto & Soporte

Para reportar problemas, revisar:
- `logs/execution.log` - Registro de ejecución
- `SPRINT_1.md` - Especificaciones del sprint
