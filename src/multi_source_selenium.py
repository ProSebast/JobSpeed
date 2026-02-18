#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Source Scraper v2 - CON SELENIUM PARA TODAS LAS FUENTES
Usa navegador Chrome real para evitar bloqueos WAF y bot detection
"""

import logging
import time
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import sys
import os

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detectar ruta de Chrome
CHROME_PATHS = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Users\sebar\AppData\Local\Google\Chrome\Application\chrome.exe',
]

CHROME_PATH = None
for path in CHROME_PATHS:
    if os.path.exists(path):
        CHROME_PATH = path
        logger.info(f"[INIT] Chrome encontrado en: {CHROME_PATH}")
        break

if not CHROME_PATH:
    logger.warning("[INIT] Chrome no encontrado. Se usará webdriver-manager")


class SeleniumScraperBase(ABC):
    """Clase base para scrapers que usan Selenium (navegador real)"""
    
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.driver = None
        self.wait = None
        
    def _init_driver(self):
        """Inicializa el navegador Chrome"""
        try:
            options = Options()
            # options.add_argument('--headless')  # Comentado para ver qué está pasando
            options.add_argument('--start-maximized')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Si encontramos Chrome, usarlo directamente
            if CHROME_PATH:
                options.binary_location = CHROME_PATH
                try:
                    self.driver = webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=options
                    )
                except Exception as inner_e:
                    logger.debug(f"[{self.source_name}] Intento 1 fallo: {inner_e}")
                    # Intento 2: Sin especificar path
                    self.driver = webdriver.Chrome(
                        service=Service(),
                        options=options
                    )
            else:
                # Sin Chrome Path, usar webdriver-manager
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info(f"[{self.source_name}] Navegador Chrome inicializado")
            return True
        except Exception as e:
            logger.error(f"[{self.source_name}] Error iniciando Chrome: {str(e)}")
            return False
    
    def _quit_driver(self):
        """Cierra el navegador"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info(f"[{self.source_name}] Navegador cerrado")
            except:
                pass
    
    @abstractmethod
    def scrape(self, **kwargs):
        """Scrape usando navegador - implementar en subclases"""
        pass
    
    def test_connection(self):
        """Prueba conectividad"""
        try:
            self._init_driver()
            self.driver.get(self.base_url)
            time.sleep(2)
            conectado = self.driver.title is not None
            self._quit_driver()
            return True, "OK"
        except Exception as e:
            if self.driver:
                self._quit_driver()
            return False, str(e)


