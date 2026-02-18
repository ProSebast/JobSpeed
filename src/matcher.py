# -*- coding: utf-8 -*-
"""
Matcher Module - JobSpeed Sprint 2
Calcula la compatibilidad entre un usuario y una oferta de empleo
basado en skills
"""
import logging
import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Matcher:
    """Calcula compatibilidad entre usuario y oferta de empleo"""
    
    def __init__(self, db_manager):
        """
        Inicializa el Matcher
        
        Args:
            db_manager: Instancia de DatabaseManager
        """
        self.db = db_manager
    
    def extraer_skills_de_texto(self, texto: str) -> List[str]:
        """
        Extrae skills potenciales de un texto (descripción de oferta)
        Busca palabras clave comunes en ofertas de empleo
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Lista de skills encontradas
        """
        if not texto:
            return []
        
        texto_limpio = texto.lower()
        
        # Patrones comunes en ofertas
        patrones = {
            # Lenguajes
            r'\bpython\b': 'python',
            r'\bjava\b(?!script)': 'java',
            r'\bjavascript\b': 'javascript',
            r'\btypescript\b': 'typescript',
            r'\bc\+\+\b': 'c++',
            r'\bc#\b': 'c#',
            r'\bphp\b': 'php',
            r'\bruby\b': 'ruby',
            r'\bgo\b': 'go',
            r'\brust\b': 'rust',
            r'\bswift\b': 'swift',
            
            # BD y Storage
            r'\bsql\b': 'SQL',
            r'\bpostgresql\b': 'postgresql',
            r'\bmysql\b': 'mysql',
            r'\bmongodb\b': 'mongodb',
            r'\bredis\b': 'redis',
            r'\bfirebase\b': 'firebase',
            r'\belasticsearch\b': 'elasticsearch',
            
            # Frontend
            r'\breact\b': 'react',
            r'\bvue\b': 'vue',
            r'\bangular\b': 'angular',
            r'\bhtml\b': 'html',
            r'\bcss\b': 'css',
            r'\bbootstrap\b': 'bootstrap',
            r'\btailwind\b': 'tailwind',
            
            # Backend y Frameworks
            r'\bdjango\b': 'django',
            r'\bflask\b': 'flask',
            r'\bexpressjs\b': 'expressjs',
            r'\bfastapi\b': 'fastapi',
            r'\bspring\b': 'spring',
            r'\blaravel\b': 'laravel',
            r'\brails\b': 'rails',
            
            # DevOps
            r'\bdocker\b': 'docker',
            r'\bkubernetes\b': 'kubernetes',
            r'\bgit\b': 'git',
            r'\bci/cd\b': 'ci/cd',
            r'\baws\b': 'aws',
            r'\bazure\b': 'azure',
            r'\bgcp\b': 'gcp',
            r'\blinux\b': 'linux',
            
            # Arquitectura y patrones
            r'\bmicroservicios\b': 'microservicios',
            r'\bresta?api\b': 'rest api',
            r'\bgraphql\b': 'graphql',
            r'\bpatrones\b': 'patrones',
            r'\bclean code\b': 'clean code',
            r'\bdesign patterns\b': 'patrones',
            
            # Datos y BI
            r'\bdata analysis\b': 'data analysis',
            r'\bdashboards\b': 'dashboards',
            r'\bpower bi\b': 'power bi',
            r'\btableau\b': 'tableau',
            r'\bexcel\b': 'excel',
            r'\bpython\b': 'python',
            r'\br\b': 'r',
            
            # Habilidades blandas
            r'\bcomunicaci[óo]n\b': 'comunicación',
            r'\benglish\b': 'english',
            r'\bingl[ée]s\b': 'inglés',
            r'\bliderazgo\b': 'liderazgo',
            r'\bteamwork\b': 'teamwork',
            r'\bproblem solving\b': 'problem solving',
            r'\bcreativity\b': 'creativity',
        }
        
        skills_encontradas = []
        for patron, skill_name in patrones.items():
            if re.search(patron, texto_limpio):
                skills_encontradas.append(skill_name)
        
        return list(set(skills_encontradas))  # Eliminar duplicados
    
    def normalizar_skill(self, skill: str) -> str:
        """
        Normaliza un nombre de skill para búsqueda en BD
        
        Args:
            skill: Nombre del skill a normalizar
            
        Returns:
            Skill normalizado
        """
        return skill.lower().strip()
    
    def buscar_skill_similar(self, skill_buscado: str, skills_disponibles: List[str]) -> Optional[str]:
        """
        Busca un skill similar si no hay coincidencia exacta
        
        Args:
            skill_buscado: Skill a buscar
            skills_disponibles: Lista de skills disponibles en la BD
            
        Returns:
            Skill más similar o None
        """
        skill_normalizado = self.normalizar_skill(skill_buscado)
        
        # Buscar coincidencia exacta primero
        for skill_disp in skills_disponibles:
            if self.normalizar_skill(skill_disp) == skill_normalizado:
                return skill_disp
        
        # Buscar coincidencia parcial
        mejores_coincidencias = []
        for skill_disp in skills_disponibles:
            ratio = SequenceMatcher(None, skill_normalizado, self.normalizar_skill(skill_disp)).ratio()
            if ratio > 0.6:  # Umbral de similitud
                mejores_coincidencias.append((skill_disp, ratio))
        
        if mejores_coincidencias:
            mejores_coincidencias.sort(key=lambda x: x[1], reverse=True)
            return mejores_coincidencias[0][0]
        
        return None
    
    def calcular_match(self, usuario_id: int, oferta: Dict) -> Dict:
        """
        Calcula la compatibilidad entre un usuario y una oferta
        
        Args:
            usuario_id: ID del usuario
            oferta: Diccionario con datos de la oferta (debe tener 'descripcion' o 'titulo')
            
        Returns:
            Dict con:
                - match_score: Porcentaje de compatibilidad (0-100)
                - match_count: Cantidad de skills encontradas
                - total_skills_oferta: Total de skills en la oferta
                - skills_coincidentes: Lista de skills coincidentes
                - skills_faltantes: Skills de la oferta que no tiene el usuario
                - nivel_recomendacion: ALTA / MEDIA / BAJA
        """
        
        # Obtener skills del usuario
        skills_usuario_data = self.db.obtener_skills_usuario(usuario_id)
        skills_usuario = {s['nombre_skill'].lower() for s in skills_usuario_data}
        
        # Obtener todos los skills disponibles en BD
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT nombre_skill FROM skills')
        skills_disponibles = [row['nombre_skill'] for row in cursor.fetchall()]
        
        # Extraer skills de la oferta
        texto_oferta = f"{oferta.get('titulo', '')} {oferta.get('descripcion', '')}"
        skills_oferta_raw = self.extraer_skills_de_texto(texto_oferta)
        
        # Normalizar y encontrar en BD
        skills_oferta = []
        for skill_raw in skills_oferta_raw:
            skill_encontrado = self.buscar_skill_similar(skill_raw, skills_disponibles)
            if skill_encontrado:
                skills_oferta.append(skill_encontrado.lower())
        
        skills_oferta = list(set(skills_oferta))  # Eliminar duplicados
        
        # Calcular concordancia
        skills_coincidentes = [s for s in skills_oferta if s in skills_usuario]
        skills_faltantes = [s for s in skills_oferta if s not in skills_usuario]
        
        # Calcular score
        if len(skills_oferta) > 0:
            match_score = (len(skills_coincidentes) / len(skills_oferta)) * 100
        else:
            match_score = 0
        
        # Determinar recomendación
        if match_score >= 70:
            nivel_recomendacion = "ALTA ⭐⭐⭐"
        elif match_score >= 50:
            nivel_recomendacion = "MEDIA ⭐⭐"
        else:
            nivel_recomendacion = "BAJA ⭐"
        
        return {
            'match_score': round(match_score, 2),
            'match_count': len(skills_coincidentes),
            'total_skills_oferta': len(skills_oferta),
            'skills_coincidentes': skills_coincidentes,
            'skills_faltantes': skills_faltantes,
            'nivel_recomendacion': nivel_recomendacion,
            'porcentaje': f"{match_score:.1f}%"
        }
    
    def analizar_multiples_ofertas(
        self, usuario_id: int, ofertas: List[Dict]
    ) -> List[Dict]:
        """
        Analiza múltiples ofertas para un usuario y retorna ranking
        
        Args:
            usuario_id: ID del usuario
            ofertas: Lista de diccionarios con datos de ofertas
            
        Returns:
            Lista de ofertas con scores, ordenada por match_score descendente
        """
        resultados = []
        
        for i, oferta in enumerate(ofertas):
            match_data = self.calcular_match(usuario_id, oferta)
            
            resultado = {
                'posicion': i + 1,
                'titulo': oferta.get('titulo', 'Sin título'),
                'empresa': oferta.get('empresa', 'Desconocida'),
                'url': oferta.get('url', ''),
                **match_data
            }
            resultados.append(resultado)
        
        # Ordenar por match_score descendente
        resultados.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Actualizar posiciones
        for i, resultado in enumerate(resultados):
            resultado['ranking'] = i + 1
        
        return resultados
    
    def calcular_score_final(self, usuario_id: int, oferta: Dict) -> Dict:
        """
        Calcula un score final combinando match técnico y proximidad geográfica
        
        Args:
            usuario_id: ID del usuario
            oferta: Diccionario con datos de la oferta
            
        Returns:
            Dict con scores completos y categoría de recomendación
        """
        # Obtener usuario
        usuario = self.db.obtener_usuario(usuario_id)
        
        # Calcular match técnico
        match_data = self.calcular_match(usuario_id, oferta)
        match_score = match_data['match_score']
        
        # Calcular proximidad geográfica (0-100)
        pais_oferta = oferta.get('pais', '').lower().strip()
        ciudad_oferta = oferta.get('ciudad', '').lower().strip()
        pais_usuario = usuario.get('pais', '').lower().strip()
        ciudad_usuario = usuario.get('ciudad', '').lower().strip()
        
        proximidad_score = 0
        if pais_oferta == pais_usuario:
            proximidad_score = 100  # Mismo país
            if ciudad_oferta == ciudad_usuario:
                proximidad_score = 100  # Misma ciudad
        elif pais_oferta == pais_usuario and ciudad_oferta != ciudad_usuario:
            proximidad_score = 80  # Mismo país, diferente ciudad
        else:
            proximidad_score = 30  # País diferente (pero viaje posible)
        
        # Score final (70% técnico, 30% proximidad)
        score_final = (match_score * 0.7) + (proximidad_score * 0.3)
        
        # Determinar categoría de recomendación
        categoria = self._determinar_categoria(match_score, proximidad_score, score_final)
        
        return {
            'match_score': match_score,
            'proximidad_score': proximidad_score,
            'score_final': round(score_final, 2),
            'categoria_recomendacion': categoria,
            'skills_coincidentes': match_data['skills_coincidentes'],
            'skills_faltantes': match_data['skills_faltantes']
        }
    
    def _determinar_categoria(self, match_score: float, proximidad_score: float, score_final: float) -> str:
        """
        Determina la categoría de recomendación basada en scores
        
        Args:
            match_score: Score técnico (0-100)
            proximidad_score: Score de proximidad (0-100)
            score_final: Score combinado (0-100)
            
        Returns:
            Categoría: "Recomendados", "Mejor Match", "Cerca de ti"
        """
        # Priorizar por match técnico primero, luego por ubicación
        if match_score >= 70:
            return "Recomendados"
        elif match_score >= 50 and proximidad_score >= 80:
            return "Cerca de ti"
        elif match_score >= 40:
            return "Mejor Match"
        else:
            return "Otros"
    
    def reporte_match(self, usuario_id: int, oferta: Dict) -> str:
        """
        Genera un reporte formateado del match
        
        Args:
            usuario_id: ID del usuario
            oferta: Diccionario con datos de la oferta
            
        Returns:
            String con reporte formateado
        """
        match_data = self.calcular_match(usuario_id, oferta)
        
        reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║           ANÁLISIS DE COMPATIBILIDAD - JOBSPEED             ║
╚══════════════════════════════════════════════════════════════╝

OFERTA: {oferta.get('titulo', 'Sin título')}
EMPRESA: {oferta.get('empresa', 'Desconocida')}

RESULTADO:
  Score: {match_data['match_score']}%
  Recomendación: {match_data['nivel_recomendacion']}
  Skills Coincidentes: {match_data['match_count']}/{match_data['total_skills_oferta']}

SKILLS COINCIDENTES ({len(match_data['skills_coincidentes'])}):
"""
        for skill in match_data['skills_coincidentes']:
            reporte += f"  [OK] {skill}\n"
        
        if match_data['skills_faltantes']:
            reporte += f"\nSKILLS FALTANTES ({len(match_data['skills_faltantes'])}): \n"
            for skill in match_data['skills_faltantes']:
                reporte += f"  [NO] {skill}\n"
        
        reporte += "\n" + "=" * 62 + "\n"
        
        return reporte
