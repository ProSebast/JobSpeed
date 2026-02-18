#!/usr/bin/env python3
"""
Multi-Source Job Scraper
Integra múltiples fuentes de portales de empleo para recolectar ofertas activas
Soporta: LinkedIn, Indeed, Chiletrabajos, Trabajando.cl y otros

ANÁLISIS DE FUENTES:
✓ ACTIVAS (implementadas):
  - LinkedIn Jobs: Via Collector existente
  
⚠ LIMITADAS (requieren alternativas):
  - Indeed: API requiere credenciales de pago + CORS issues
  - GetOnBoard: Bloquea scraping con User-Agent blocks
  - Stack Overflow: Bloquea scraping/API access (403 Forbidden)
  - Chiletrabajos: No API pública (404)
  - Trabajando.cl: No API pública (404)

SOLUCIÓN: Usar combinación de:
1. LinkedIn (via collector existente)
2. Búsquedas web con requests para obtener URLs de ofertas
3. Scraping selectivo donde sea permitido
"""

import logging
import requests
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JobSource:
    """Información de una fuente de ofertas"""
    name: str
    api_url: Optional[str]
    has_public_api: bool
    type: str  # 'api', 'scraping', 'unavailable'
    status: str = "unknown"  # unknown, active, inactive, requires_auth, not_available
    message: Optional[str] = None
    difficulty: str = "N/A"  # Easy, Medium, Hard, Not Available


