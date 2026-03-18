"""
UFC DATA AGGREGATOR - PRIORIZA datos de ESPN, enriquece con dataset
"""
import streamlit as st
from ufc_dataset_integrator import UFCDatasetIntegrator

class UFCDataAggregator:
    def __init__(self):
        self.dataset = UFCDatasetIntegrator()
        self.cache = {}
        print("✅ UFC Data Aggregator inicializado")
    
    def _parse_record(self, record_str):
        """Parsea string de récord (ej: '11-5-0') a dict"""
        try:
            parts = record_str.split('-')
            if len(parts) >= 3:
                return {
                    'wins': int(parts[0]),
                    'losses': int(parts[1]),
                    'draws': int(parts[2])
                }
            elif len(parts) == 2:
                return {
                    'wins': int(parts[0]),
                    'losses': int(parts[1]),
                    'draws': 0
                }
        except:
            pass
        return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def get_fighter_data(self, fighter_name, espn_record=None):
        """
        Obtiene datos del peleador:
        - Usa récord de ESPN si está disponible
        - Enriquece con datos físicos del dataset
        """
        if fighter_name in self.cache:
            return self.cache[fighter_name]
        
        # Obtener datos del dataset (altura, peso, estadísticas)
        stats = self.dataset.get_fighter_stats(fighter_name)
        
        # Crear datos base
        data = {
            'nombre': fighter_name,
            'record': espn_record if espn_record else '0-0-0',
            'altura': stats.get('altura', 'N/A') if stats else 'N/A',
            'peso': stats.get('peso', 'N/A') if stats else 'N/A',
            'alcance': stats.get('alcance', 'N/A') if stats else 'N/A',
            'postura': stats.get('postura', 'Desconocida') if stats else 'Desconocida',
            'record_dict': self._parse_record(espn_record if espn_record else '0-0-0')
        }
        
        # Añadir estadísticas de carrera si existen
        if stats:
            data['estadisticas_carrera'] = {
                'sig_strikes_landed_per_min': stats.get('splm', 0),
                'sig_strike_accuracy': stats.get('str_acc', 0),
                'td_avg_per_15min': stats.get('td_avg', 0),
                'td_accuracy': stats.get('td_acc', 0),
                'td_defense': stats.get('td_def', 0),
                'sub_avg_per_15min': stats.get('sub_avg', 0)
            }
        
        # Obtener historial y estadísticas avanzadas
        historial = self.dataset.get_fight_history(fighter_name)
        if historial:
            data['historial'] = historial
        
        win_stats = self.dataset.get_win_rate_stats(fighter_name)
        if win_stats:
            data['win_stats'] = win_stats
        
        adv_stats = self.dataset.get_fighter_advanced_stats(fighter_name)
        if adv_stats:
            data['advanced_stats'] = adv_stats
        
        self.cache[fighter_name] = data
        return data
    
    def get_fight_data(self, fighter1_name, fighter2_name, event_data=None):
        """
        Obtiene datos de ambos peleadores
        - Usa récords de ESPN del evento
        - Enriquece con datos del dataset
        """
        # Buscar récords de ESPN en el evento
        espn_record1 = None
        espn_record2 = None
        
        if event_data:
            for fight in event_data:
                p1 = fight.get('peleador1', {})
                p2 = fight.get('peleador2', {})
                
                if fighter1_name in p1.get('nombre', '') or p1.get('nombre', '') in fighter1_name:
                    espn_record1 = p1.get('record')
                if fighter2_name in p2.get('nombre', '') or p2.get('nombre', '') in fighter2_name:
                    espn_record2 = p2.get('record')
        
        # Obtener datos combinados
        p1_data = self.get_fighter_data(fighter1_name, espn_record1)
        p2_data = self.get_fighter_data(fighter2_name, espn_record2)
        
        return {
            'peleador1': p1_data,
            'peleador2': p2_data,
            'real': True
        }
