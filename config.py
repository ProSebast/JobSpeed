"""
Configuración global de JobSpeed
"""
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SRC_DIR = BASE_DIR / "src"

# Asegurar que existen las carpetas
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# CSV de almacenamiento
CSV_PATH = DATA_DIR / "ofertas.csv"

# Log de ejecución
LOG_FILE = LOGS_DIR / "execution.log"

# Configuración de scraping
SCRAPE_CONFIG = {
    "timeout": 10,
    "retries": 3,
    "delay": 1,  # segundos entre requests
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}

# Plataforma inicial (LinkedIn)
TARGET_PLATFORMS = {
    "linkedin": "https://linkedin.com",
    # Agregar mas plataformas en futuro sprints
}

# Campos esperados en CSV
CSV_COLUMNS = [
    "id",
    "titulo",
    "empresa",
    "ubicacion",
    "salario",
    "descripcion",
    "url",
    "fecha_extraccion"
]

# Configuración de logging
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
LOG_LEVEL = "INFO"
