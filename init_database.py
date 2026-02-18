"""
Script de Inicialización - JobSpeed Sprint 2
Carga datos personales del usuario: Sebastian Alejandro Alvarez Aravena
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from database import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# DATOS PERSONALES DEL USUARIO
USUARIO_DATOS = {
    "nombre": "Sebastian Alejandro Alvarez Aravena",
    "carrera": "Ingeniería en Informática",
    "pais": "Chile",
    "ciudad": "Santiago"
}

SKILLS = [
    ("python", "backend"),
    ("software architecture", "software_engineering"),
    ("software quality", "software_engineering"),
    ("requirements analysis", "analysis"),
    ("data modeling", "databases"),
    ("sql", "databases"),
    ("english", "language"),
    ("business intelligence", "data"),
    ("project management", "management"),
    ("programming fundamentals", "programming"),
]

CERTIFICADOS = [
    "Arquitectura de Software",
    "Inglés Intermedio",
    "Inglés Intermedio Alto",
    "Calidad de Software",
    "Programación de Software",
    "Análisis y Desarrollo de Modelos de Datos",
    "Análisis y Planificación de Requerimientos Informáticos",
    "Inteligencia de Negocios",
    "Gestión de Proyectos Informáticos",
]

# Mapeo: certificado_id -> [skill_ids]
CERTIFICADO_SKILLS = {
    1: [2],           # Arquitectura de Software -> software architecture
    2: [7],           # Inglés Intermedio -> english
    3: [7],           # Inglés Intermedio Alto -> english
    4: [3],           # Calidad de Software -> software quality
    5: [1, 10],       # Programación de Software -> python, programming fundamentals
    6: [5, 6],        # Modelos de Datos -> data modeling, sql
    7: [4],           # Análisis de Requerimientos -> requirements analysis
    8: [8],           # Inteligencia de Negocios -> business intelligence
    9: [9],           # Gestión de Proyectos -> project management
}


def inicializar_base_datos():
    """Inicializa la BD con datos personales del usuario"""
    
    logger.info("=" * 80)
    logger.info("INICIALIZANDO BASE DE DATOS JOBSPEED - SPRINT 2")
    logger.info("=" * 80)
    
    db = DatabaseManager()
    
    # Crear tablas
    db.crear_tablas()
    
    # ========== CREAR USUARIO ==========
    logger.info("\n[1/3] Creando usuario...")
    usuario_id = db.agregar_usuario(
        nombre=USUARIO_DATOS["nombre"],
        carrera=USUARIO_DATOS["carrera"],
        pais=USUARIO_DATOS["pais"],
        ciudad=USUARIO_DATOS["ciudad"]
    )
    
    # ========== CREAR SKILLS ==========
    logger.info(f"\n[2/3] Agregando {len(SKILLS)} skills...")
    skill_ids = {}
    for skill_name, categoria in SKILLS:
        skill_id = db.agregar_skill(skill_name, categoria)
        skill_ids[skill_name] = skill_id
    logger.info(f"✓ {len(SKILLS)} skills creadas")
    
    # ========== CREAR CERTIFICADOS Y RELACIONES ==========
    logger.info(f"\n[3/3] Agregando {len(CERTIFICADOS)} certificados...")
    
    for cert_id, cert_nombre in enumerate(CERTIFICADOS, start=1):
        # Crear certificado (sin institución por ahora)
        db.agregar_certificado(cert_nombre, "Universidad/Instituto")
        
        # Asociar skills al certificado
        if cert_id in CERTIFICADO_SKILLS:
            for skill_id in CERTIFICADO_SKILLS[cert_id]:
                db.asociar_certificado_skill(cert_id, skill_id)
        
        # Asignar certificado al usuario
        db.agregar_certificado_usuario(usuario_id, cert_id)
        
        # Asignar skills al usuario desde el certificado
        if cert_id in CERTIFICADO_SKILLS:
            for skill_id in CERTIFICADO_SKILLS[cert_id]:
                db.agregar_skill_usuario(
                    usuario_id=usuario_id,
                    skill_id=skill_id,
                    nivel=None,
                    años_experiencia=0,
                    origen='certificado'
                )
    
    logger.info(f"✓ {len(CERTIFICADOS)} certificados creados")
    
    # ========== VERIFICACIÓN ==========
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICACIÓN DE DATOS")
    logger.info("=" * 80)
    
    perfil = db.obtener_perfil_completo(usuario_id)
    if perfil:
        logger.info(f"\n👤 USUARIO: {perfil['usuario']['nombre']}")
        logger.info(f"   Carrera: {perfil['usuario']['carrera']}")
        logger.info(f"\n📜 CERTIFICADOS ({len(perfil['certificados'])})")
        for i, cert in enumerate(perfil['certificados'], 1):
            logger.info(f"   {i}. {cert['nombre_certificado']}")
        
        logger.info(f"\n🔧 SKILLS ({len(perfil['skills'])})")
        for i, skill in enumerate(perfil['skills'], 1):
            logger.info(f"   {i}. {skill['nombre_skill']} (categoría: {skill['categoria']})")
    
    logger.info("\n" + "=" * 80)
    logger.info("✓ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
    logger.info("=" * 80)
    
    db.cerrar()



if __name__ == "__main__":
    try:
        inicializar_base_datos()
    except Exception as e:
        logger.error(f"Error durante inicialización: {e}", exc_info=True)
        sys.exit(1)
