# -*- coding: utf-8 -*-
"""
ESPN UFC - Módulo exclusivo para UFC
Lee desde SQLite (datos ya sincronizados)
"""
import sqlite3
import json

class ESPN_UFC:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
    
    def get_events(self):
        """Obtiene eventos UFC desde la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT nombre, fecha, cartelera FROM eventos_ufc ORDER BY fecha DESC LIMIT 1")
            evento = c.fetchone()
            conn.close()
            
            combates = []
            if evento and evento[2]:
                cartelera = json.loads(evento[2])
                for pelea in cartelera:
                    combates.append({
                        'peleador1': {'nombre': pelea.get('peleador1', '')},
                        'peleador2': {'nombre': pelea.get('peleador2', '')},
                        'categoria': pelea.get('peso', 'Peso Pactado'),
                        'evento': evento[0],
                        'fecha': evento[1]
                    })
            return combates
        except Exception as e:
            print(f"Error UFC: {e}")
            return []
