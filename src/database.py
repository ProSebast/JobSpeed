# -*- coding: utf-8 -*-
"""
Database Manager - JobSpeed Sprint 2
Gestiona las tablas de usuarios, skills, certificados y relaciones
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de base de datos SQLite para JobSpeed"""
    
    def __init__(self, db_path: str = "data/jobspeed.db"):
        """Inicializa la conexión a la BD"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = None
        self.conectar()
    
    def conectar(self):
        """Establece conexión a la BD"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Para acceder como diccionarios
            logger.info(f"Conectado a BD: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error conectando a BD: {e}")
            raise
    
    def crear_tablas(self):
        """Crea todas las tablas necesarias"""
        try:
            cursor = self.conn.cursor()
            
            # TABLA USUARIOS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    carrera TEXT NOT NULL,
                    pais TEXT,
                    ciudad TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("[OK] Tabla USUARIOS creada")
            
            # TABLA SKILLS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_skill TEXT NOT NULL UNIQUE,
                    categoria TEXT NOT NULL
                )
            ''')
            logger.info("[OK] Tabla SKILLS creada")
            
            # TABLA CERTIFICADOS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_certificado TEXT NOT NULL,
                    institucion TEXT NOT NULL,
                    UNIQUE(nombre_certificado, institucion)
                )
            ''')
            logger.info("[OK] Tabla CERTIFICADOS creada")
            
            # TABLA CERTIFICADO_SKILL (relación N:N)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificado_skill (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    certificado_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    FOREIGN KEY (certificado_id) REFERENCES certificados(id),
                    FOREIGN KEY (skill_id) REFERENCES skills(id),
                    UNIQUE(certificado_id, skill_id)
                )
            ''')
            logger.info("[OK] Tabla CERTIFICADO_SKILL creada")
            
            # TABLA CERTIFICADOS_USUARIO
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificados_usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    certificado_id INTEGER NOT NULL,
                    fecha_obtencion DATE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (certificado_id) REFERENCES certificados(id),
                    UNIQUE(usuario_id, certificado_id)
                )
            ''')
            logger.info("[OK] Tabla CERTIFICADOS_USUARIO creada")
            
            # TABLA SKILL_USUARIO
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skill_usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    nivel TEXT CHECK(nivel IN ('junior', 'mid', 'senior')),
                    años_experiencia INTEGER DEFAULT 0,
                    origen TEXT CHECK(origen IN ('certificado', 'experiencia', 'proyecto')),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (skill_id) REFERENCES skills(id),
                    UNIQUE(usuario_id, skill_id)
                )
            ''')
            logger.info("[OK] Tabla SKILL_USUARIO creada")
            
            self.conn.commit()
            logger.info("=" * 70)
            logger.info("Todas las tablas creadas exitosamente")
            logger.info("=" * 70)
            
        except sqlite3.Error as e:
            logger.error(f"Error creando tablas: {e}")
            self.conn.rollback()
            raise
    
    # ========== OPERACIONES USUARIO ==========
    def agregar_usuario(self, nombre: str, carrera: str, pais: str = None, ciudad: str = None) -> int:
        """Agrega un nuevo usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO usuarios (nombre, carrera, pais, ciudad) VALUES (?, ?, ?, ?)',
                (nombre, carrera, pais, ciudad)
            )
            self.conn.commit()
            usuario_id = cursor.lastrowid
            logger.info(f"Usuario creado: {nombre} (ID: {usuario_id})")
            return usuario_id
        except sqlite3.IntegrityError:
            logger.warning(f"Usuario {nombre} ya existe")
            return self.obtener_usuario_id(nombre)
        except sqlite3.Error as e:
            logger.error(f"Error agregando usuario: {e}")
            raise
    
    def obtener_usuario_id(self, nombre: str) -> Optional[int]:
        """Obtiene ID de usuario por nombre"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM usuarios WHERE nombre = ?', (nombre,))
            resultado = cursor.fetchone()
            return resultado['id'] if resultado else None
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    def obtener_usuario(self, usuario_id: int) -> Optional[Dict]:
        """Obtiene información completa de un usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
            resultado = cursor.fetchone()
            return dict(resultado) if resultado else None
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    # ========== OPERACIONES SKILLS ==========
    def agregar_skill(self, nombre_skill: str, categoria: str) -> int:
        """Agrega una nueva skill"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO skills (nombre_skill, categoria) VALUES (?, ?)',
                (nombre_skill, categoria)
            )
            self.conn.commit()
            skill_id = cursor.lastrowid
            logger.debug(f"Skill creada: {nombre_skill} (ID: {skill_id})")
            return skill_id
        except sqlite3.IntegrityError:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM skills WHERE nombre_skill = ?', (nombre_skill,))
            resultado = cursor.fetchone()
            return resultado['id'] if resultado else None
        except sqlite3.Error as e:
            logger.error(f"Error agregando skill: {e}")
            raise
    
    def obtener_skill_id(self, nombre_skill: str) -> Optional[int]:
        """Obtiene ID de skill por nombre"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM skills WHERE nombre_skill = ?', (nombre_skill,))
            resultado = cursor.fetchone()
            return resultado['id'] if resultado else None
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo skill: {e}")
            return None
    
    # ========== OPERACIONES CERTIFICADOS ==========
    def agregar_certificado(self, nombre_certificado: str, institucion: str) -> int:
        """Agrega un nuevo certificado"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO certificados (nombre_certificado, institucion) VALUES (?, ?)',
                (nombre_certificado, institucion)
            )
            self.conn.commit()
            cert_id = cursor.lastrowid
            logger.debug(f"Certificado creado: {nombre_certificado} (ID: {cert_id})")
            return cert_id
        except sqlite3.IntegrityError:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id FROM certificados WHERE nombre_certificado = ? AND institucion = ?',
                (nombre_certificado, institucion)
            )
            resultado = cursor.fetchone()
            return resultado['id'] if resultado else None
        except sqlite3.Error as e:
            logger.error(f"Error agregando certificado: {e}")
            raise
    
    # ========== OPERACIONES CERTIFICADO-SKILL ==========
    def asociar_certificado_skill(self, certificado_id: int, skill_id: int):
        """Asocia una skill a un certificado"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO certificado_skill (certificado_id, skill_id) VALUES (?, ?)',
                (certificado_id, skill_id)
            )
            self.conn.commit()
            logger.debug(f"Skill {skill_id} asociada a certificado {certificado_id}")
        except sqlite3.IntegrityError:
            logger.debug("Asociación ya existe")
        except sqlite3.Error as e:
            logger.error(f"Error asociando skill a certificado: {e}")
            raise
    
    # ========== OPERACIONES CERTIFICADOS_USUARIO ==========
    def agregar_certificado_usuario(
        self, usuario_id: int, certificado_id: int, fecha_obtencion: Optional[str] = None
    ) -> int:
        """Agrega un certificado obtenido por un usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''INSERT INTO certificados_usuario (usuario_id, certificado_id, fecha_obtencion)
                   VALUES (?, ?, ?)''',
                (usuario_id, certificado_id, fecha_obtencion or datetime.now().strftime('%Y-%m-%d'))
            )
            self.conn.commit()
            cert_user_id = cursor.lastrowid
            logger.debug(f"Certificado {certificado_id} asignado a usuario {usuario_id}")
            return cert_user_id
        except sqlite3.IntegrityError:
            logger.debug(f"Usuario {usuario_id} ya tiene certificado {certificado_id}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error agregando certificado a usuario: {e}")
            raise
    
    # ========== OPERACIONES SKILL_USUARIO ==========
    def agregar_skill_usuario(
        self,
        usuario_id: int,
        skill_id: int,
        nivel: str = 'mid',
        años_experiencia: int = 0,
        origen: str = 'certificado'
    ) -> int:
        """Agrega una skill a un usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''INSERT INTO skill_usuario 
                   (usuario_id, skill_id, nivel, años_experiencia, origen)
                   VALUES (?, ?, ?, ?, ?)''',
                (usuario_id, skill_id, nivel, años_experiencia, origen)
            )
            self.conn.commit()
            skill_user_id = cursor.lastrowid
            logger.debug(f"Skill {skill_id} asignada a usuario {usuario_id}")
            return skill_user_id
        except sqlite3.IntegrityError:
            logger.debug(f"Usuario {usuario_id} ya tiene skill {skill_id}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error agregando skill a usuario: {e}")
            raise
    
    def obtener_skills_usuario(self, usuario_id: int) -> List[Dict]:
        """Obtiene todas las skills de un usuario con detalles"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''SELECT s.id, s.nombre_skill, s.categoria, su.nivel, 
                          su.años_experiencia, su.origen
                   FROM skill_usuario su
                   JOIN skills s ON su.skill_id = s.id
                   WHERE su.usuario_id = ?''',
                (usuario_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo skills del usuario: {e}")
            return []
    
    def obtener_certificados_usuario(self, usuario_id: int) -> List[Dict]:
        """Obtiene todos los certificados de un usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''SELECT c.id, c.nombre_certificado, c.institucion, cu.fecha_obtencion
                   FROM certificados_usuario cu
                   JOIN certificados c ON cu.certificado_id = c.id
                   WHERE cu.usuario_id = ?''',
                (usuario_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo certificados del usuario: {e}")
            return []
    
    # ========== CONSULTAS AVANZADAS ==========
    def obtener_skills_por_certificado(self, certificado_id: int) -> List[str]:
        """Obtiene todas las skills asociadas a un certificado"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''SELECT s.nombre_skill FROM skills s
                   JOIN certificado_skill cs ON s.id = cs.skill_id
                   WHERE cs.certificado_id = ?''',
                (certificado_id,)
            )
            return [row['nombre_skill'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo skills del certificado: {e}")
            return []
    
    def obtener_perfil_completo(self, usuario_id: int) -> Dict:
        """Obtiene el perfil completo de un usuario (usuario + skills + certificados)"""
        try:
            usuario = self.obtener_usuario(usuario_id)
            if not usuario:
                return None
            
            return {
                'usuario': usuario,
                'skills': self.obtener_skills_usuario(usuario_id),
                'certificados': self.obtener_certificados_usuario(usuario_id)
            }
        except Exception as e:
            logger.error(f"Error obteniendo perfil completo: {e}")
            return None
    
    def cerrar(self):
        """Cierra la conexión a la BD"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión a BD cerrada")
    
    def limpiar_base_datos(self):
        """Elimina todos los datos (útil para testing)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM skill_usuario')
            cursor.execute('DELETE FROM certificados_usuario')
            cursor.execute('DELETE FROM certificado_skill')
            cursor.execute('DELETE FROM usuarios')
            cursor.execute('DELETE FROM certificados')
            cursor.execute('DELETE FROM skills')
            self.conn.commit()
            logger.warning("Base de datos limpiada")
        except sqlite3.Error as e:
            logger.error(f"Error limpiando BD: {e}")
            raise
