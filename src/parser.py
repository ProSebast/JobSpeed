"""
Módulo Parser: Extrae y normaliza datos de ofertas
"""
import re
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from datetime import datetime
from config import SCRAPE_CONFIG, LOG_FILE, LOG_FORMAT, LOG_LEVEL

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


class Parser:
    """Sistema de parseo y normalización de ofertas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(SCRAPE_CONFIG["headers"])
        self.timeout = SCRAPE_CONFIG["timeout"]
        self.ofertas_procesadas = []
    
    def procesar_ofertas(self, ofertas_raw: List[Dict]) -> List[Dict]:
        """
        Procesa lista de ofertas crudas y extrae datos relevantes
        Filtra ofertas incompletas
        
        Args:
            ofertas_raw: Lista de ofertas sin procesar
            
        Returns:
            Lista de ofertas normalizadas (sin incompletas)
        """
        logger.info(f"Iniciando procesamiento de {len(ofertas_raw)} ofertas")
        
        for idx, oferta in enumerate(ofertas_raw, 1):
            logger.debug(f"Procesando oferta {idx}/{len(ofertas_raw)}")
            
            try:
                oferta_procesada = self._extraer_detalles(oferta)
                
                # Filtrar ofertas incompletas
                if oferta_procesada and self._es_oferta_completa(oferta_procesada):
                    self.ofertas_procesadas.append(oferta_procesada)
                elif oferta_procesada:
                    logger.warning(f"Oferta incompleta descartada: {oferta.get('titulo')}")
                    
            except Exception as e:
                logger.warning(f"Error procesando oferta {oferta.get('url')}: {str(e)}")
                continue
        
        logger.info(f"[OK] Procesadas {len(self.ofertas_procesadas)} ofertas (incompletas eliminadas)")
        return self.ofertas_procesadas
    
    def _es_oferta_completa(self, oferta: Dict) -> bool:
        """Verifica si una oferta tiene datos suficientes"""
        # Campos minimos requeridos
        campos_requeridos = ['titulo', 'url']
        
        for campo in campos_requeridos:
            if campo not in oferta or oferta[campo] in ["N/A", "No disponible", "", None]:
                return False
        
        # Aceptar si tiene al menos título y URL, aunque otros campos sean N/A
        return True
    
    def _extraer_detalles(self, oferta: Dict) -> Dict:
        """Extrae detalles de una oferta individual"""
        try:
            url = oferta.get("url", "")
            
            # Intentar obtener la página
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                contenido_extraido = True
            except:
                # Si no se puede obtener la página, usar datos básicos
                logger.warning(f"No se pudo acceder a {url}, usando datos básicos")
                soup = None
                contenido_extraido = False
            
            # Extraer campos
            titulo = oferta.get("titulo", "N/A")
            
            # Empresa
            empresa = "N/A"
            if contenido_extraido:
                empresa_elem = soup.find("span", {"data-testid": "inlineHeader-companyName"})
                if not empresa_elem:
                    empresa_elem = soup.find("a", {"data-testid": "companyName"})
                if not empresa_elem:
                    empresa_elem = soup.find("div", class_="css-16my886")
                if empresa_elem:
                    empresa = empresa_elem.get_text(strip=True)
            
            # Descripción
            descripcion = "No disponible"
            if contenido_extraido:
                descripcion_elem = soup.find("div", {"id": "jobDescriptionText"})
                if not descripcion_elem:
                    descripcion_elem = soup.find("div", class_="show-more-less-html__markup")
                if descripcion_elem:
                    descripcion = descripcion_elem.get_text(strip=True)[:500]
            
            # Ubicación
            ubicacion = "No especificada"
            if contenido_extraido:
                ubicacion = self._extraer_ubicacion(soup)
            
            # Salario
            salario = "No especificado"
            if contenido_extraido:
                salario = self._extraer_salario(soup, descripcion)
            
            # Extraer país y ciudad desde ubicación
            pais = "N/A"
            ciudad = "N/A"
            if ubicacion and ubicacion != "No especificada":
                # Si location es "Ciudad, País" o solo "País"
                partes = [p.strip() for p in ubicacion.split(",")]
                if len(partes) == 2:
                    ciudad = partes[0]
                    pais = partes[1]
                elif len(partes) == 1:
                    # Asumir que es país o ciudad
                    pais = partes[0]
            
            # Normalizar
            return {
                "id": oferta.get("id"),
                "titulo": self._normalizar_texto(titulo),
                "empresa": self._normalizar_texto(empresa),
                "pais": self._normalizar_texto(pais),
                "ciudad": self._normalizar_texto(ciudad),
                "ubicacion": self._normalizar_texto(ubicacion),  # Mantener para compatibilidad
                "salario": salario,
                "descripcion": self._normalizar_texto(descripcion),
                "url": url,
                "source": oferta.get("source", "N/A"),  # IMPORTANTE: Preservar source
                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.debug(f"Error extrayendo detalles de {oferta.get('url')}: {str(e)}")
            # Retornar con datos mínimos en caso de error
            return {
                "id": oferta.get("id"),
                "titulo": oferta.get("titulo", "N/A"),
                "empresa": "N/A",
                "pais": "N/A",
                "ciudad": "N/A",
                "ubicacion": "N/A",
                "salario": "N/A",
                "descripcion": "N/A",
                "url": oferta.get("url", ""),
                "source": oferta.get("source", "N/A"),  # IMPORTANTE: Preservar source
                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _extraer_ubicacion(self, soup: BeautifulSoup) -> str:
        """Extrae ubicación de la oferta"""
        try:
            # Intentar múltiples selectores para ubicación
            ubicacion_elem = soup.find("span", {"data-testid": "inlineHeader-companyLocation"})
            if ubicacion_elem:
                return ubicacion_elem.get_text(strip=True)
            
            # Alternativa 2
            ubicacion_elem = soup.find("div", class_="css-qvq2eb")
            if ubicacion_elem:
                return ubicacion_elem.get_text(strip=True)
            
            # Alternativa 3 - Buscar por clase genérica
            ubicacion_elem = soup.find("span", class_="js-match-insights-provider-tooltiptext")
            if ubicacion_elem:
                return ubicacion_elem.get_text(strip=True)
            
            return "No especificada"
        except:
            return "No especificada"
    
    def _extraer_salario(self, soup: BeautifulSoup, descripcion: str) -> str:
        """Extrae información de salario usando regex"""
        # Patrones para salarios
        patrones_salario = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',  # $X - $Y
            r'\$[\d,]+k\s*-\s*\$[\d,]+k',  # $Xk - $Yk
            r'Salario:\s*\$[\d,]+',  # Salario: $X
        ]
        
        texto_busqueda = soup.get_text() + " " + descripcion
        
        for patron in patrones_salario:
            match = re.search(patron, texto_busqueda, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "No especificado"
    
    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto: limpia espacios y caracteres especiales"""
        if not texto or texto == "N/A":
            return "N/A"
        
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        # Eliminar saltos de línea
        texto = texto.replace('\n', ' ').replace('\r', ' ')
        # Limpiar espacios al inicio y final
        texto = texto.strip()
        
        return texto if texto else "N/A"
    
    def obtener_ofertas_procesadas(self) -> List[Dict]:
        """Retorna ofertas procesadas"""
        return self.ofertas_procesadas


if __name__ == "__main__":
    from collector import Collector
    
    collector = Collector()
    ofertas_raw = collector.buscar_ofertas("python", cantidad=10)
    
    parser = Parser()
    ofertas_procesadas = parser.procesar_ofertas(ofertas_raw)
    
    print(f"Total procesadas: {len(ofertas_procesadas)}")
    if ofertas_procesadas:
        print(f"Primer registro: {ofertas_procesadas[0]}")
