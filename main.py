"""
Main Runner - JobSpeed Sprint 2
Orquesta la ejecución de Collector, Parser, Matcher y Storage
Busca ofertas, calcula compatibilidad con perfil y guarda con match_score
"""
# -*- coding: utf-8 -*-
import sys
import logging
import os
from pathlib import Path
from datetime import datetime

# Solución para Windows: Configurar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar src al path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from collector import Collector
from parser import Parser
from database import DatabaseManager
from matcher import Matcher
from storage import Storage
from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL
from multi_source_selenium import MultiSourceSeleniumAggregator

# Configurar logging global con UTF-8
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def ejecutar_pipeline():
    """Ejecuta el pipeline completo: Collector -> Parser -> Matcher -> Storage"""
    
    logger.info("=" * 80)
    logger.info("INICIANDO JOBSPEED - SPRINT 2")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    db = None
    
    try:
        # STEP 0: Conectar a BD y obtener usuario
        logger.info("\n[0/4] Conectando a Base de Datos...")
        db = DatabaseManager()
        usuario_id = db.obtener_usuario_id("Sebastian Alejandro Alvarez Aravena")
        
        if not usuario_id:
            logger.error("[ERROR] No se encontró el usuario en la BD")
            logger.error("   Ejecuta primero: python init_database.py")
            return False
        
        usuario = db.obtener_usuario(usuario_id)
        logger.info(f"[OK] Usuario conectado: {usuario['nombre']}")
        logger.info(f"  Carrera: {usuario['carrera']}")
        logger.info(f"  Ubicación: {usuario['ciudad']}, {usuario['pais']}")
        
        # STEP 1: Recolectar de múltiples fuentes
        logger.info("\n[1/4] Iniciando Multi-Source Collector (LinkedIn + Chiletrabajos + Trabajando + Indeed)...")
        
        # 1a. Recolectar de LinkedIn
        logger.info("\n  [1a] Recolectando de LinkedIn con Selenium...")
        collector = Collector()
        ofertas_linkedin = collector.buscar_ofertas(query="python developer", ubicacion="Chile", cantidad=15)
        
        if ofertas_linkedin:
            collector.deduplicar()
            ofertas_linkedin = collector.obtener_ofertas()
            logger.info(f"  [OK] {len(ofertas_linkedin)} ofertas de LinkedIn extraídas")
        else:
            logger.warning("  [AVISO] No se encontraron ofertas en LinkedIn")
            ofertas_linkedin = []
        
        # STEP 1-B: Recolectar de otras fuentes (Chiletrabajos, Trabajando.cl, Indeed con SELENIUM)
        logger.info("\n  [1b] Recolectando de plataformas chilenas/latinas con Selenium (navegador real)...")
        agregador = MultiSourceSeleniumAggregator()
        
        # Scrape las otras fuentes con navegador real (evita bloqueos WAF)
        ofertas_otras_fuentes = agregador.scrape_multiples_fuentes(
            keywords=['python developer', 'python'],
            locations=['santiago', 'chile']
        )
        
        if ofertas_otras_fuentes:
            logger.info(f"  [OK] {len(ofertas_otras_fuentes)} ofertas de otras fuentes extraídas")
            ofertas_linkedin.extend(ofertas_otras_fuentes)
        else:
            logger.warning("  [AVISO] No se encontraron ofertas en otras fuentes")
        
        # Consolidar todas las ofertas
        ofertas_raw = ofertas_linkedin
        
        # Validar que tenemos ofertas
        if not ofertas_raw:
            logger.error("")
            logger.error("=" * 80)
            logger.error("PROBLEMA: No se encontraron ofertas en ninguna fuente")
            logger.error("")
            logger.error("Posibles causas:")
            logger.error("1. LinkedIn pidió validación CAPTCHA")
            logger.error("2. Otros sitios están bloqueando los requests")
            logger.error("3. Necesitas acceso a internet")
            logger.error("")
            logger.error("Solución:")
            logger.error("- El sistema ahora usa Selenium (navegador real) para todas las fuentes")
            logger.error("- Esto debería evitar bloqueos de WAF y bot detection")
            logger.error("- Intenta ejecutar de nuevo: python main.py")
            logger.error("=" * 80)
            logger.error("")
            return False
        
        # Deduplicar ofertas por URL
        urls_vistas = set()
        ofertas_unicas = []
        for oferta in ofertas_raw:
            url = oferta.get('url', '').lower().strip()
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                ofertas_unicas.append(oferta)
        
        logger.info(f"[OK] Deduplicadas ofertas: {len(ofertas_raw)} → {len(ofertas_unicas)}")
        ofertas_raw = ofertas_unicas
        
        # STEP 2: Parsear
        logger.info("\n[2/4] Iniciando Parser...")
        parser = Parser()
        ofertas_procesadas = parser.procesar_ofertas(ofertas_raw)
        
        if not ofertas_procesadas:
            logger.error("No se procesaron ofertas. Abortando.")
            return False
        
        logger.info(f"[OK] Ofertas procesadas: {len(ofertas_procesadas)}")
        
        # STEP 3: Calcular Matching
        logger.info("\n[3/4] Calculando Compatibilidad (Match Score + Proximidad)...")
        matcher = Matcher(db)
        
        # Agregar score_final a cada oferta
        ofertas_con_match = []
        for oferta in ofertas_procesadas:
            score_data = matcher.calcular_score_final(usuario_id, oferta)
            oferta['match_score'] = score_data['match_score']
            oferta['proximidad_score'] = score_data['proximidad_score']
            oferta['score_final'] = score_data['score_final']
            oferta['categoria_recomendacion'] = score_data['categoria_recomendacion']
            ofertas_con_match.append(oferta)
        
        # Agrupar por categoría y ordenar
        categorias = {}
        for oferta in ofertas_con_match:
            cat = oferta.get('categoria_recomendacion', 'Otros')
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(oferta)
        
        # Ordenar dentro de cada categoría por score_final descendente
        for cat in categorias:
            categorias[cat].sort(key=lambda x: x['score_final'], reverse=True)
        
        logger.info(f"[OK] Compatibilidad calculada para {len(ofertas_con_match)} ofertas")
        
        # Mostrar ranking por categorías
        logger.info("\n" + "=" * 90)
        logger.info("RESULTADOS JOBSPEED - RANKING INTELIGENTE")
        logger.info("=" * 90)
        
        posicion_global = 1
        
        # Mostrar "Recomendados para ti" primero
        if "Recomendados" in categorias:
            logger.info("\n[RECOMENDADOS] - Mayor Compatibilidad Técnica")
            logger.info("-" * 90)
            for oferta in categorias["Recomendados"][:5]:  # Top 5
                titulo = oferta.get('titulo', 'Sin título')
                empresa = oferta.get('empresa', 'N/A')
                ciudad = oferta.get('ciudad', 'N/A')
                pais = oferta.get('pais', 'N/A')
                score = oferta.get('score_final', 0)
                
                logger.info(f"\n#{posicion_global}. {titulo} - {empresa}")
                logger.info(f"    Ubicación: {ciudad}, {pais}")
                logger.info(f"    Score: {score:.1f}% (Match: {oferta.get('match_score', 0):.1f}%)")
                posicion_global += 1
        
        # Mostrar "Mejor Match Técnico"
        if "Mejor Match" in categorias:
            logger.info("\n[MEJOR MATCH] - Buena Compatibilidad con Skills")
            logger.info("-" * 90)
            for oferta in categorias["Mejor Match"][:5]:
                titulo = oferta.get('titulo', 'Sin título')
                empresa = oferta.get('empresa', 'N/A')
                ciudad = oferta.get('ciudad', 'N/A')
                pais = oferta.get('pais', 'N/A')
                score = oferta.get('score_final', 0)
                
                logger.info(f"\n#{posicion_global}. {titulo} - {empresa}")
                logger.info(f"    Ubicación: {ciudad}, {pais}")
                logger.info(f"    Score: {score:.1f}% (Match: {oferta.get('match_score', 0):.1f}%)")
                posicion_global += 1
        
        # Mostrar "Cerca de ti"
        if "Cerca de ti" in categorias:
            logger.info("\n[CERCA DE TI] - Ubicación Cercana con Match Aceptable")
            logger.info("-" * 90)
            for oferta in categorias["Cerca de ti"][:5]:
                titulo = oferta.get('titulo', 'Sin título')
                empresa = oferta.get('empresa', 'N/A')
                ciudad = oferta.get('ciudad', 'N/A')
                pais = oferta.get('pais', 'N/A')
                score = oferta.get('score_final', 0)
                
                logger.info(f"\n#{posicion_global}. {titulo} - {empresa}")
                logger.info(f"    Ubicación: {ciudad}, {pais}")
                logger.info(f"    Score: {score:.1f}% (Match: {oferta.get('match_score', 0):.1f}%)")
                posicion_global += 1
        
        logger.info("\n" + "=" * 90)
        
        # STEP 4: Almacenar
        logger.info("\n[4/4] Iniciando Storage...")
        
        # VERIFICACION CRITICA: Asegurar que TODAS las ofertas tengan TODAS las columnas
        logger.info("  Completando datos de ofertas...")
        from config import CSV_COLUMNS
        
        for oferta in ofertas_con_match:
            # Asegurar que todas las columnas obligatorias existan
            for col in CSV_COLUMNS:
                if col not in oferta:
                    # Asignar valores por defecto
                    if col in ['match_score', 'proximidad_score', 'score_final']:
                        oferta[col] = 0.0
                    else:
                        oferta[col] = 'N/A'
            
            # IMPORTANTE: Si 'source' es vacío, marcar como 'LinkedIn'
            if not oferta.get('source') or oferta.get('source') == 'N/A':
                oferta['source'] = 'LinkedIn'
            
            logger.debug(f"  Oferta completada: {oferta.get('titulo', 'N/A')} (Source: {oferta.get('source')})")
        
        # Log de ofertas por source
        sources_count = {}
        for oferta in ofertas_con_match:
            src = oferta.get('source', 'N/A')
            sources_count[src] = sources_count.get(src, 0) + 1
        
        logger.info(f"  Ofertas por fuente:")
        for source, count in sources_count.items():
            logger.info(f"    - {source}: {count} ofertas")
        
        storage = Storage()
        exito = storage.guardar_ofertas(ofertas_con_match)
        
        if not exito:
            logger.error("Error guardando ofertas. Abortando.")
            return False
        
        # Estadísticas
        stats = storage.obtener_estadisticas()
        logger.info(f"[OK] CSV Actualizado. Estadísticas: {stats}")
        
        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE EJECUTADO EXITOSAMENTE")
        logger.info(f"Total de ofertas procesadas: {len(ofertas_con_match)}")
        logger.info(f"Empresas únicas: {stats.get('empresas_unicas', 0)}")
        logger.info(f"Ciudades: {stats.get('ciudades_unicas', 0)}")
        logger.info(f"Países: {stats.get('paises_unicos', 0)}")
        
        # Top 3 ofertas
        if ofertas_con_match:
            todas_ordenadas = sorted(ofertas_con_match, key=lambda x: x.get('score_final', 0), reverse=True)
            logger.info(f"\n[TOP 3] MEJORES OFERTAS PARA TI:")
            for idx, oferta in enumerate(todas_ordenadas[:3], 1):
                titulo = oferta.get('titulo', 'Sin título')
                score = oferta.get('score_final', 0)
                logger.info(f"  {idx}. {titulo} - Score: {score:.1f}%")
        
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}", exc_info=True)
        return False
    
    finally:
        if db:
            db.cerrar()


if __name__ == "__main__":
    exito = ejecutar_pipeline()
    sys.exit(0 if exito else 1)
