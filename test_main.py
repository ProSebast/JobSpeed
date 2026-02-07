"""
Test Runner - JobSpeed Sprint 1
Versión de prueba con datos simulados para validar el pipeline
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from parser import Parser
from storage import Storage
from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def generar_datos_test() -> list:
    """Genera datos de prueba para simular ofertas extraídas"""
    
    ofertas_test = [
        {
            "id": 1,
            "titulo": "Senior Python Developer",
            "url": "https://example.com/job/1",
            "fuente": "test"
        },
        {
            "id": 2,
            "titulo": "Python Data Scientist",
            "url": "https://example.com/job/2",
            "fuente": "test"
        },
        {
            "id": 3,
            "titulo": "Backend Python Engineer",
            "url": "https://example.com/job/3",
            "fuente": "test"
        },
        {
            "id": 4,
            "titulo": "Full Stack Python Developer",
            "url": "https://example.com/job/4",
            "fuente": "test"
        },
        {
            "id": 5,
            "titulo": "Python Developer - Remote",
            "url": "https://example.com/job/5",
            "fuente": "test"
        },
    ]
    
    return ofertas_test


def generar_ofertas_procesadas_test() -> list:
    """Genera ofertas ya procesadas para simular salida del Parser"""
    
    return [
        {
            "id": 1,
            "titulo": "Senior Python Developer",
            "empresa": "Tech Corp Inc",
            "ubicacion": "New York, NY",
            "salario": "$120k - $150k",
            "descripcion": "We are looking for an experienced Senior Python Developer to join our growing team. Requirements: 5+ years Python, Django, REST APIs, PostgreSQL.",
            "url": "https://example.com/job/1",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 2,
            "titulo": "Python Data Scientist",
            "empresa": "DataMind Solutions",
            "ubicacion": "Remote",
            "salario": "$100k - $130k",
            "descripcion": "Join our Data Science team. Experience with: Python, pandas, scikit-learn, TensorFlow. Machine learning and statistical analysis.",
            "url": "https://example.com/job/2",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 3,
            "titulo": "Backend Python Engineer",
            "empresa": "CloudServices Ltd",
            "ubicacion": "San Francisco, CA",
            "salario": "$110k - $140k",
            "descripcion": "Build scalable backend systems with Python. FastAPI, microservices, cloud deployment (AWS). 3+ years experience required.",
            "url": "https://example.com/job/3",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 4,
            "titulo": "Full Stack Python Developer",
            "empresa": "WebDev Innovations",
            "ubicacion": "Toronto, Canada",
            "salario": "$95k - $120k",
            "descripcion": "Full stack development with Python backend (Flask/Django) and modern frontend. DevOps knowledge a plus.",
            "url": "https://example.com/job/4",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 5,
            "titulo": "Python Developer - Remote",
            "empresa": "StartupXYZ",
            "ubicacion": "Remote",
            "salario": "$80k - $110k",
            "descripcion": "Exciting opportunity to work with a growing startup. Python development, startups experience preferred. Flexible hours.",
            "url": "https://example.com/job/5",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
    ]


def ejecutar_pipeline_test():
    """Ejecuta el pipeline con datos de prueba"""
    
    logger.info("=" * 70)
    logger.info("JOBSPEED SPRINT 1 - TEST EXECUTION")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    try:
        # STEP 1: Simular Collector
        logger.info("\n[1/3] Collector (SIMULADO)...")
        ofertas_raw = generar_datos_test()
        logger.info(f"[OK] Ofertas extraídas (test): {len(ofertas_raw)}")
        
        # STEP 2: Parsear (creamos datos ya parseados para acelerar)
        logger.info("\n[2/3] Parser (SIMULADO)...")
        ofertas_procesadas = generar_ofertas_procesadas_test()
        logger.info(f"[OK] Ofertas procesadas: {len(ofertas_procesadas)}")
        
        # STEP 3: Almacenar
        logger.info("\n[3/3] Almacenando en CSV...")
        storage = Storage()
        exito = storage.guardar_ofertas(ofertas_procesadas)
        
        if not exito:
            logger.error("Error guardando ofertas.")
            return False
        
        # Estadísticas
        stats = storage.obtener_estadisticas()
        logger.info(f"[OK] CSV Actualizado. Estadísticas: {stats}")
        
        # Verificación
        logger.info("\n[VERIFICACION] Leyendo CSV...")
        df = storage.leer_ofertas()
        logger.info(f"[OK] Total en CSV: {len(df)} ofertas")
        logger.info(f"[OK] Columnas: {df.columns.tolist()}")
        
        # Resumen
        logger.info("\n" + "=" * 70)
        logger.info("[SUCCESS] PIPELINE TEST EJECUTADO EXITOSAMENTE")
        logger.info(f"Total de ofertas: {stats.get('total_ofertas', 0)}")
        logger.info(f"Empresas unicas: {stats.get('empresas_unicas', 0)}")
        logger.info(f"Ubicaciones unicas: {stats.get('ubicaciones_unicas', 0)}")
        logger.info(f"CSV guardado en: data/ofertas.csv")
        logger.info("=" * 70)
        logger.info("\n[NOTE] Esta es una prueba con datos simulados.")
        logger.info("Para usar datos reales, se necesita resolver el acceso a Indeed o usar otra fuente.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    exito = ejecutar_pipeline_test()
    sys.exit(0 if exito else 1)
