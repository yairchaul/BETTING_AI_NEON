import streamlit as st
import importlib
import datetime
import re

# --- LÓGICA DE IMPORTACIÓN ---
ufc_api = None
try:
    ufc_api = importlib.import_module('ufc_api')
except ImportError:
    try:
        ufc_api = importlib.import_module('ufc-api')
    except ImportError:
        pass

get_fighter = getattr(ufc_api, 'get_fighter', None) if ufc_api else None

class UFCRealAPI:
    def __init__(self):
        self.cache_fighters = {}

    def get_fighter_stats(self, fighter_name):
        if not get_fighter: return None
        if fighter_name in self.cache_fighters: return self.cache_fighters[fighter_name]
        try:
            data = get_fighter(fighter_name)
            self.cache_fighters[fighter_name] = data
            return data
        except:
            return None

    def parse_fighter_stats(self, data):
        if not data: return None
        try:
            wins = data.get('wins', {})
            w = int(wins.get('total', 0))
            l = int(data.get('losses', {}).get('total', 0))
            t = (w + l) if (w + l) > 0 else 1
            return {
                'name': data.get('name', 'N/A'),
                'win_rate': w / t,
                'total_fights': t
            }
        except: return None

PELEAS_UFC = [
    {'fighter1': 'Chris Curtis', 'fighter2': 'Myktybek Orolbai', 'odds1': 210, 'odds2': -286}
]
