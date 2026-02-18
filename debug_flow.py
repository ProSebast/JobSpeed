#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Debugging - Verifica el flujo de datos completo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("DEBUGGING - FLUJO DE DATOS")
print("="*80 + "\n")

try:
    # Test 1: Importar y probar Collector (LinkedIn)
    logger.info("[1/3] Probando Collector (LinkedIn)...")
    from collector import Collector
    collector = Collector()
    ofertas_linkedin = collector.buscar_ofertas(query="python", ubicacion="Chile", cantidad=5)
    
    logger.info(f"  Ofertas LinkedIn extraídas: {len(ofertas_linkedin)}")
    if ofertas_linkedin:
        oferta_sample = ofertas_linkedin[0]
        logger.info(f"  Ejemplo: {oferta_sample.get('titulo', 'N/A')}")
        logger.info(f"  Keys en oferta: {list(oferta_sample.keys())}")
        logger.info(f"  Tiene 'source'?: {'source' in oferta_sample}")
    
    # Test 2: Probar MultiSourceSeleniumAggregator
    logger.info("\n[2/3] Probando MultiSourceSeleniumAggregator (Chiletrabajos)...")
    from multi_source_selenium import MultiSourceSeleniumAggregator
    agregador = MultiSourceSeleniumAggregator()
    
    # Solo test
    scraper_ct = agregador.scrapers['chiletrabajos']
    ofertas_ct, exito, msg = scraper_ct.scrape(keyword='python', location='santiago')
    
    logger.info(f"  Ofertas Chiletrabajos: {len(ofertas_ct)}")
    if ofertas_ct:
        oferta_sample = ofertas_ct[0]
        logger.info(f"  Ejemplo: {oferta_sample.get('titulo', 'N/A')}")
        logger.info(f"  Keys en oferta: {list(oferta_sample.keys())}")
        logger.info(f"  Source: {oferta_sample.get('source', 'NO TIENE')}")
    
    # Test 3: Verificar que las ofertas tienen estructura correcta
    logger.info("\n[3/3] Verificando estructura de CSV...")
    from config import CSV_COLUMNS
    logger.info(f"  Columnas esperadas: {CSV_COLUMNS}")
    
    # Verificar que LinkedIn tenga 'source'
    if ofertas_linkedin and 'source' not in ofertas_linkedin[0]:
        logger.warning("  [PROBLEMA] Ofertas de LinkedIn NO tienen columna 'source'")
        logger.info("  [SOLUCION] Agregando 'source'='LinkedIn' a todas las ofertas de LinkedIn")
        for oferta in ofertas_linkedin:
            oferta['source'] = 'LinkedIn'
    
    # Combinar
    todas_ofertas = ofertas_linkedin + ofertas_ct
    logger.info(f"\n  Total ofertas combinadas: {len(todas_ofertas)}")
    
    # Verificar sources
    sources = set([o.get('source', 'N/A') for o in todas_ofertas])
    logger.info(f"  Sources encontrados: {sources}")
    
    logger.info("\n[SUCCESS] Debugging completado!")
    
except Exception as e:
    logger.error(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
