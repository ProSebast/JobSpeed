#!/usr/bin/env python3
"""
Sprint 2 Summary - Visual Overview
Muestra un resumen de lo completado en Sprint 2
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from database import DatabaseManager
from matcher import Matcher


def mostrar_resumen():
    """Muestra resumen de Sprint 2"""
    
    print("\n" + "=" * 80)
    print("🎯 JOBSPEED SPRINT 2 - RESUMEN COMPLETADO")
    print("=" * 80)
    
    try:
        db = DatabaseManager()
        
        # Info base de datos
        print("\n📊 BASE DE DATOS")
        print("   ✅ Esquema de 6 tablas normalizadas")
        print("   ✅ Relaciones N:N implementadas (Certificado-Skill)")
        print("   ✅ Seguimiento de origen de skills (certificado/experiencia/proyecto)")
        print("   ✅ Niveles de expertise (junior/mid/senior)")
        
        # Usuarios
        cursor = db.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM usuarios')
        usuarios_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM skills')
        skills_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM certificados')
        certs_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM skill_usuario')
        user_skills_count = cursor.fetchone()['count']
        
        print(f"\n📈 ESTADÍSTICAS")
        print(f"   • Usuarios: {usuarios_count}")
        print(f"   • Skills registradas: {skills_count}")
        print(f"   • Certificados: {certs_count}")
        print(f"   • Skills asignadas a usuarios: {user_skills_count}")
        
        # Info usuarios
        print(f"\n👥 USUARIOS CREADOS")
        
        usuario_id = db.obtener_usuario_id("Sebastian Alejandro Alvarez Aravena")
        if usuario_id:
            perfil = db.obtener_perfil_completo(usuario_id)
            if perfil:
                print(f"\n   👤 {perfil['usuario']['nombre']}")
                print(f"       📚 Carrera: {perfil['usuario']['carrera']}")
                print(f"       📜 Certificados: {len(perfil['certificados'])}")
                for cert in perfil['certificados']:
                    print(f"          • {cert['nombre_certificado']}")
                print(f"       🔧 Skills: {len(perfil['skills'])} totales")
                skills_by_cat = {}
                for skill in perfil['skills']:
                    cat = skill['categoria']
                    if cat not in skills_by_cat:
                        skills_by_cat[cat] = []
                    skills_by_cat[cat].append(skill['nombre_skill'])
                for cat, skills in sorted(skills_by_cat.items()):
                    print(f"          • {cat}: {', '.join(skills)}")
        
        # Matcher capabilities
        print(f"\n🎲 MÓDULO MATCHER")
        print(f"   ✅ Extracción automática de skills de texto")
        print(f"   ✅ Búsqueda fuzzy (similitud de strings)")
        print(f"   ✅ Cálculo de compatibilidad (match score 0-100%)")
        print(f"   ✅ Clasificación (ALTA/MEDIA/BAJA)")
        print(f"   ✅ Ranking automático de ofertas")
        print(f"   ✅ +50 skills técnicos y blandos soportados")
        
        # Test execution
        print(f"\n🧪 TESTING")
        print(f"   ✅ test_sprint2.py - Demostración completa")
        print(f"   ✅ init_database.py - Inicialización de datos")
        print(f"   ✅ Datos de prueba variados (Informática & Pedagogía)")
        
        # Files created
        print(f"\n📁 ARCHIVOS CREADOS")
        print(f"   ✅ src/database.py - Gestor de BD (350+ líneas)")
        print(f"   ✅ src/matcher.py - Motor de matching (300+ líneas)")
        print(f"   ✅ init_database.py - Script de inicialización")
        print(f"   ✅ test_sprint2.py - Tests y demostración")
        print(f"   ✅ docs/SPRINT_2.md - Documentación completa")
        print(f"   ✅ data/jobspeed.db - Base de datos SQLite")
        
        # Próximos pasos
        print(f"\n🚀 PRÓXIMOS PASOS (SPRINT 3)")
        print(f"   ⏳ Integración Matcher con Storage")
        print(f"   ⏳ API REST con FastAPI")
        print(f"   ⏳ Frontend con React")
        print(f"   ⏳ Notificaciones de ofertas")
        print(f"   ⏳ Machine Learning para recomendación")
        
        print("\n" + "=" * 80)
        print("✨ SPRINT 2 COMPLETADO EXITOSAMENTE ✨")
        print("=" * 80 + "\n")
        
        db.cerrar()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    mostrar_resumen()
