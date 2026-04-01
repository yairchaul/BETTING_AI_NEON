# -*- coding: utf-8 -*-
"""
DATABASE MANAGER - Gestor central de base de datos
Añadido: métodos para obtener top players por estadística
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Inicializa tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de estadísticas de jugadores (para NBA y MLB)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                equipo TEXT,
                deporte TEXT,
                temporada TEXT,
                puntos REAL,
                triples_por_partido REAL,
                intentos_triples REAL,
                porcentaje_triples REAL,
                hr INTEGER,
                avg REAL,
                rbi INTEGER,
                slugging REAL,
                ultima_actualizacion TEXT
            )
        ''')
        
        # Tabla de equipos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                deporte TEXT,
                ciudad TEXT,
                estadio TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_top_player_stat(self, equipo, stat, limit=1, deporte='nba'):
        """
        Obtiene el/los mejores jugadores de un equipo por una estadística específica.
        
        Args:
            equipo (str): Nombre del equipo
            stat (str): 'three_pm', 'hr', 'points', etc.
            limit (int): Número de jugadores a retornar
            deporte (str): 'nba' o 'mlb'
        
        Returns:
            list: Lista de diccionarios con los mejores jugadores
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if deporte == 'nba':
                if stat == 'three_pm':
                    query = '''
                        SELECT nombre, triples_por_partido, porcentaje_triples, puntos
                        FROM player_stats 
                        WHERE equipo LIKE ? AND deporte = 'nba'
                        ORDER BY triples_por_partido DESC, porcentaje_triples DESC
                        LIMIT ?
                    '''
                elif stat == 'points':
                    query = '''
                        SELECT nombre, puntos, triples_por_partido
                        FROM player_stats 
                        WHERE equipo LIKE ? AND deporte = 'nba'
                        ORDER BY puntos DESC
                        LIMIT ?
                    '''
                else:
                    return []
            
            elif deporte == 'mlb':
                if stat == 'hr':
                    query = '''
                        SELECT nombre, hr, avg, rbi, slugging
                        FROM player_stats 
                        WHERE equipo LIKE ? AND deporte = 'mlb'
                        ORDER BY hr DESC, slugging DESC
                        LIMIT ?
                    '''
                elif stat == 'avg':
                    query = '''
                        SELECT nombre, avg, hr, rbi
                        FROM player_stats 
                        WHERE equipo LIKE ? AND deporte = 'mlb'
                        ORDER BY avg DESC
                        LIMIT ?
                    '''
                else:
                    return []
            else:
                return []
            
            # Buscar equipo parcialmente
            equipo_pattern = f'%{equipo}%'
            cursor = conn.cursor()
            cursor.execute(query, (equipo_pattern, limit))
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                resultados = []
                for row in rows:
                    if deporte == 'nba':
                        resultados.append({
                            'nombre': row[0],
                            'triples_por_partido': row[1],
                            'porcentaje_triples': row[2],
                            'puntos': row[3]
                        })
                    else:
                        resultados.append({
                            'nombre': row[0],
                            'hr': row[1],
                            'avg': row[2],
                            'rbi': row[3],
                            'slugging': row[4]
                        })
                return resultados if limit > 1 else resultados[0]
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo top player para {equipo} ({stat}): {e}")
            return None
    
    def get_team_stats(self, equipo, deporte, limit=5):
        """Obtiene estadísticas históricas de un equipo"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT AVG(puntos_favor) as promedio_favor, 
                       AVG(puntos_contra) as promedio_contra,
                       COUNT(*) as partidos
                FROM historial_equipos 
                WHERE nombre_equipo LIKE ? AND deporte = ?
                ORDER BY fecha DESC
                LIMIT ?
            '''
            cursor = conn.cursor()
            cursor.execute(query, (f'%{equipo}%', deporte, limit))
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                return {
                    'promedio_favor': row[0],
                    'promedio_contra': row[1],
                    'partidos': row[2]
                }
            return {}
        except Exception as e:
            logger.error(f"Error obteniendo stats de {equipo}: {e}")
            return {}
    
    def guardar_player_stats(self, stats_list, deporte):
        """Guarda estadísticas de jugadores en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for stat in stats_list:
                if deporte == 'nba':
                    cursor.execute('''
                        INSERT OR REPLACE INTO player_stats 
                        (nombre, equipo, deporte, temporada, puntos, triples_por_partido, 
                         intentos_triples, porcentaje_triples, ultima_actualizacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stat.get('nombre'),
                        stat.get('equipo'),
                        'nba',
                        stat.get('temporada', '2025'),
                        stat.get('puntos', 0),
                        stat.get('triples_por_partido', 0),
                        stat.get('intentos_triples', 0),
                        stat.get('porcentaje_triples', 0),
                        datetime.now().isoformat()
                    ))
                elif deporte == 'mlb':
                    cursor.execute('''
                        INSERT OR REPLACE INTO player_stats 
                        (nombre, equipo, deporte, temporada, hr, avg, rbi, slugging, ultima_actualizacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stat.get('nombre'),
                        stat.get('equipo'),
                        'mlb',
                        stat.get('temporada', '2025'),
                        stat.get('hr', 0),
                        stat.get('avg', 0),
                        stat.get('rbi', 0),
                        stat.get('slugging', 0),
                        datetime.now().isoformat()
                    ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ {len(stats_list)} jugadores guardados para {deporte}")
        except Exception as e:
            logger.error(f"Error guardando player stats: {e}")

# Instancia global
db = DatabaseManager()
