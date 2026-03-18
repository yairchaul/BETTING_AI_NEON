"""
ANALIZADOR GEMINI NBA - Reactivado
"""
import google.generativeai as genai
import json
import re
import streamlit as st

class AnalizadorGeminiNBA:
    def __init__(self, api_key):
        self.api_key = api_key
        self.gemini_disponible = False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.gemini_disponible = True
            print("✅ Analizador Gemini NBA inicializado")
        except Exception as e:
            st.warning(f"⚠️ Gemini no disponible: {e}")
    
    def analizar(self, partido, resumen_heurístico):
        if not self.gemini_disponible:
            return {
                'apuesta_seleccionada': '❌ GEMINI NO DISPONIBLE',
                'confianza': 0,
                'color': 'red'
            }
        
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        odds = partido.get('odds', {})
        records = partido.get('records', {})
        
        prompt = f"""
        ACTÚA COMO UN EXPERTO EN APUESTAS DEPORTIVAS (PREMIUM ANALYTICS).
        
        Analiza el partido: {local} vs {visitante}
        
        DATOS:
        - Récords: {local} ({records.get('local', '0-0')}), {visitante} ({records.get('visitante', '0-0')})
        - Moneyline: {local} {odds.get('moneyline', {}).get('local', 'N/A')}, {visitante} {odds.get('moneyline', {}).get('visitante', 'N/A')}
        - Spread: {odds.get('spread', {}).get('valor', 0)}
        - Total: {odds.get('totales', {}).get('linea', 0)}
        
        Proporciona análisis PREMIUM con:
        1. Edge Rating (0-10)
        2. Public Money (%)
        3. Sharps Action (dónde va el dinero inteligente)
        4. Recomendación final
        
        Responde SOLO JSON:
        {{
            "edge_rating": 4.2,
            "public_money": 72,
            "sharps_action": "Heavy on GSW Moneyline",
            "recomendacion": "Celtics -12.5",
            "confianza": 68
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
        
        return {
            'edge_rating': 0,
            'public_money': 50,
            'sharps_action': 'N/A',
            'recomendacion': 'Análisis no disponible',
            'confianza': 0
        }
