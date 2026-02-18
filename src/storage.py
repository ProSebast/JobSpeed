"""
Módulo Storage: Almacena ofertas en CSV
"""
import pandas as pd
import logging
from typing import List, Dict
from pathlib import Path
from config import CSV_PATH, CSV_COLUMNS, LOG_FILE, LOG_FORMAT, LOG_LEVEL

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


class Storage:
    """Sistema de almacenamiento en CSV"""
    
    def __init__(self, csv_path: Path = CSV_PATH):
        self.csv_path = csv_path
        self.df = None
    
    def guardar_ofertas(self, ofertas: List[Dict]) -> bool:
        """
        Guarda ofertas en CSV
        
        Args:
            ofertas: Lista de ofertas a guardar
            
        Returns:
            True si se guardó correctamente
        """
        if not ofertas:
            logger.warning("No hay ofertas para guardar")
            return False
        
        try:
            # Crear DataFrame
            df = pd.DataFrame(ofertas)
            
            # Validar columnas
            df = self._validar_columnas(df)
            
            # Verificar si el archivo existe
            if self.csv_path.exists():
                logger.info("CSV existente. Verificando duplicados...")
                df_existente = pd.read_csv(self.csv_path)
                
                # Eliminar duplicados por URL
                df_existente_urls = set(df_existente["url"].tolist())
                df = df[~df["url"].isin(df_existente_urls)]
                
                if len(df) == 0:
                    logger.info("Todas las ofertas ya existen en el CSV")
                    return True
                
                # Concatenar
                df_final = pd.concat([df_existente, df], ignore_index=True)
            else:
                df_final = df
            
            # Guardar
            df_final.to_csv(self.csv_path, index=False)
            logger.info(f"[OK] Guardadas {len(df)} nuevas ofertas en {self.csv_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando CSV: {str(e)}")
            return False
    
    def _validar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida y asegura que el DataFrame tenga todas las columnas esperadas"""
        for col in CSV_COLUMNS:
            if col not in df.columns:
                logger.warning(f"Columna faltante: {col}. Agregando con valores N/A")
                df[col] = "N/A"
        
        # Reordenar columnas
        df = df[CSV_COLUMNS]
        return df
    
    def leer_ofertas(self, limite: int = None) -> pd.DataFrame:
        """
        Lee ofertas desde CSV
        
        Args:
            limite: Número máximo de registros a leer
            
        Returns:
            DataFrame con ofertas
        """
        try:
            if not self.csv_path.exists():
                logger.warning("CSV no existe aún")
                return pd.DataFrame()
            
            df = pd.read_csv(self.csv_path)
            
            if limite:
                df = df.head(limite)
            
            logger.info(f"Leídas {len(df)} ofertas del CSV")
            return df
            
        except Exception as e:
            logger.error(f"Error leyendo CSV: {str(e)}")
            return pd.DataFrame()
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del CSV"""
        try:
            df = self.leer_ofertas()
            
            if df.empty:
                return {
                    "total_ofertas": 0,
                    "empresas_unicas": 0,
                    "ciudades_unicas": 0
                }
            
            return {
                "total_ofertas": len(df),
                "empresas_unicas": df["empresa"].nunique(),
                "ciudades_unicas": df["ciudad"].nunique() if "ciudad" in df.columns else 0,
                "paises_unicos": df["pais"].nunique() if "pais" in df.columns else 0,
                "salarios_disponibles": (df["salario"] != "No especificado").sum() if "salario" in df.columns else 0
            }
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {str(e)}")
            return {}


if __name__ == "__main__":
    storage = Storage()
    stats = storage.obtener_estadisticas()
    print(f"Estadísticas: {stats}")
