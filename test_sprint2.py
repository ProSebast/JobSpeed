"""
Test Sprint 2 - Demostración de Database y Matcher
Prueba la inicialización de BD y el cálculo de compatibilidad
"""
import sys
import logging
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from database import DatabaseManager
from matcher import Matcher

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def test_matching():
    """Prueba el sistema de matching"""
    
    logger.info("=" * 70)
    logger.info("TEST SPRINT 2 - DATABASE Y MATCHER")
    logger.info("=" * 70)
    
    # Conectar a BD
    db = DatabaseManager()
    
    # Obtener usuario
    usuario_id = db.obtener_usuario_id("Sebastian Alejandro Alvarez Aravena")
    
    if not usuario_id:
        logger.error("❌ No se encontró el usuario. Ejecuta init_database.py primero")
        return
    
    # Crear matcher
    matcher = Matcher(db)
    
    # ========== OFERTAS DE EJEMPLO ==========
    ofertas_ejemplo = [
        {
            "titulo": "Senior Python Developer",
            "empresa": "Tech Corp",
            "descripcion": "Buscamos un Senior Python Developer con experiencia en microservicios, "
                          "Docker y Kubernetes. Conocimiento en SQL y PostgreSQL es esencial. "
                          "Must have: Clean Code, Design Patterns, REST API, Git, Linux.",
            "url": "https://ejemplo.com/oferta1"
        },
        {
            "titulo": "Full Stack JavaScript Developer",
            "empresa": "Web Solutions Inc",
            "descripcion": "Necesitamos Full Stack con JavaScript/TypeScript, React, Node.js, "
                          "Express, MongoDB y Redis. Plus: Docker, AWS, CI/CD, Testing.",
            "url": "https://ejemplo.com/oferta2"
        },
        {
            "titulo": "Data Analyst",
            "empresa": "Analytics Plus",
            "descripcion": "Analista de datos con experiencia en SQL, Excel, Power BI, Tableau. "
                          "Conocimiento en Python para data analysis. Comunicación excelente.",
            "url": "https://ejemplo.com/oferta3"
        },
        {
            "titulo": "Docente de Educación Digital",
            "empresa": "Instituto Educativo",
            "descripcion": "Buscamos docente con experiencia en e-learning, plataformas educativas, "
                          "comunicación efectiva, liderazgo y diseño instruccional. "
                          "Español e inglés.",
            "url": "https://ejemplo.com/oferta4"
        },
        {
            "titulo": "Capacitador Corporativo",
            "empresa": "Training Solutions",
            "descripcion": "Capacitador con habilidades de comunicación, presentaciones, "
                          "liderazgo, trabajo en equipo y creative thinking. "
                          "Experiencia en e-learning deseable.",
            "url": "https://ejemplo.com/oferta5"
        }
    ]
    
    # ========== ANÁLISIS USUARIO ==========
    logger.info("\n" + "=" * 70)
    logger.info("ANÁLISIS: Sebastian Alejandro Alvarez Aravena (Ingeniería en Informática)")
    logger.info("=" * 70)
    
    resultados = matcher.analizar_multiples_ofertas(usuario_id, ofertas_ejemplo)
    
    for resultado in resultados:
        logger.info(f"\n[#{resultado['ranking']}] {resultado['titulo']} - {resultado['empresa']}")
        logger.info(f"    Match: {resultado['porcentaje']} → {resultado['nivel_recomendacion']}")
        logger.info(f"    Skills: {resultado['match_count']}/{resultado['total_skills_oferta']} coincidencias")
        if resultado['skills_coincidentes']:
            skills_str = ', '.join(resultado['skills_coincidentes'][:3])
            if len(resultado['skills_coincidentes']) > 3:
                skills_str += f" +{len(resultado['skills_coincidentes']) - 3} más"
            logger.info(f"    ✓ Coincidencias: {skills_str}")
        if resultado['skills_faltantes']:
            skills_faltantes_str = ', '.join(resultado['skills_faltantes'][:2])
            if len(resultado['skills_faltantes']) > 2:
                skills_faltantes_str += f" +{len(resultado['skills_faltantes']) - 2} más"
            logger.info(f"    ✗ Faltantes: {skills_faltantes_str}")
    
    # Reporte detallado de la mejor oferta
    if resultados:
        mejor_oferta = resultados[0]
        oferta_dict = next(o for o in ofertas_ejemplo if o['titulo'] == mejor_oferta['titulo'])
        logger.info("\n" + matcher.reporte_match(usuario_id, oferta_dict))
    
    # ========== CONCLUSIÓN ==========
    logger.info("\n" + "=" * 70)
    logger.info("✓ TEST COMPLETADO EXITOSAMENTE")
    logger.info("=" * 70)
    
    db.cerrar()


if __name__ == "__main__":
    try:
        test_matching()
    except Exception as e:
        logger.error(f"Error durante test: {e}", exc_info=True)
        sys.exit(1)
