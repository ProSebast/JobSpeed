"""
Collector: Extrae SOLO LINKS de ofertas usando Chrome/Selenium
Sin iniciar sesión. Sin datos simulados - solo URLs reales.
"""
import logging
import time
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Collector:
    """Extrae SOLO LINKS de LinkedIn usando Chrome/Selenium. Sin fallback simulado."""

    def __init__(self):
        self.ofertas_raw: List[Dict] = []
        self.driver = None

    def _cerrar_driver(self):
        """Cierra el navegador si está abierto"""
        if self.driver:
            try:
                logger.info('[COLLECTOR] Cerrando navegador Chrome...')
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.debug(f'Error cerrando driver: {e}')
                self.driver = None

    def buscar_ofertas(self, query: str = 'python developer', ubicacion: str = '', cantidad: int = 30) -> List[Dict]:
        """
        Extrae SOLO links de ofertas desde LinkedIn usando Chrome/Selenium.
        Sin datos simulados. Si falla, retorna vacio.
        
        Args:
            query: termino de busqueda (ej: 'python developer')
            ubicacion: ubicacion (ej: 'Chile')
            cantidad: numero de links a extraer
            
        Returns:
            Lista de {id, titulo, url} dicts
        """
        logger.info(f"[COLLECTOR] Iniciando extraccion de links: '{query}' ({ubicacion}) -> {cantidad}")

        try:
            logger.info('[COLLECTOR] Iniciando navegador Chrome...')
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

            path = ChromeDriverManager().install()
            import os, glob
            driver_exe = None
            if os.path.isfile(path) and path.lower().endswith('.exe'):
                driver_exe = path
            else:
                base_dir = os.path.dirname(path)
                matches = glob.glob(os.path.join(base_dir, '**', 'chromedriver*.exe'), recursive=True)
                if matches:
                    driver_exe = matches[0]
                else:
                    candidate = os.path.join(base_dir, 'chromedriver-win32', 'chromedriver.exe')
                    if os.path.isfile(candidate):
                        driver_exe = candidate

            if not driver_exe:
                logger.error('[COLLECTOR] chromedriver.exe no encontrado')
                return []

            service = Service(driver_exe)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info('[COLLECTOR] Navegador iniciado')

            query_enc = query.replace(' ', '%20')
            location_param = f"&location={ubicacion}" if ubicacion else ''
            url_search = f"https://www.linkedin.com/jobs/search/?keywords={query_enc}{location_param}"

            logger.info(f'[COLLECTOR] Accediendo a LinkedIn: {url_search}')
            self.driver.get(url_search)
            time.sleep(3)

            # Scroll para cargar mas ofertas
            logger.info('[COLLECTOR] Scrolling para cargar ofertas...')
            for i in range(5):
                self.driver.execute_script('window.scrollBy(0, 500)')
                time.sleep(0.5)

            # Extraer enlaces a ofertas: a[href*="/jobs/view/"]
            logger.info('[COLLECTOR] Extrayendo enlaces...')
            anchors = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/jobs/view/"]')
            
            urls_set = set()  # Para deduplicar automáticamente
            for a in anchors:
                try:
                    href = a.get_attribute('href')
                    if href and '/jobs/view/' in href:
                        # Limpiar parametros
                        clean_url = href.split('?')[0]
                        urls_set.add(clean_url)
                except:
                    continue

            urls = list(urls_set)[:cantidad]
            logger.info(f'[COLLECTOR] Total enlaces extraidos: {len(urls)}')

            if not urls:
                logger.warning('[COLLECTOR] No se extrajeron enlaces (LinkedIn puede estar bloqueado o requiere login)')
                self._cerrar_driver()
                return []

            # Crear ofertas simples: solo id, titulo, url
            ofertas = []
            for idx, link_url in enumerate(urls, 1):
                oferta = {
                    'id': idx,
                    'titulo': f'Oferta {idx}',  # Titulo minimo
                    'url': link_url,
                    'fuente': 'linkedin'
                }
                ofertas.append(oferta)
                logger.debug(f'[COLLECTOR] Link {idx}: {link_url}')

            self.ofertas_raw = ofertas
            logger.info(f'[COLLECTOR] Total ofertas procesadas: {len(ofertas)}')
            self._cerrar_driver()
            return ofertas

        except Exception as e:
            logger.error(f'[COLLECTOR] Error durante extraccion: {str(e)[:100]}')
            self._cerrar_driver()
            return []

    def deduplicar(self) -> List[Dict]:
        """Elimina URLs duplicadas"""
        urls_vistas = set()
        ofertas_unicas = []

        for oferta in self.ofertas_raw:
            url = oferta.get('url', '')
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                ofertas_unicas.append(oferta)

        self.ofertas_raw = ofertas_unicas
        logger.info(f"[COLLECTOR] Deduplicacion: {len(ofertas_unicas)} enlaces unicos")
        return self.ofertas_raw

    def obtener_ofertas(self) -> List[Dict]:
        """Retorna los links extraidos"""
        return self.ofertas_raw


if __name__ == '__main__':
    collector = Collector()
    ofertas = collector.buscar_ofertas('python developer', ubicacion='Chile', cantidad=10)
    collector.deduplicar()
    print(f"\nTotal extraido: {len(collector.obtener_ofertas())} enlaces")
    for oferta in collector.obtener_ofertas():
        print(f"  - {oferta['url']}")

