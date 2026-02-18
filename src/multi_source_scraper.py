#!/usr/bin/env python3
"""
Multi-Source Job Scraper – Implementación Real
Integra múltiples fuentes de ofertas laborales con scrapers y APIs públicas
"""

import logging
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperBase(ABC):
    """Clase base para scrapers de ofertas"""
    
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    @abstractmethod
    def scrape(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """Scrape ofertas - retorna (ofertas, éxito, mensaje)"""
        pass
    
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba conexión a la fuente"""
        try:
            response = self.session.head(self.base_url, timeout=5)
            return response.status_code in [200, 301, 302], f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)


class ChileTrabajosScraperV2(ScraperBase):
    """Scraper para Chiletrabajos.cl - Sitio chileno de empleo"""
    
    def __init__(self):
        super().__init__(
            "Chiletrabajos",
            "https://www.chiletrabajos.cl"
        )
        self.search_url = "https://www.chiletrabajos.cl/?s={keyword}&l={location}&r=50"
        
    def scrape(self, keyword: str = "python", location: str = "santiago", **kwargs) -> Tuple[List[Dict], bool, str]:
        """
        Scrape ofertas de Chiletrabajos
        
        Args:
            keyword: Búsqueda (ej: python, developer)
            location: Ubicación (ej: santiago, chile)
        """
        ofertas = []
        
        try:
            # Preparar búsqueda
            url = self.search_url.format(keyword=keyword, location=location)
            logger.info(f"[{self.source_name}] Scrapeando: {url}")
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return [], False, f"HTTP {response.status_code}"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tarjetas de ofertas (estructura típica de sitios de empleo)
            # Este selector depende de la estructura actual de Chiletrabajos
            job_cards = soup.find_all('div', class_=['job-card', 'job-listing', 'job-item'])
            
            if not job_cards:
                # Intentar selectores alternativos
                job_cards = soup.find_all('article', class_='job')
            
            if not job_cards:
                job_cards = soup.find_all('li', class_=['job', 'job-item'])
            
            for card in job_cards:
                try:
                    oferta = {
                        'titulo': self._extraer_titulo(card),
                        'empresa': self._extraer_empresa(card),
                        'ciudad': self._extraer_ciudad(card),
                        'pais': 'Chile',  # Chiletrabajos es sitio chileno
                        'descripcion': self._extraer_descripcion(card),
                        'url': self._extraer_url(card),
                        'salario': self._extraer_salario(card),
                        'fecha_publicacion': self._extraer_fecha(card),
                        'source': 'Chiletrabajos',
                        'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Validar que tenga datos mínimos
                    if oferta['titulo'] and oferta['url']:
                        ofertas.append(oferta)
                        
                except Exception as e:
                    logger.debug(f"Error extrayendo oferta: {str(e)}")
                    continue
            
            logger.info(f"[{self.source_name}] {len(ofertas)} ofertas extraídas")
            return ofertas, True, f"{len(ofertas)} ofertas extraídas"
            
        except Exception as e:
            logger.error(f"[{self.source_name}] Error: {str(e)}")
            return [], False, str(e)
    
    def _extraer_titulo(self, card) -> str:
        """Extrae título del trabajo"""
        selectors = ['h2.job-title', '.job-title', 'a.job-link', 'h3']
        for selector in selectors:
            elem = card.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return "N/A"
    
    def _extraer_empresa(self, card) -> str:
        """Extrae nombre de empresa"""
        selectors = ['.company-name', '.empresa', '.employer', '.job-company']
        for selector in selectors:
            elem = card.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return "N/A"
    
    def _extraer_ciudad(self, card) -> str:
        """Extrae ubicación/ciudad"""
        selectors = ['.location', '.city', '.ciudad', '.ubicacion']
        for selector in selectors:
            elem = card.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return "No especificada"
    
    def _extraer_descripcion(self, card) -> str:
        """Extrae descripción del puesto"""
        selectors = ['.job-description', '.descripcion', 'p.description', 'p']
        for selector in selectors:
            elem = card.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                return text[:500]  # Primeros 500 caracteres
        return "No disponible"
    
    def _extraer_url(self, card) -> str:
        """Extrae URL de la oferta"""
        # Buscar enlace principal
        link = card.find('a', href=True)
        if link:
            href = link.get('href')
            # Si es URL relativa, convertir a absoluta
            if href.startswith('/'):
                return f"{self.base_url}{href}"
            elif href.startswith('http'):
                return href
        return ""
    
    def _extraer_salario(self, card) -> str:
        """Extrae rango salarial"""
        selectors = ['.salary', '.sueldo', '.compensation']
        for selector in selectors:
            elem = card.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return "No especificado"
    
    def _extraer_fecha(self, card) -> str:
        """Extrae fecha de publicación"""
        selectors = ['.date', '.fecha', 'time', '.posted-date']
        for selector in selectors:
            elem = card.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                return text if text else datetime.now().strftime('%Y-%m-%d')
        return datetime.now().strftime('%Y-%m-%d')


class TrabajandoClScraperV2(ScraperBase):
    """Scraper para Trabajando.cl - Portal de empleos latino"""
    
    def __init__(self):
        super().__init__(
            "Trabajando.cl",
            "https://www.trabajando.cl"
        )
        # Trabajando.cl tiene URLs públicas de búsqueda
        self.search_url = "https://www.trabajando.cl/jobs?search={keyword}&location={location}"
        
    def scrape(self, keyword: str = "python developer", location: str = "santiago", **kwargs) -> Tuple[List[Dict], bool, str]:
        """Scrape ofertas de Trabajando.cl"""
        ofertas = []
        
        try:
            url = self.search_url.format(keyword=keyword, location=location)
            logger.info(f"[{self.source_name}] Scrapeando: {url}")
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return [], False, f"HTTP {response.status_code}"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trabajando.cl usa divs con clase 'job-item' o similar
            job_cards = soup.find_all('div', class_=['job-item', 'job-card', 'offer'])
            
            for card in job_cards:
                try:
                    oferta = {
                        'titulo': self._extraer_titulo(card),
                        'empresa': self._extraer_empresa(card),
                        'ciudad': self._extraer_ciudad(card),
                        'pais': 'Chile',
                        'descripcion': self._extraer_descripcion(card),
                        'url': self._extraer_url(card),
                        'salario': self._extraer_salario(card),
                        'source': 'Trabajando.cl',
                        'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    if oferta['titulo'] and oferta['url']:
                        ofertas.append(oferta)
                        
                except Exception as e:
                    logger.debug(f"Error extrayendo oferta: {str(e)}")
                    continue
            
            logger.info(f"[{self.source_name}] {len(ofertas)} ofertas extraídas")
            return ofertas, True, f"{len(ofertas)} ofertas extraídas"
            
        except Exception as e:
            logger.error(f"[{self.source_name}] Error: {str(e)}")
            return [], False, str(e)
    
    def _extraer_titulo(self, card) -> str:
        title = card.select_one('h2, h3, .job-title')
        return title.get_text(strip=True) if title else "N/A"
    
    def _extraer_empresa(self, card) -> str:
        empresa = card.select_one('.company, .empresa')
        return empresa.get_text(strip=True) if empresa else "N/A"
    
    def _extraer_ciudad(self, card) -> str:
        ciudad = card.select_one('.city, .location, .ubicacion')
        return ciudad.get_text(strip=True) if ciudad else "No especificada"
    
    def _extraer_descripcion(self, card) -> str:
        desc = card.select_one('.description, p')
        if desc:
            return desc.get_text(strip=True)[:500]
        return "No disponible"
    
    def _extraer_url(self, card) -> str:
        link = card.find('a', href=True)
        if link:
            href = link.get('href')
            if href.startswith('/'):
                return f"{self.base_url}{href}"
            return href
        return ""
    
    def _extraer_salario(self, card) -> str:
        salary = card.select_one('.salary, .sueldo')
        return salary.get_text(strip=True) if salary else "No especificado"


class IndeedPublicScraper(ScraperBase):
    """
    Scraper para Indeed usando búsqueda pública
    (Indeed permite scraping de resultados públicos sin API)
    """
    
    def __init__(self):
        super().__init__(
            "Indeed",
            "https://indeed.com"
        )
        self.search_url = "https://indeed.com/jobs?q={keyword}&l={location}"
        
    def scrape(self, keyword: str = "python", location: str = "chile", **kwargs) -> Tuple[List[Dict], bool, str]:
        """Scrape ofertas públicas de Indeed"""
        ofertas = []
        
        try:
            url = self.search_url.format(keyword=keyword, location=location)
            logger.info(f"[{self.source_name}] Scrapeando: {url}")
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return [], False, f"HTTP {response.status_code}"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Indeed usa divs con data-company-name
            job_cards = soup.find_all('div', class_='job')
            
            for card in job_cards:
                try:
                    oferta = {
                        'titulo': self._extraer_titulo(card),
                        'empresa': self._extraer_empresa(card),
                        'ciudad': self._extraer_ubicacion(card),
                        'pais': 'International',
                        'descripcion': self._extraer_descripcion(card),
                        'url': self._extraer_url(card),
                        'salario': self._extraer_salario(card),
                        'source': 'Indeed',
                        'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    if oferta['titulo'] and oferta['url']:
                        ofertas.append(oferta)
                        
                except Exception as e:
                    logger.debug(f"Error extrayendo oferta: {str(e)}")
                    continue
            
            logger.info(f"[{self.source_name}] {len(ofertas)} ofertas extraídas")
            return ofertas, True, f"{len(ofertas)} ofertas extraídas"
            
        except Exception as e:
            logger.error(f"[{self.source_name}] Error: {str(e)}")
            return [], False, str(e)
    
    def _extraer_titulo(self, card) -> str:
        title = card.select_one('h2.jobTitle span')
        return title.get_text(strip=True) if title else "N/A"
    
    def _extraer_empresa(self, card) -> str:
        empresa = card.select_one('[data-company-name]')
        return empresa.get_text(strip=True) if empresa else "N/A"
    
    def _extraer_ubicacion(self, card) -> str:
        loc = card.select_one('.companyLocation')
        return loc.get_text(strip=True) if loc else "No especificada"
    
    def _extraer_descripcion(self, card) -> str:
        desc = card.select_one('.summary')
        if desc:
            return desc.get_text(strip=True)[:500]
        return "No disponible"
    
    def _extraer_url(self, card) -> str:
        link = card.find('a', href=True)
        if link:
            href = link.get('href')
            if href.startswith('/'):
                return f"{self.base_url}{href}"
            return href
        return ""
    
    def _extraer_salario(self, card) -> str:
        salary = card.select_one('.salary-snippet')
        return salary.get_text(strip=True) if salary else "No especificado"


class MultiSourceAggregator:
    """Agregador que combina ofertas de múltiples fuentes"""
    
    def __init__(self):
        self.scrapers = {
            'linkedin': None,  # Se pasa externamente desde collector
            'chiletrabajos': ChileTrabajosScraperV2(),
            'trabajando': TrabajandoClScraperV2(),
            'indeed': IndeedPublicScraper(),
        }
        self.todas_las_ofertas = []
        self.resultados_por_fuente = {}
        
    def agregar_scraper_linkedin(self, linkedin_ofertas: List[Dict]):
        """Agregar ofertas de LinkedIn (del collector existente)"""
        self.resultados_por_fuente['linkedin'] = {
            'ofertas': linkedin_ofertas,
            'exito': True,
            'mensaje': f"{len(linkedin_ofertas)} ofertas de LinkedIn"
        }
        self.todas_las_ofertas.extend(linkedin_ofertas)
        
    def scrape_todas_las_fuentes(self, keywords: List[str] = None, locations: List[str] = None) -> Dict:
        """
        Scrape todas las fuentes (excepto LinkedIn que se agrega manualmente)
        
        Args:
            keywords: Palabras clave de búsqueda ['python', 'developer']
            locations: Ubicaciones ['santiago', 'chile']
        """
        if not keywords:
            keywords = ['python developer']
        if not locations:
            locations = ['chile', 'santiago']
        
        logger.info("="*80)
        logger.info("INICIANDO SCRAPING MULTI-FUENTE")
        logger.info("="*80)
        
        for fuente_name, scraper in self.scrapers.items():
            if fuente_name == 'linkedin':
                continue  # LinkedIn se maneja aparte
            
            if not scraper:
                continue
            
            logger.info(f"\n[SCRAPING] {fuente_name.upper()}...")
            
            for keyword in keywords:
                for location in locations:
                    try:
                        ofertas, exito, mensaje = scraper.scrape(
                            keyword=keyword,
                            location=location
                        )
                        
                        self.resultados_por_fuente[fuente_name] = {
                            'ofertas': ofertas,
                            'exito': exito,
                            'mensaje': mensaje,
                            'keyword': keyword,
                            'location': location
                        }
                        
                        if exito and ofertas:
                            self.todas_las_ofertas.extend(ofertas)
                            logger.info(f"  ✓ {mensaje}")
                        else:
                            logger.warning(f"  ✗ {mensaje}")
                        
                        time.sleep(2)  # Respetar rate limiting
                        
                    except Exception as e:
                        logger.error(f"  Error en {fuente_name}: {str(e)}")
                        continue
        
        logger.info(f"\n{'='*80}")
        logger.info(f"TOTAL DE OFERTAS EXTRAÍDAS: {len(self.todas_las_ofertas)}")
        logger.info(f"{'='*80}\n")
        
        return self._generar_reporte()
    
    def _generar_reporte(self) -> Dict:
        """Genera reporte de scraping"""
        reporte = {
            'timestamp': datetime.now().isoformat(),
            'total_ofertas': len(self.todas_las_ofertas),
            'por_fuente': {}
        }
        
        for fuente, resultados in self.resultados_por_fuente.items():
            reporte['por_fuente'][fuente] = {
                'cantidad': len(resultados.get('ofertas', [])),
                'exito': resultados.get('exito'),
                'mensaje': resultados.get('mensaje')
            }
        
        return reporte
    
    def obtener_todas_ofertas(self) -> List[Dict]:
        """Retorna todas las ofertas consolidadas"""
        return self.todas_las_ofertas
    
    def deduplicar_ofertas(self) -> List[Dict]:
        """Elimina duplicadas basado en URL similar"""
        urls_vistas = set()
        ofertas_unicas = []
        
        for oferta in self.todas_las_ofertas:
            url = oferta.get('url', '')
            # Normalizar URL para comparación
            url_norm = url.lower().strip()
            
            if url_norm and url_norm not in urls_vistas:
                urls_vistas.add(url_norm)
                ofertas_unicas.append(oferta)
        
        logger.info(f"Deduplicadas ofertas: {len(self.todas_las_ofertas)} → {len(ofertas_unicas)}")
        return ofertas_unicas


def main():
    """Demo del agregador multi-fuente"""
    
    agregador = MultiSourceAggregator()
    
    # Ejemplo: agregar ofertas de LinkedIn (simularemos con ejemplo)
    ofertas_linkedin_ejemplo = [
        {
            'titulo': 'Senior Python Developer',
            'empresa': 'Tech Corp',
            'ciudad': 'Santiago',
            'pais': 'Chile',
            'salario': '$3000-5000 USD',
            'descripcion': 'Buscamos senior python...',
            'url': 'https://linkedin.com/jobs/1',
            'source': 'LinkedIn',
            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    agregador.agregar_scraper_linkedin(ofertas_linkedin_ejemplo)
    
    # Scrape las otras fuentes
    reporte = agregador.scrape_todas_las_fuentes(
        keywords=['python', 'desarrollador'],
        locations=['santiago', 'chile']
    )
    
    # Mostrar reporte
    logger.info("\nREPORTE FINAL:")
    logger.info(json.dumps(reporte, indent=2, default=str))
    
    # Deduplicar
    ofertas_finales = agregador.deduplicar_ofertas()
    
    logger.info(f"\nOfertas finales para procesar: {len(ofertas_finales)}")
    for i, oferta in enumerate(ofertas_finales[:5], 1):
        logger.info(f"{i}. {oferta['titulo']} ({oferta['source']})")


if __name__ == "__main__":
    main()
