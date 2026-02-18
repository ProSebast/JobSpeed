#!/usr/bin/env python3
# Demo Multi-Source
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
#!/usr/bin/env python3
"""
Demo - Multi-Source Job Aggregator
Ejecuta el agregador y muestra ofertas consolidadas de múltiples fuentes
"""

import sys
from pathlib import Path
import json
import logging

# Agregar src al path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from multi_source_scraper import MultiSourceAggregator, ChileTrabajosScraperV2
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Demo del agregador"""
    
    logger.info("\n" + "="*80)
    logger.info("JOBSPEED - AGREGADOR MULTI-FUENTE")
    logger.info("="*80)
    logger.info(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # Crear agregador
    agregador = MultiSourceAggregator()
    
    # Ejemplo: Agregar ofertas simuladas de LinkedIn
    logger.info("\n[PASO 1] Simulando ofertas de LinkedIn...")
    ofertas_linkedin_demo = [
        {
            'titulo': 'Senior Python Developer',
            'empresa': 'Tech Corp Chile',
            'ciudad': 'Santiago',
            'pais': 'Chile',
            'salario': '$3000-5000 USD',
            'descripcion': 'Buscamos desarrollador senior en Python con experiencia en Django y REST APIs',
            'url': 'https://linkedin.com/jobs/python-developer-1',
            'source': 'LinkedIn',
            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'titulo': 'Backend Python Developer',
            'empresa': 'StartUp Latam',
            'ciudad': 'Santiago',
            'pais': 'Chile',
            'salario': '$2500-3500 USD',
            'descripcion': 'Necesitamos backend developer en Python para microservicios',
            'url': 'https://linkedin.com/jobs/backend-python-2',
            'source': 'LinkedIn',
            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'titulo': 'Python Full Stack Developer',
            'empresa': 'Digital Agency',
            'ciudad': 'Valparaiso',
            'pais': 'Chile',
            'salario': '$2000-3000 USD',
            'descripcion': 'Buscamos Full Stack Python developer con React',
            'url': 'https://linkedin.com/jobs/fullstack-3',
            'source': 'LinkedIn',
            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    agregador.agregar_scraper_linkedin(ofertas_linkedin_demo)
    logger.info(f"✓ {len(ofertas_linkedin_demo)} ofertas de LinkedIn agregadas")
    
    # Scrape las otras fuentes
    logger.info("\n[PASO 2] Scrapeando fuentes adicionales...")
    logger.info("Nota: Este proceso puede tomar 1-2 minutos por fuente\n")
    
    reporte = agregador.scrape_todas_las_fuentes(
        keywords=['python', 'developer'],
        locations=['santiago', 'chile']
    )
    
    # Obtener todas las ofertas consolidadas
    todas_ofertas = agregador.obtener_todas_ofertas()
    
    # Deduplicar
    ofertas_finales = agregador.deduplicar_ofertas()
    
    # Mostrar reporte detallado
    logger.info("\n" + "="*80)
    logger.info("REPORTE DE SCRAPING")
    logger.info("="*80)
    
    logger.info(f"\nTotal de ofertas extraídas: {len(ofertas_finales)}")
    logger.info("\nOfertas por fuente:")
    logger.info("-"*80)
    
    # Agrupar por fuente
    por_fuente = {}
    for oferta in ofertas_finales:
        source = oferta.get('source', 'Desconocida')
        if source not in por_fuente:
            por_fuente[source] = []
        por_fuente[source].append(oferta)
    
    for source in sorted(por_fuente.keys()):
        cantidad = len(por_fuente[source])
        porcentaje = (cantidad / len(ofertas_finales) * 100) if ofertas_finales else 0
        logger.info(f"  • {source:20s}: {cantidad:3d} ofertas ({porcentaje:5.1f}%)")
    
    # Mostrar primeras 5 ofertas
    logger.info("\n" + "="*80)
    logger.info("PRIMERAS 5 OFERTAS CONSOLIDADAS")
    logger.info("="*80)
    
    for i, oferta in enumerate(ofertas_finales[:5], 1):
        logger.info(f"\n#{i}. {oferta.get('titulo', 'Sin título')}")
        logger.info(f"   Empresa: {oferta.get('empresa', 'N/A')}")
        logger.info(f"   Ubicación: {oferta.get('ciudad', 'N/A')}, {oferta.get('pais', 'N/A')}")
        logger.info(f"   Salario: {oferta.get('salario', 'No especificado')}")
        logger.info(f"   Fuente: {oferta.get('source', 'Desconocida')}")
        logger.info(f"   URL: {oferta.get('url', 'N/A')[:60]}...")
    
    # Mostrar estadísticas JSON
    logger.info("\n" + "="*80)
    logger.info("TABLA RESUMEN")
    logger.info("="*80)
    
    resumen = {
        'timestamp': datetime.now().isoformat(),
        'total_ofertas': len(ofertas_finales),
        'fuentes': {}
    }
    
    for source, ofertas in por_fuente.items():
        resumen['fuentes'][source] = {
            'cantidad': len(ofertas),
            'ciudades': len(set(o.get('ciudad', 'N/A') for o in ofertas)),
            'empresas': len(set(o.get('empresa', 'N/A') for o in ofertas))
        }
    
    logger.info(json.dumps(resumen, indent=2, default=str))
    
    logger.info("\n" + "="*80)
    logger.info("PRÓXIMOS PASOS:")
    logger.info("="*80)
    logger.info("1. Ejecuta 'python main.py' para procesar ofertas con tu perfil")
    logger.info("2. Las ofertas se analizarán con tu CV y se calcularán scores")
    logger.info("3. Verás recomendaciones basadas en match + proximidad geográfica")
    logger.info("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)
