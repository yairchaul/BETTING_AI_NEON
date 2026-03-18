"""
UFC DATASET INTEGRATOR - Integra Kaggle + UFC.com
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from ufc_com_scraper import UFCComScraper

class UFCDatasetIntegrator:
    """
    Integra datasets de Kaggle y UFC.com
    """
    
    def __init__(self, data_dir="ufc_data"):
        self.data_dir = Path(data_dir)
        self.dfs = {}
        self.ufc_com = UFCComScraper()
        self.cargar_datasets()
    
    def cargar_datasets(self):
        """Carga todos los archivos CSV disponibles"""
        archivos = list(self.data_dir.glob("*.csv"))
        
        for archivo in archivos:
            nombre = archivo.stem
            try:
                df = pd.read_csv(archivo)
                self.dfs[nombre] = df
                print(f"✅ {nombre}.csv: {len(df)} registros")
            except Exception as e:
                print(f"Error cargando {nombre}: {e}")
    
    def get_fighter_stats(self, fighter_name):
        """
        Obtiene estadísticas de un peleador (Kaggle + UFC.com)
        """
        # 1. Intentar Kaggle
        if 'fighter_details' in self.dfs:
            df = self.dfs['fighter_details']
            mascara = df['name'].str.contains(fighter_name, case=False, na=False)
            resultados = df[mascara]
            
            if len(resultados) > 0:
                fighter = resultados.iloc[0].to_dict()
                
                altura_cm = self._parse_height(fighter.get('height', ''))
                peso_kg = self._parse_weight(fighter.get('weight', ''))
                
                return {
                    'nombre': fighter.get('name', fighter_name),
                    'record': f"{fighter.get('wins', 0)}-{fighter.get('losses', 0)}-{fighter.get('draws', 0)}",
                    'altura': altura_cm,
                    'peso': peso_kg,
                    'alcance': fighter.get('reach', 'N/A'),
                    'postura': fighter.get('stance', 'Desconocida'),
                    'splm': fighter.get('splm', 0),
                    'str_acc': fighter.get('str_acc', 0),
                    'sapm': fighter.get('sapm', 0),
                    'str_def': fighter.get('str_def', 0),
                    'td_avg': fighter.get('td_avg', 0),
                    'td_acc': fighter.get('td_avg_acc', 0),
                    'td_def': fighter.get('td_def', 0),
                    'sub_avg': fighter.get('sub_avg', 0),
                    'fuente': 'Kaggle'
                }
        
        # 2. Intentar UFC.com
        ufc_data = self.ufc_com.get_fighter_data(fighter_name)
        if ufc_data:
            return {
                'nombre': fighter_name,
                'record': '0-0-0',
                'altura': ufc_data.get('altura', 'N/A'),
                'peso': ufc_data.get('peso', 'N/A'),
                'alcance': ufc_data.get('alcance', 'N/A'),
                'postura': ufc_data.get('postura', 'Desconocida'),
                'splm': 0,
                'str_acc': 0,
                'sapm': 0,
                'str_def': 0,
                'td_avg': 0,
                'td_acc': 0,
                'td_def': 0,
                'sub_avg': 0,
                'fuente': 'UFC.com'
            }
        
        return None
    
    def _parse_height(self, height_str):
        """Convierte altura a formato legible"""
        try:
            if pd.isna(height_str) or height_str == '':
                return 'N/A'
            
            if isinstance(height_str, (int, float)):
                return f"{height_str:.1f} cm"
            
            height_str = str(height_str)
            if 'cm' in height_str:
                return height_str
            
            if '"' in height_str or "'" in height_str:
                parts = height_str.replace('"', '').replace("'", ' ').split()
                if len(parts) >= 2:
                    feet = int(parts[0])
                    inches = int(parts[1])
                    total_cm = (feet * 30.48) + (inches * 2.54)
                    return f"{total_cm:.1f} cm"
        except:
            pass
        return height_str
    
    def _parse_weight(self, weight_str):
        """Convierte peso a formato legible"""
        try:
            if pd.isna(weight_str) or weight_str == '':
                return 'N/A'
            
            if isinstance(weight_str, (int, float)):
                return f"{weight_str:.1f} kg"
            
            weight_str = str(weight_str)
            if 'kg' in weight_str:
                return weight_str
            
            import re
            nums = re.findall(r'\d+', weight_str)
            if nums:
                lbs = float(nums[0])
                kg = lbs * 0.453592
                return f"{kg:.1f} kg"
        except:
            pass
        return weight_str
    
    def get_fight_history(self, fighter_name):
        """Obtiene historial de peleas (solo Kaggle)"""
        if 'fight_details' not in self.dfs:
            return []
        
        df = self.dfs['fight_details']
        mask_rojo = df['r_name'].str.contains(fighter_name, case=False, na=False)
        mask_azul = df['b_name'].str.contains(fighter_name, case=False, na=False)
        peleas = df[mask_rojo | mask_azul].copy()
        
        if len(peleas) == 0:
            return []
        
        historial = []
        for _, pelea in peleas.iterrows():
            es_rojo = fighter_name.lower() in str(pelea['r_name']).lower()
            
            if es_rojo:
                resultado = "Victoria" if pelea['r_kd'] > pelea['b_kd'] else "Derrota"
                oponente = pelea['b_name']
            else:
                resultado = "Victoria" if pelea['b_kd'] > pelea['r_kd'] else "Derrota"
                oponente = pelea['r_name']
            
            historial.append({
                'fecha': pelea.get('event_name', 'Desconocida'),
                'evento': pelea.get('event_name', 'Desconocido'),
                'oponente': oponente,
                'resultado': resultado,
                'metodo': pelea.get('method', 'Desconocido'),
                'round': pelea.get('finish_round', 0),
                'tiempo': pelea.get('match_time_sec', 0)
            })
        
        return historial
    
    def get_win_rate_stats(self, fighter_name):
        """Calcula estadísticas de win rate"""
        historial = self.get_fight_history(fighter_name)
        
        if not historial:
            return {}
        
        total = len(historial)
        wins = sum(1 for h in historial if h['resultado'] == 'Victoria')
        
        ko_wins = 0
        for h in historial:
            if h['resultado'] == 'Victoria' and h['metodo']:
                metodo = str(h['metodo']).upper()
                if 'KO' in metodo or 'TKO' in metodo:
                    ko_wins += 1
        
        recientes = historial[:3]
        wins_recientes = sum(1 for h in recientes if h['resultado'] == 'Victoria')
        
        return {
            'total_peleas': total,
            'victorias': wins,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'ko_pct': (ko_wins / wins * 100) if wins > 0 else 0,
            'forma_reciente': (wins_recientes / len(recientes) * 100) if recientes else 0
        }
    
    def get_fighter_advanced_stats(self, fighter_name):
        """Obtiene estadísticas avanzadas"""
        if 'fight_details' not in self.dfs:
            return {}
        
        df = self.dfs['fight_details']
        mask_rojo = df['r_name'].str.contains(fighter_name, case=False, na=False)
        mask_azul = df['b_name'].str.contains(fighter_name, case=False, na=False)
        peleas = df[mask_rojo | mask_azul].copy()
        
        if len(peleas) == 0:
            return {}
        
        total_stats = {
            'sig_str_landed': 0,
            'sig_str_atmpted': 0,
            'td_landed': 0,
            'td_atmpted': 0,
            'kd': 0,
            'peleas': 0
        }
        
        for _, pelea in peleas.iterrows():
            es_rojo = fighter_name.lower() in str(pelea['r_name']).lower()
            
            if es_rojo:
                total_stats['sig_str_landed'] += pelea.get('r_sig_str_landed', 0)
                total_stats['sig_str_atmpted'] += pelea.get('r_sig_str_atmpted', 0)
                total_stats['td_landed'] += pelea.get('r_td_landed', 0)
                total_stats['td_atmpted'] += pelea.get('r_td_atmpted', 0)
                total_stats['kd'] += pelea.get('r_kd', 0)
            else:
                total_stats['sig_str_landed'] += pelea.get('b_sig_str_landed', 0)
                total_stats['sig_str_atmpted'] += pelea.get('b_sig_str_atmpted', 0)
                total_stats['td_landed'] += pelea.get('b_td_landed', 0)
                total_stats['td_atmpted'] += pelea.get('b_td_atmpted', 0)
                total_stats['kd'] += pelea.get('b_kd', 0)
            
            total_stats['peleas'] += 1
        
        if total_stats['peleas'] > 0:
            return {
                'sig_str_landed_per_fight': total_stats['sig_str_landed'] / total_stats['peleas'],
                'sig_str_acc': (total_stats['sig_str_landed'] / total_stats['sig_str_atmpted'] * 100) if total_stats['sig_str_atmpted'] > 0 else 0,
                'td_landed_per_fight': total_stats['td_landed'] / total_stats['peleas'],
                'td_acc': (total_stats['td_landed'] / total_stats['td_atmpted'] * 100) if total_stats['td_atmpted'] > 0 else 0,
                'kd_per_fight': total_stats['kd'] / total_stats['peleas'],
                'total_peleas': total_stats['peleas']
            }
        
        return {}
