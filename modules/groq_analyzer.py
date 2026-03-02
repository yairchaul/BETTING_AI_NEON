# modules/groq_analyzer.py
import streamlit as st
from groq import Groq
import json
import re

class GroqAnalyzer:
    def __init__(self):
        """Inicializa el cliente de Groq"""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Modelo recomendado para análisis
        self.model = "llama-3.3-70b-versatile"
    
    def analyze_match(self, home_team, away_team, odds_data=None):
        """
        Usa Groq para analizar el partido y predecir probabilidades
        """
        try:
            # Construir prompt detallado para Groq
            odds_text = f"ODDS DE LA CASA DE APUESTAS: Local {odds_data[0]}, Empate {odds_data[1]}, Visitante {odds_data[2]}" if odds_data else ""
            
            prompt = f"""
            Eres un experto analista de apuestas deportivas con acceso a información actualizada de fútbol.
            
            PARTIDO: {home_team} vs {away_team}
            
            {odds_text}
            
            Por favor, analiza este partido y proporciona:
            
            1. PREDICCIÓN DEL RESULTADO (Local/Empate/Visitante) con probabilidad (0-100%)
            2. PROBABILIDAD DE AMBOS EQUIPOS ANOTAN (BTTS) (0-100%)
            3. PROBABILIDAD DE OVER 1.5 GOLES (0-100%)
            4. PROBABILIDAD DE OVER 2.5 GOLES (0-100%)
            5. PROBABILIDAD DE OVER 3.5 GOLES (0-100%)
            6. PROBABILIDAD DE OVER 4.5 GOLES (0-100%)
            7. PROBABILIDAD DE OVER 5.5 GOLES (0-100%)
            8. PROBABILIDAD DE GOLES EN PRIMER TIEMPO (Over 0.5 y Over 1.5)
            9. MEJOR APUESTA RECOMENDADA (con explicación breve)
            
            IMPORTANTE: 
            - Basa tu análisis en tendencias actuales, historial reciente y estadísticas
            - Si no conoces algún equipo, investiga mentalmente su liga y rendimiento
            - Las probabilidades deben sumar coherencia (ej: Over 2.5 no puede ser mayor que Over 1.5)
            
            Responde SOLO con un objeto JSON válido con esta estructura:
            {{
                "resultado_local": 0.XX,
                "resultado_empate": 0.XX,
                "resultado_visitante": 0.XX,
                "btts": 0.XX,
                "over_1_5": 0.XX,
                "over_2_5": 0.XX,
                "over_3_5": 0.XX,
                "over_4_5": 0.XX,
                "over_5_5": 0.XX,
                "over_0_5_1t": 0.XX,
                "over_1_5_1t": 0.XX,
                "mejor_apuesta": "texto con la mejor opción",
                "explicacion": "breve explicación del análisis",
                "liga": "nombre de la liga si la conoces",
                "confianza": "ALTA/MEDIA/BAJA"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista experto en apuestas de fútbol. Respondes solo con JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parsear respuesta
            content = response.choices[0].message.content
            content = re.sub(r'```json\s*|\s*```', '', content)
            result = json.loads(content)
            
            return result
            
        except Exception as e:
            st.error(f"Error en Groq Analyzer: {e}")
            return None
