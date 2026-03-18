"""
ANALIZADOR UFC GEMINI - Análisis con inteligencia artificial
"""
import google.generativeai as genai
import json
import re
import streamlit as st

class AnalizadorUFCGemini:
    def __init__(self, api_key):
        self.api_key = api_key
        self.gemini_disponible = False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.gemini_disponible = True
            print("✅ Analizador UFC Gemini inicializado")
        except Exception as e:
            st.warning(f"⚠️ Gemini no disponible: {e}")
    
    def analizar(self, f1_data, f2_data, resumen_heurístico):
        """
        Envía todos los datos a Gemini para análisis profundo
        """
        if not self.gemini_disponible:
            return {
                'ganador': 'GEMINI NO DISPONIBLE',
                'prob_f1': 0,
                'prob_f2': 0,
                'metodo': 'N/A',
                'edge_rating': 0,
                'factores_clave': [],
                'color': 'red'
            }
        
        # Extraer datos del resumen heurístico
        f1_nombre = resumen_heurístico.get('f1_nombre', f1_data.get('nombre', ''))
        f2_nombre = resumen_heurístico.get('f2_nombre', f2_data.get('nombre', ''))
        f1_record = resumen_heurístico.get('f1_record', '0-0-0')
        f2_record = resumen_heurístico.get('f2_record', '0-0-0')
        f1_winrate = resumen_heurístico.get('f1_winrate', 50)
        f2_winrate = resumen_heurístico.get('f2_winrate', 50)
        
        prompt = f"""
        ACTÚA COMO UN EXPERTO EN ANÁLISIS DE UFC CON MAESTRÍA EN DATA SCIENCE.
        
        Analiza el siguiente combate de UFC:
        
        **PELEADOR 1:** {f1_nombre}
        - Récord: {f1_record}
        - Win Rate: {f1_winrate}%
        
        **PELEADOR 2:** {f2_nombre}
        - Récord: {f2_record}
        - Win Rate: {f2_winrate}%
        
        Basado en estos datos, determina:
        
        1. Probabilidad de victoria para cada peleador (0-100%)
        2. Método más probable (KO/TKO, Sumisión, Decisión)
        3. Edge Rating (0-10) basado en la diferencia de win rates
        
        Responde SOLO con JSON:
        {{
            "prob_f1": 60,
            "prob_f2": 40,
            "ganador": "{f1_nombre}",
            "metodo": "Decisión",
            "edge_rating": 6.5,
            "factores_clave": ["Mayor win rate", "Experiencia en peleas largas"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                resultado = json.loads(match.group(0))
                return resultado
        except Exception as e:
            st.warning(f"⚠️ Error en Gemini: {e}")
        
        return {
            'ganador': 'Análisis no disponible',
            'prob_f1': 0,
            'prob_f2': 0,
            'metodo': 'N/A',
            'edge_rating': 0,
            'factores_clave': [],
            'color': 'red'
        }
