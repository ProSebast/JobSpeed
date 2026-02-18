#!/usr/bin/env python3
# Diagnóstico de Scraping
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
#!/usr/bin/env python3
"""
Diagnóstico - Por qué solo funciona LinkedIn
Prueba cada fuente para identificar bloqueos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from multi_source_scraper import (
    ChileTrabajosScraperV2,
    TrabajandoClScraperV2, 
    IndeedPublicScraper
)
import requests

print("\n" + "="*80)
print("DIAGNÓSTICO - TESTEO DE FUENTES")
print("="*80)

# Test 1: Conexión básica
print("\n[TEST 1] CONEXIÓN BÁSICA (HEAD Request)")
print("-"*80)

fuentes = {
    "Chiletrabajos": "https://www.chiletrabajos.cl",
    "Trabajando.cl": "https://www.trabajando.cl",
    "Indeed": "https://indeed.com",
}

for nombre, url in fuentes.items():
    try:
        print(f"\n{nombre} ({url})")
        response = requests.head(url, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Headers CloudFlare: {'cf-ray' in response.headers}")
        print(f"  Headers Block: {'Server' in response.headers}")
        if 'Server' in response.headers:
            print(f"    Server: {response.headers['Server']}")
    except Exception as e:
        print(f"  Error: {str(e)}")

# Test 2: GET Request con User-Agent
print("\n\n[TEST 2] GET REQUEST CON USER-AGENT")
print("-"*80)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for nombre, url in fuentes.items():
    try:
        print(f"\n{nombre}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Content Length: {len(response.content)} bytes")
        
        if response.status_code == 403:
            print(f"  ⚠️  BLOQUEADO (403 Forbidden)")
        elif response.status_code == 200:
            print(f"  ✅ OK (200)")
        else:
            print(f"  ⚠️  Status: {response.status_code}")
            
    except Exception as e:
        print(f"  Error: {str(e)}")

# Test 3: Scraping real
print("\n\n[TEST 3] SCRAPING REAL (BeautifulSoup)")
print("-"*80)

print("\n[Chiletrabajos]")
scraper = ChileTrabajosScraperV2()
ofertas, exito, msg = scraper.scrape(keyword='python', location='santiago')
print(f"  Resultado: {exito}")
print(f"  Mensaje: {msg}")
print(f"  Ofertas: {len(ofertas)}")
if ofertas:
    print(f"  Primera: {ofertas[0].get('titulo', 'N/A')}")

print("\n[Trabajando.cl]")
scraper = TrabajandoClScraperV2()
ofertas, exito, msg = scraper.scrape(keyword='python', location='santiago')
print(f"  Resultado: {exito}")
print(f"  Mensaje: {msg}")
print(f"  Ofertas: {len(ofertas)}")
if ofertas:
    print(f"  Primera: {ofertas[0].get('titulo', 'N/A')}")

print("\n[Indeed]")
scraper = IndeedPublicScraper()
ofertas, exito, msg = scraper.scrape(keyword='python', location='chile')
print(f"  Resultado: {exito}")
print(f"  Mensaje: {msg}")
print(f"  Ofertas: {len(ofertas)}")
if ofertas:
    print(f"  Primera: {ofertas[0].get('titulo', 'N/A')}")

print("\n" + "="*80)
print("CONCLUSIÓN")
print("="*80)
print("\nSi las fuentes retornan 0 ofertas → Necesitamos Selenium Browser")
print("Si hay status 403 → Bloqueado por WAF Cloudflare")
print("Si hay error → Problema de conexión")
print("\n" + "="*80)
