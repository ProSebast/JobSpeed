#!/usr/bin/env python3
# Verificar Datos
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
#!/usr/bin/env python3
"""
Verificación de Datos Personales - JobSpeed Sprint 2
Muestra los datos almacenados en format de tablas para verificación
"""
import sys
from pathlib import Path
import sqlite3

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from database import DatabaseManager


def mostrar_datos():
    """Muestra todos los datos en formato de tabla"""
    
    db = DatabaseManager()
    
    print("\n" + "=" * 90)
    print("VERIFICACIÓN DE DATOS PERSONALES - JOBSPEED SPRINT 2")
    print("=" * 90)
    
    # ========== USUARIOS ==========
    print("\n" + "=" * 90)
    print("USUARIOS")
    print("=" * 90)
    
    cursor = db.conn.cursor()
    cursor.execute('''SELECT id, nombre, carrera, fecha_creacion FROM usuarios''')
    
    print(f"{'id':<5} {'nombre':<45} {'carrera':<30} {'fecha_creacion':<15}")
    print("-" * 90)
    
    for row in cursor.fetchall():
        print(f"{row['id']:<5} {row['nombre']:<45} {row['carrera']:<30} {row['fecha_creacion']:<15}")
    
    # ========== SKILLS ==========
    print("\n" + "=" * 90)
    print("SKILLS")
    print("=" * 90)
    
    cursor.execute('''SELECT id, nombre_skill, categoria FROM skills ORDER BY id''')
    
    print(f"{'id':<5} {'nombre_skill':<30} {'categoria':<30}")
    print("-" * 90)
    
    for row in cursor.fetchall():
        print(f"{row['id']:<5} {row['nombre_skill']:<30} {row['categoria']:<30}")
    
    # ========== CERTIFICADOS ==========
    print("\n" + "=" * 90)
    print("CERTIFICADOS")
    print("=" * 90)
    
    cursor.execute('''SELECT id, nombre_certificado FROM certificados ORDER BY id''')
    
    print(f"{'id':<5} {'nombre_certificado':<60}")
    print("-" * 90)
    
    for row in cursor.fetchall():
        print(f"{row['id']:<5} {row['nombre_certificado']:<60}")
    
    # ========== CERTIFICADO_SKILL ==========
    print("\n" + "=" * 90)
    print("CERTIFICADO_SKILL")
    print("=" * 90)
    
    cursor.execute('''SELECT certificado_id, skill_id FROM certificado_skill ORDER BY certificado_id, skill_id''')
    
    print(f"{'certificado_id':<15} {'skill_id':<15}")
    print("-" * 90)
    
    for row in cursor.fetchall():
        print(f"{row['certificado_id']:<15} {row['skill_id']:<15}")
    
    # ========== CERTIFICADOS_USUARIO ==========
    print("\n" + "=" * 90)
    print("CERTIFICADOS_USUARIO")
    print("=" * 90)
    
    cursor.execute('''SELECT id, usuario_id, certificado_id, fecha_obtencion FROM certificados_usuario ORDER BY id''')
    
    print(f"{'id':<5} {'usuario_id':<12} {'certificado_id':<17} {'fecha_obtencion':<20}")
    print("-" * 90)
    
    for row in cursor.fetchall():
        fecha = row['fecha_obtencion'] if row['fecha_obtencion'] else 'NULL'
        print(f"{row['id']:<5} {row['usuario_id']:<12} {row['certificado_id']:<17} {fecha:<20}")
    
    # ========== SKILL_USUARIO ==========
    print("\n" + "=" * 90)
    print("SKILL_USUARIO")
    print("=" * 90)
    
    cursor.execute('''SELECT id, usuario_id, skill_id, nivel, años_experiencia, origen 
                      FROM skill_usuario ORDER BY id''')
    
    print(f"{'id':<5} {'usuario_id':<12} {'skill_id':<10} {'nivel':<8} {'años_exp':<10} {'origen':<15}")
    print("-" * 90)
    
    for row in cursor.fetchall():
        nivel = row['nivel'] if row['nivel'] else 'NULL'
        print(f"{row['id']:<5} {row['usuario_id']:<12} {row['skill_id']:<10} {nivel:<8} {row['años_experiencia']:<10} {row['origen']:<15}")
    
    print("\n" + "=" * 90)
    print("\n✅ Verificación completada\n")
    
    db.cerrar()


if __name__ == "__main__":
    try:
        mostrar_datos()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
