"""
Main Runner - JobSpeed Sprint 1
Orquesta la ejecución de Collector, Parser y Storage
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from collector import Collector
from parser import Parser
from storage import Storage
from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Configurar logging global
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ejecutar_pipeline():
    """Ejecuta el pipeline completo: Collector -> Parser -> Storage"""
    
    logger.info("=" * 70)
    logger.info("INICIANDO JOBSPEED - SPRINT 1")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    try:
        # STEP 1: Recolectar
        logger.info("\n[1/3] Iniciando Collector (LinkedIn con Selenium)...")
        collector = Collector()
        ofertas_raw = collector.buscar_ofertas(query="python developer", ubicacion="Chile", cantidad=15)
        
        if not ofertas_raw:
            logger.error("")
            logger.error("=" * 70)
            logger.error("PROBLEMA: No se encontraron ofertas en LinkedIn")
            logger.error("")
            logger.error("Posibles causas:")
            logger.error("1. Linkedin pidio validacion CAPTCHA")
            logger.error("2. Necesitas acceso a internet")
            logger.error("3. Chrome/Selenium no se instalo correctamente")
            logger.error("")
            logger.error("Intenta:")
            logger.error("- Visita linkedin.com manualmente para validarte")
            logger.error("- Verifica tu conexion a internet")
            logger.error("- Reinicia el programa")
            logger.error("=" * 70)
            logger.error("")
            return False
        
        # Deduplicar
        collector.deduplicar()
        ofertas_raw = collector.obtener_ofertas()
        logger.info(f"[OK] Ofertas extraídas y deduplicadas: {len(ofertas_raw)}")
        
        # STEP 2: Parsear
        logger.info("\n[2/3] Iniciando Parser...")
        parser = Parser()
        ofertas_procesadas = parser.procesar_ofertas(ofertas_raw)
        
        if not ofertas_procesadas:
            logger.error("No se procesaron ofertas. Abortando.")
            return False
        
        logger.info(f"[OK] Ofertas procesadas: {len(ofertas_procesadas)}")
        
        # Mostrar links de ofertas en terminal
        logger.info("\n" + "=" * 70)
        logger.info("LINKS DE OFERTAS EXTRAÍDAS:")
        logger.info("=" * 70)
        for idx, oferta in enumerate(ofertas_procesadas, 1):
            url = oferta.get("url", "N/A")
            titulo = oferta.get("titulo", "Sin título")
            empresa = oferta.get("empresa", "N/A")
            logger.info(f"{idx}. {titulo} - {empresa}")
            logger.info(f"   [LINK] {url}")
        logger.info("=" * 70)
        
        # STEP 3: Almacenar
        logger.info("\n[3/3] Iniciando Storage...")
        storage = Storage()
        exito = storage.guardar_ofertas(ofertas_procesadas)
        
        if not exito:
            logger.error("Error guardando ofertas. Abortando.")
            return False
        
        # Estadísticas
        stats = storage.obtener_estadisticas()
        logger.info(f"[OK] CSV Actualizado. Estadisticas: {stats}")
        
        # Resumen final
        logger.info("\n" + "=" * 70)
        logger.info("PIPELINE EJECUTADO EXITOSAMENTE")
        logger.info(f"Total de ofertas de LinkedIn: {stats.get('total_ofertas', 0)}")
        logger.info(f"Empresas unicas: {stats.get('empresas_unicas', 0)}")
        logger.info(f"Ubicaciones diversas encontradas: {stats.get('ubicaciones_unicas', 0)}")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    exito = ejecutar_pipeline()
    sys.exit(0 if exito else 1)