class ChileTrabajosSeleniumScraper(SeleniumScraperBase):
    """Scraper de Chiletrabajos usando Selenium"""
    
    def __init__(self):
        super().__init__(
            "Chiletrabajos",
            "https://www.chiletrabajos.cl"
        )
        self.search_url = "https://www.chiletrabajos.cl/?s={keyword}&l={location}"
    
    def scrape(self, keyword: str = "python", location: str = "santiago", **kwargs):
        """Scrape de Chiletrabajos con Selenium"""
        ofertas = []
        
        try:
            if not self._init_driver():
                return [], False, "Error iniciando navegador"
            
            url = self.search_url.format(keyword=keyword, location=location)
            logger.info(f"[{self.source_name}] Abriendo: {url}")
            
            self.driver.get(url)
            time.sleep(3)  # Esperar a que cargue la página
            
            # Buscar ofertas en la página
            try:
                # Intentar encontrar tarjetas de ofertas
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='job-card'], div.job-card, article.job, div.job-item")
                
                logger.info(f"[{self.source_name}] Encontradas {len(job_cards)} tarjetas de ofertas")
                
                for card in job_cards:
                    try:
                        oferta = {
                            'titulo': self._extraer_titulo_selenium(card),
                            'empresa': self._extraer_empresa_selenium(card),
                            'ciudad': self._extraer_ciudad_selenium(card),
                            'pais': 'Chile',
                            'salario': self._extraer_salario_selenium(card),
                            'descripcion': 'Ver en sitio',
                            'url': self._extraer_url_selenium(card),
                            'source': 'Chiletrabajos',
                            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if oferta['titulo'] and oferta['url']:
                            ofertas.append(oferta)
                            logger.debug(f"✓ Oferta extraída: {oferta['titulo']}")
                    
                    except Exception as e:
                        logger.debug(f"Error extrayendo oferta: {str(e)}")
                        continue
                
            except Exception as e:
                logger.warning(f"[{self.source_name}] Error buscando elementos: {str(e)}")
            
            self._quit_driver()
            logger.info(f"[{self.source_name}] {len(ofertas)} ofertas extraídas")
            return ofertas, True, f"{len(ofertas)} ofertas extraídas"
        
        except Exception as e:
            logger.error(f"[{self.source_name}] Error: {str(e)}")
            self._quit_driver()
            return [], False, str(e)
    
    def _extraer_titulo_selenium(self, element):
        try:
            titulo = element.find_element(By.CSS_SELECTOR, "h2, h3, a.job-title")
            return titulo.text.strip()
        except:
            return "N/A"
    
    def _extraer_empresa_selenium(self, element):
        try:
            empresa = element.find_element(By.CSS_SELECTOR, ".company, .empresa, .employer")
            return empresa.text.strip()
        except:
            return "N/A"
    
    def _extraer_ciudad_selenium(self, element):
        try:
            ciudad = element.find_element(By.CSS_SELECTOR, ".location, .city, .ciudad")
            return ciudad.text.strip()
        except:
            return "No especificada"
    
    def _extraer_salario_selenium(self, element):
        try:
            salario = element.find_element(By.CSS_SELECTOR, ".salary, .sueldo")
            return salario.text.strip()
        except:
            return "No especificado"
    
    def _extraer_url_selenium(self, element):
        try:
            link = element.find_element(By.CSS_SELECTOR, "a")
            href = link.get_attribute('href')
            if href:
                if href.startswith('/'):
                    return f"{self.base_url}{href}"
                return href
        except:
            pass
        return ""


class TrabajandoClSeleniumScraper(SeleniumScraperBase):
    """Scraper de Trabajando.cl usando Selenium"""
    
    def __init__(self):
        super().__init__(
            "Trabajando.cl",
            "https://www.trabajando.cl"
        )
        self.search_url = "https://www.trabajando.cl/jobs?search={keyword}&location={location}"
    
    def scrape(self, keyword: str = "python", location: str = "santiago", **kwargs):
        """Scrape de Trabajando.cl con Selenium"""
        ofertas = []
        
        try:
            if not self._init_driver():
                return [], False, "Error iniciando navegador"
            
            url = self.search_url.format(keyword=keyword, location=location)
            logger.info(f"[{self.source_name}] Abriendo: {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            try:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-card, div.job-item, article.job")
                
                logger.info(f"[{self.source_name}] Encontradas {len(job_cards)} ofertas")
                
                for card in job_cards:
                    try:
                        oferta = {
                            'titulo': self._extraer_titulo(card),
                            'empresa': self._extraer_empresa(card),
                            'ciudad': self._extraer_ciudad(card),
                            'pais': 'Chile',
                            'salario': self._extraer_salario(card),
                            'descripcion': 'Ver en sitio',
                            'url': self._extraer_url(card),
                            'source': 'Trabajando.cl',
                            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if oferta['titulo'] and oferta['url']:
                            ofertas.append(oferta)
                    
                    except:
                        continue
                
            except Exception as e:
                logger.warning(f"[{self.source_name}] Error: {str(e)}")
            
            self._quit_driver()
            logger.info(f"[{self.source_name}] {len(ofertas)} ofertas extraídas")
            return ofertas, True, f"{len(ofertas)} ofertas extraídas"
        
        except Exception as e:
            logger.error(f"[{self.source_name}] Error: {str(e)}")
            self._quit_driver()
            return [], False, str(e)
    
    def _extraer_titulo(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, "h2, h3").text.strip()
        except:
            return "N/A"
    
    def _extraer_empresa(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, ".company, .empresa").text.strip()
        except:
            return "N/A"
    
    def _extraer_ciudad(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, ".location, .city").text.strip()
        except:
            return "No especificada"
    
    def _extraer_salario(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, ".salary").text.strip()
        except:
            return "No especificado"
    
    def _extraer_url(self, element):
        try:
            link = element.find_element(By.TAG_NAME, "a")
            href = link.get_attribute('href')
            if href:
                if href.startswith('/'):
                    return f"{self.base_url}{href}"
                return href
        except:
            pass
        return ""


class IndeedSeleniumScraper(SeleniumScraperBase):
    """Scraper de Indeed usando Selenium"""
    
    def __init__(self):
        super().__init__(
            "Indeed",
            "https://indeed.com"
        )
        self.search_url = "https://indeed.com/jobs?q={keyword}&l={location}"
    
    def scrape(self, keyword: str = "python", location: str = "chile", **kwargs):
        """Scrape de Indeed con Selenium"""
        ofertas = []
        
        try:
            if not self._init_driver():
                return [], False, "Error iniciando navegador"
            
            url = self.search_url.format(keyword=keyword, location=location)
            logger.info(f"[{self.source_name}] Abriendo: {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            try:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job, div.jobsearch-SerpJobCard")
                
                logger.info(f"[{self.source_name}] Encontradas {len(job_cards)} ofertas")
                
                for card in job_cards:
                    try:
                        oferta = {
                            'titulo': self._extraer_titulo(card),
                            'empresa': self._extraer_empresa(card),
                            'ciudad': self._extraer_ciudad(card),
                            'pais': 'International',
                            'salario': self._extraer_salario(card),
                            'descripcion': 'Ver en sitio',
                            'url': self._extraer_url(card),
                            'source': 'Indeed',
                            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if oferta['titulo'] and oferta['url']:
                            ofertas.append(oferta)
                    
                    except:
                        continue
                
            except Exception as e:
                logger.warning(f"[{self.source_name}] Error: {str(e)}")
            
            self._quit_driver()
            logger.info(f"[{self.source_name}] {len(ofertas)} ofertas extraídas")
            return ofertas, True, f"{len(ofertas)} ofertas extraídas"
        
        except Exception as e:
            logger.error(f"[{self.source_name}] Error: {str(e)}")
            self._quit_driver()
            return [], False, str(e)
    
    def _extraer_titulo(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, "h2, a.jobtitle").text.strip()
        except:
            return "N/A"
    
    def _extraer_empresa(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, ".company").text.strip()
        except:
            return "N/A"
    
    def _extraer_ciudad(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, ".location").text.strip()
        except:
            return "No especificada"
    
    def _extraer_salario(self, element):
        try:
            return element.find_element(By.CSS_SELECTOR, ".salary").text.strip()
        except:
            return "No especificado"
    
    def _extraer_url(self, element):
        try:
            link = element.find_element(By.TAG_NAME, "a")
            href = link.get_attribute('href')
            if href:
                return href if href.startswith('http') else f"{self.base_url}{href}"
        except:
            pass
        return ""


class MultiSourceSeleniumAggregator:
    """Agregador que usa Selenium para todas las fuentes"""
    
    def __init__(self):
        self.scrapers = {
            'chiletrabajos': ChileTrabajosSeleniumScraper(),
            'trabajando': TrabajandoClSeleniumScraper(),
            'indeed': IndeedSeleniumScraper(),
        }
        self.todas_ofertas = []
    
    def scrape_multiples_fuentes(self, keywords=None, locations=None):
        """Scrape de todas las fuentes"""
        if not keywords:
            keywords = ['python developer']
        if not locations:
            locations = ['santiago']
        
        logger.info("="*80)
        logger.info("INICIANDO SCRAPING CON SELENIUM (NAVEGADOR REAL)")
        logger.info("="*80)
        
        for fuente_name, scraper in self.scrapers.items():
            logger.info(f"\n[SCRAPING] {fuente_name.upper()}...")
            
            for keyword in keywords:
                for location in locations:
                    try:
                        ofertas, exito, msg = scraper.scrape(
                            keyword=keyword,
                            location=location
                        )
                        
                        if exito and ofertas:
                            self.todas_ofertas.extend(ofertas)
                            logger.info(f"  [OK] {msg}")
                        else:
                            logger.warning(f"  [ERROR] {msg}")
                        
                        time.sleep(2)
                    
                    except Exception as e:
                        logger.error(f"  Error: {str(e)}")
                        continue
        
        logger.info(f"\n{'='*80}")
        logger.info(f"TOTAL OFERTAS EXTRAÍDAS: {len(self.todas_ofertas)}")
        logger.info(f"{'='*80}\n")
        
        return self.todas_ofertas


if __name__ == "__main__":
    aggregator = MultiSourceSeleniumAggregator()
    ubicaciones = [
        ('python', 'santiago'),
        ('python', 'chile'),
        ('developer', 'santiago'),
    ]
    
    # Extraer ubicaciones simples
    keywords = list(set([kw for kw, _ in ubicaciones]))
    locations = list(set([loc for _, loc in ubicaciones]))
    
    ofertas = aggregator.scrape_multiples_fuentes(
        keywords=keywords,
        locations=locations
    )
    
    logger.info(f"\n[SUCCESS] Total de ofertas recolectadas: {len(ofertas)}")