class JobSourceBase(ABC):
    """Clase base para fuentes de ofertas"""
    
    def __init__(self, source_name: str, source_type: str, api_url: Optional[str] = None):
        self.source_name = source_name
        self.source_type = source_type  # 'api', 'scraping', 'unavailable'
        self.api_url = api_url
        self.session = requests.Session()
        self.session.timeout = 10
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    @abstractmethod
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """Obtener ofertas de trabajo - retorna (jobs, success, message)"""
        pass
    
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión a la fuente"""
        if not self.api_url:
            return False, "No API/source URL available"
        
        try:
            response = self.session.head(self.api_url, timeout=5, allow_redirects=True)
            if response.status_code in [200, 301, 302]:
                return True, "Connection successful"
            elif response.status_code == 401:
                return False, "Authentication required (API key/login needed)"
            elif response.status_code == 403:
                return False, "Forbidden (scraping/access blocked)"
            elif response.status_code == 404:
                return False, "Not found (invalid API endpoint)"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.Timeout:
            return False, "Connection timeout"
        except requests.ConnectionError:
            return False, "Connection refused (API not accessible)"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"


class LinkedInCollectorWrapper(JobSourceBase):
    """Envuelve el Collector existente de LinkedIn"""
    
    def __init__(self):
        super().__init__("LinkedIn", "api", "https://linkedin.com/jobs")
        
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """Usa el collector existente para LinkedIn"""
        try:
            # Intentar importar y usar el collector existente
            sys.path.insert(0, str(Path(__file__).parent))
            from collector import Collector
            
            logger.info("LinkedIn: Using existing Collector module")
            return [], True, "Available via collector.py"
        except ImportError:
            return [], False, "Collector module not found"
        except Exception as e:
            return [], False, str(e)


class ChileTrabajosSource(JobSourceBase):
    """
    Chiletrabajos - No tiene API pública
    Análisis: Sitio requiere login para búsquedas avanzadas
    """
    
    def __init__(self):
        super().__init__("Chiletrabajos", "unavailable", "https://www.chiletrabajos.cl")
        
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """No disponible sin scraping complejo"""
        return [], False, "No public API. Requires authenticated scraping."


class TrabajandoClSource(JobSourceBase):
    """
    Trabajando.cl - No tiene API pública
    Análisis: Sitio dinamizado con JavaScript
    """
    
    def __init__(self):
        super().__init__("Trabajando.cl", "unavailable", "https://www.trabajando.cl")
        
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """No disponible sin Selenium/Playwright"""
        return [], False, "No public API. Requires JS rendering (Selenium/Playwright)."


class IndeedSource(JobSourceBase):
    """
    Indeed - API privada con restricciones
    Análisis: Requiere API key de pago + CORS bloqueado
    """
    
    def __init__(self):
        super().__init__("Indeed", "api", "https://api.indeed.com/v2/search")
        
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """Requiere credenciales de pago"""
        return [], False, "Requires paid API key. CORS-blocked from browsers."


class GetOnBoardSource(JobSourceBase):
    """
    GetOnBoard - Bloquea scraping
    Análisis: Cloudflare + User-Agent validation
    """
    
    def __init__(self):
        super().__init__("GetOnBoard", "api", "https://getonboard.com/api/v2/jobs")
        
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """Bloqueado por Cloudflare"""
        return [], False, "Blocked by Cloudflare WAF. Requires playwright/undetected-chromedriver."


class StackOverflowSource(JobSourceBase):
    """
    Stack Overflow Jobs - Bloquea acceso
    Análisis: Requiere autenticación + bloquea bots
    """
    
    def __init__(self):
        super().__init__("Stack Overflow", "api", "https://stackoverflow.com/jobs")
        
    def fetch_jobs(self, **kwargs) -> Tuple[List[Dict], bool, str]:
        """Bloqueado por protección bot"""
        return [], False, "Blocks bot scraping (403 Forbidden)."



class GetOnBoardScraper(JobSourceBase):
    """GetOnBoard API - Portal latino de ofertas técnicas"""
    
    def __init__(self):
        api_url = "https://getonboard.com/api/v2/jobs"
        super().__init__("GetOnBoard", api_url)
        self.country = "cl"  # Chile
        self.page = 1
        
    def fetch_jobs(self, **kwargs) -> List[Dict]:
        """Obtener ofertas de GetOnBoard"""
        jobs = []
        try:
            params = {
                'country': self.country,
                'page': self.page,
                'per_page': 50
            }
            
            response = self.session.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                offers = data.get('data', [])
                
                for offer in offers:
                    job = {
                        'id': offer.get('id'),
                        'titulo': offer.get('title'),
                        'empresa': offer.get('company_name'),
                        'ubicacion': offer.get('location'),
                        'descripcion': offer.get('description'),
                        'url': offer.get('url'),
                        'fecha_creacion': offer.get('created_at'),
                        'salary': offer.get('salary'),
                        'source': 'GetOnBoard',
                        'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    jobs.append(job)
                
                logger.info(f"GetOnBoard: {len(jobs)} ofertas obtenidas")
                return jobs
        except Exception as e:
            logger.error(f"GetOnBoard error: {e}")
        
        return jobs


class IndeedScraper(JobSourceBase):
    """Indeed API - Requiere API key"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_url = "https://api.indeed.com/v2/search"
        super().__init__("Indeed", api_url)
        self.api_key = api_key
        self.requires_auth = True
        
    def fetch_jobs(self, **kwargs) -> List[Dict]:
        """Obtener ofertas de Indeed - requiere API key"""
        if not self.api_key:
            logger.warning("Indeed: API key not provided")
            return []
        
        jobs = []
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            params = {
                'query': kwargs.get('query', 'Python Developer'),
                'location': kwargs.get('location', 'Santiago, Chile'),
                'limit': 50
            }
            
            response = self.session.get(self.api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                offers = data.get('results', [])
                
                for offer in offers:
                    job = {
                        'id': offer.get('jobkey'),
                        'titulo': offer.get('jobtitle'),
                        'empresa': offer.get('company'),
                        'ubicacion': offer.get('locations'),
                        'descripcion': offer.get('snippet'),
                        'url': offer.get('url'),
                        'salary': offer.get('salary'),
                        'source': 'Indeed',
                        'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    jobs.append(job)
                
                logger.info(f"Indeed: {len(jobs)} ofertas obtenidas")
                return jobs
        except Exception as e:
            logger.error(f"Indeed error: {e}")
        
        return jobs


class StackOverflowScraper(JobSourceBase):
    """Stack Overflow Jobs - Sin API oficial, scraping desde página"""
    
    def __init__(self):
        # Stack Overflow no tiene API pública para jobs, pero tienen structured data
        api_url = "https://stackoverflow.com/jobs?q=python&l=chile&d=50&u=Km"
        super().__init__("Stack Overflow", api_url)
        
    def fetch_jobs(self, **kwargs) -> List[Dict]:
        """SO no tiene API pública, requeriría scraping con BeautifulSoup"""
        logger.warning("Stack Overflow: No public API available, scraping would be required")
        return []


class LinkedInJobsScraper(JobSourceBase):
    """LinkedIn Jobs - Usar collector existente"""
    
    def __init__(self):
        # No hay API pública de LinkedIn, se usa el collector existente
        super().__init__("LinkedIn", None)
        
    def fetch_jobs(self, **kwargs) -> List[Dict]:
        """LinkedIn se maneja via collector existente"""
        logger.info("LinkedIn: Use existing src/collector.py")
        return []


class ChileTrabajosChecker(JobSourceBase):
    """Chiletrabajos - Verificar disponibilidad de API"""
    
    def __init__(self):
        # Chiletrabajos no tiene API pública oficial
        api_url = "https://www.chiletrabajos.cl/api/jobs"  # Intento
        super().__init__("Chiletrabajos", api_url)
        
    def fetch_jobs(self, **kwargs) -> List[Dict]:
        """Chiletrabajos no tiene API pública"""
        logger.warning("Chiletrabajos: No public API available")
        return []


class TrabajandoClChecker(JobSourceBase):
    """Trabajando.cl - Verificar disponibilidad"""
    
    def __init__(self):
        # Trabajando.cl no tiene API pública oficial
        api_url = "https://api.trabajando.cl/v1/jobs"  # Intento
        super().__init__("Trabajando.cl", api_url)
        
    def fetch_jobs(self, **kwargs) -> List[Dict]:
        """Trabajando.cl no tiene API pública"""
        logger.warning("Trabajando.cl: No public API available")
        return []


class MultiSourceJobScraper:
    """Orquestador de múltiples fuentes de ofertas"""
    
    def __init__(self):
        self.sources: Dict[str, JobSourceBase] = {}
        self.connection_report: Dict[str, JobSource] = {}
        self._initialize_sources()
        
    def _initialize_sources(self):
        """Inicializar todas las fuentes disponibles"""
        logger.info("="*80)
        logger.info("INITIALIZING JOB SOURCES")
        logger.info("="*80)
        
        # Agregar nuevas fuentes mejoradas
        self.sources['linkedin'] = LinkedInCollectorWrapper()
        self.sources['chiletrabajos'] = ChileTrabajosSource()
        self.sources['trabajando'] = TrabajandoClSource()
        self.sources['indeed'] = IndeedSource()
        self.sources['getonboard'] = GetOnBoardSource()
        self.sources['stackoverflow'] = StackOverflowSource()
        
    def test_all_sources(self) -> Dict:
        """Prueba conexión a todas las fuentes"""
        logger.info("\n" + "="*80)
        logger.info("TESTING JOB SOURCES")
        logger.info("="*80)
        
        results = {}
        
        for source_name, scraper in self.sources.items():
            logger.info(f"\n[{source_name.upper()}]")
            
            # Crear entrada en reporte
            source_info = JobSource(
                name=scraper.source_name,
                api_url=scraper.api_url,
                has_public_api=scraper.api_url is not None,
                type=scraper.source_type
            )
            
            # Test de conexión si tiene URL
            if scraper.api_url:
                success, message = scraper.test_connection()
                source_info.status = "active" if success else "inactive"
                source_info.message = message
            else:
                source_info.status = "not_available"
                source_info.message = "No URL available"
            
            self.connection_report[scraper.source_name] = source_info
            
            # Log resultado
            status_icon = "✓" if source_info.status == "active" else "✗"
            logger.info(f"  {status_icon} Type: {source_info.type}")
            logger.info(f"  {status_icon} Status: {source_info.status}")
            logger.info(f"  {status_icon} Message: {source_info.message}")
            
            results[source_name] = asdict(source_info)
        
        return results
    
    def print_detailed_report(self):
        """Muestra reporte detallado de conexiones"""
        logger.info("\n" + "="*80)
        logger.info("JOB SOURCES AVAILABILITY REPORT")
        logger.info("="*80)
        
        # Categorizar por disponibilidad
        available = []
        unavailable_auth = []
        unavailable_blocked = []
        unavailable_no_api = []
        
        for source_name, info in self.connection_report.items():
            if info.status == "active":
                available.append((source_name, info))
            elif "API key" in info.message or "Authentication" in info.message:
                unavailable_auth.append((source_name, info))
            elif "Blocked" in info.message or "Forbidden" in info.message:
                unavailable_blocked.append((source_name, info))
            else:
                unavailable_no_api.append((source_name, info))
        
        # Mostrar disponibles
        logger.info("\n[AVAILABLE SOURCES]")
        if available:
            for source_name, info in available:
                logger.info(f"  OK - {info.name} ({info.type})")
                logger.info(f"       URL: {info.api_url}")
        else:
            logger.info("  None currently available without authentication")
        
        # Mostrar que requieren autenticación
        logger.info("\n[REQUIRES AUTHENTICATION]")
        if unavailable_auth:
            for source_name, info in unavailable_auth:
                logger.info(f"  AUTH - {info.name}")
                logger.info(f"         {info.message}")
        else:
            logger.info("  None")
        
        # Mostrar bloqueados
        logger.info("\n[BLOCKED/PROTECTED]")
        if unavailable_blocked:
            for source_name, info in unavailable_blocked:
                logger.info(f"  BLOCK - {info.name}")
                logger.info(f"          {info.message}")
        else:
            logger.info("  None")
        
        # Mostrar sin API pública
        logger.info("\n[NO PUBLIC API]")
        if unavailable_no_api:
            for source_name, info in unavailable_no_api:
                logger.info(f"  NONE - {info.name}")
                logger.info(f"         {info.message}")
        else:
            logger.info("  None")
        
        # Resumen
        logger.info("\n" + "-"*80)
        logger.info(f"SUMMARY:")
        logger.info(f"  Total sources: {len(self.sources)}")
        logger.info(f"  Available: {len(available)}")
        logger.info(f"  Requires auth: {len(unavailable_auth)}")
        logger.info(f"  Blocked: {len(unavailable_blocked)}")
        logger.info(f"  No API: {len(unavailable_no_api)}")
        logger.info("-"*80)
        
        return {
            'total': len(self.sources),
            'available': [(n, asdict(i)) for n, i in available],
            'requires_auth': [(n, asdict(i)) for n, i in unavailable_auth],
            'blocked': [(n, asdict(i)) for n, i in unavailable_blocked],
            'no_api': [(n, asdict(i)) for n, i in unavailable_no_api]
        }
    
    def print_next_steps(self):
        """Mostrar pasos sugeridos para completar integración"""
        logger.info("\n" + "="*80)
        logger.info("NEXT STEPS TO ENABLE MORE SOURCES")
        logger.info("="*80)
        
        logger.info("\n[FOR LINKEDIN]")
        logger.info("  ✓ Already integrated via src/collector.py")
        logger.info("  Usage: python main.py (handles LinkedIn scraping)")
        
        logger.info("\n[FOR INDEED]")
        logger.info("  1. Get API key from: https://opensource.indeedeng.io/api/")
        logger.info("  2. Configure API_KEY in environment variables")
        logger.info("  3. Update IndeedSource with authentication headers")
        
        logger.info("\n[FOR GETONBOARD]")
        logger.info("  1. Check if API is available: https://getonboard.com/api/docs")
        logger.info("  2. May require authentication or proxy bypass")
        logger.info("  3. Consider: undetected-chromedriver if Cloudflare blocks")
        
        logger.info("\n[FOR CHILETRABAJOS & TRABAJANDO.CL]")
        logger.info("  1. Install: pip install selenium beautifulsoup4")
        logger.info("  2. Implement ScrapingService with Selenium WebDriver")
        logger.info("  3. Or use: Playwright for better performance")
        logger.info("  4. Note: May violate ToS, use responsibly")
        
        logger.info("\n[FOR STACKOVERFLOW]")
        logger.info("  1. Check for API at: https://stackoverflow.com/api")
        logger.info("  2. Use Playwright for JS-rendered content")
        logger.info("  3. May need proxy rotation to avoid blocking")
        
        logger.info("\n" + "="*80)
    
    def get_available_sources(self) -> List[str]:
        """Retorna lista de fuentes activas"""
        return [info.name for info in self.connection_report.values() 
                if info.status == "active"]
    
    def get_source_status(self, source_name: str) -> Optional[JobSource]:
        """Obtener estado de una fuente específica"""
        return self.connection_report.get(source_name)


def main():
    """Script de prueba de fuentes de empleo"""
    
    scraper = MultiSourceJobScraper()
    
    # Prueba todas las conexiones
    logger.info("Testing all job sources...")
    test_results = scraper.test_all_sources()
    
    # Imprime reporte detallado
    report = scraper.print_detailed_report()
    
    # Mostrar pasos siguientes
    scraper.print_next_steps()
    
    # Reporte JSON para referencia
    logger.info("\n" + "="*80)
    logger.info("JSON REPORT")
    logger.info("="*80)
    logger.info(json.dumps(report, default=str, indent=2))
    
    return scraper


if __name__ == "__main__":
    scraper = main()
