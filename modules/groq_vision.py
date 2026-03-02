# modules/groq_analyzer.py
import streamlit as st
from groq import Groq
import json
import re

class GroqAnalyzer:
    def __init__(self):
        """Inicializa el cliente de Groq"""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Modelo recomendado: llama-3.3-70b-versatile o mixtral-8x7b-32768
        self.model = "llama-3.3-70b-versatile"
    
    def analyze_match(self, home_team, away_team, odds_data=None):
        """
        Usa Groq para analizar el partido y predecir probabilidades
        """
        try:
            # Construir prompt detallado para Groq
            prompt = f"""
            Eres un experto analista de apuestas deportivas con acceso a información actualizada de fútbol.
            
            PARTIDO: {home_team} vs {away_team}
            
            {f'ODDS DE LA CASA DE APUESTAS: Local {odds_data[0]}, Empate {odds_data[1]}, Visitante {odds_data[2]}' if odds_data else ''}
            
            Por favor, analiza este partido y proporciona:
            
            1. PREDICCIÓN DEL RESULTADO (Local/Empate/Visitante) con probabilidad (0-100%)
            2. PROBABILIDAD DE AMBOS EQUIPOS ANOTAN (BTTS) (0-100%)
            3. PROBABILIDAD DE OVER 1.5 GOLES (0-100%)
            4. PROBABILIDAD DE OVER 2.5 GOLES (0-100%)
            5. PROBABILIDAD DE OVER 3.5 GOLES (0-100%)
            6. PROBABILIDAD DE OVER 4.5 GOLES (0-100%)
            7. PROBABILIDAD DE OVER 5.5 GOLES (0-100%)
            8. PROBABILIDAD DE GOLES EN PRIMER TIEMPO (Over 0.5/1.5)
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
                "explicacion": "breve explicación del análisis"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista experto en apuestas de fútbol. Respondes solo con JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Bajo para consistencia
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
    
    def analyze_with_search(self, home_team, away_team, odds_data=None):
        """
        Versión con capacidad de "búsqueda" - Groq puede buscar en su conocimiento
        """
        try:
            prompt = f"""
            INVESTIGA Y ANALIZA: {home_team} vs {away_team}
            
            Instrucciones:
            1. PRIMERO: Busca en tu conocimiento información sobre estos equipos
            2. SEGUNDO: Identifica en qué liga juegan y su nivel
            3. TERCERO: Recuerda sus últimos resultados conocidos
            4. CUARTO: Determina si son equipos goleadores o defensivos
            5. QUINTO: Basado en todo lo anterior, genera probabilidades realistas
            
            {f'Odds de referencia: Local {odds_data[0]}, Empate {odds_data[1]}, Visitante {odds_data[2]}' if odds_data else ''}
            
            Responde SOLO con JSON:
            {{
                "liga": "nombre de la liga",
                "nivel_equipos": "descripción",
                "resultado_local": 0.XX,
                "resultado_empate": 0.XX,
                "resultado_visitante": 0.XX,
                "btts": 0.XX,
                "over_1_5": 0.XX,
                "over_2_5": 0.XX,
                "over_3_5": 0.XX,
                "mejor_apuesta": "texto",
                "confianza": "ALTA/MEDIA/BAJA"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            content = re.sub(r'```json\s*|\s*```', '', content)
            return json.loads(content)
            
        except Exception as e:
            st.error(f"Error: {e}")
            return None


# ============================================================================
# NUEVO ANALIZADOR HÍBRIDO: Combina APIs + Groq
# ============================================================================

class HybridAnalyzer:
    """
    Analizador que combina:
    - Football API (cuando encuentra los equipos)
    - Groq AI (cuando no encuentra o como respaldo)
    - Búsqueda inteligente en conocimiento de Groq
    """
    
    def __init__(self):
        from modules.smart_searcher import SmartSearcher
        self.searcher = SmartSearcher()
        self.groq = GroqAnalyzer() if st.secrets.get("GROQ_API_KEY") else None
    
    def analyze_match(self, home_name, away_name, odds_data=None):
        """
        Análisis híbrido: intenta APIs, si falla usa Groq
        """
        result = {
            'home_team': home_name,
            'away_team': away_name,
            'home_found': False,
            'away_found': False,
            'markets': [],
            'probabilidades': {},
            'source': 'unknown'
        }
        
        # INTENTO 1: Buscar en APIs tradicionales
        home_team = self.searcher.find_team(home_name)
        away_team = self.searcher.find_team(away_name)
        
        if home_team and away_team:
            # Tenemos los equipos, obtener stats reales
            from modules.real_analyzer import RealAnalyzer
            real = RealAnalyzer()
            analysis = real.analyze_match(home_name, away_name)
            analysis['source'] = 'API Sports Database'
            return analysis
        
        # INTENTO 2: Usar Groq con análisis inteligente
        if self.groq:
            st.info(f"🤖 Usando Groq AI para analizar {home_name} vs {away_name}")
            
            # Primero intentar con "búsqueda" en conocimiento de Groq
            groq_result = self.groq.analyze_with_search(home_name, away_name, odds_data)
            
            if groq_result:
                # Convertir resultado de Groq a formato de mercados
                markets = []
                
                # Resultado final
                if 'resultado_local' in groq_result:
                    markets.append({'name': 'Gana Local', 'prob': groq_result['resultado_local'], 'category': '1X2'})
                if 'resultado_empate' in groq_result:
                    markets.append({'name': 'Empate', 'prob': groq_result['resultado_empate'], 'category': '1X2'})
                if 'resultado_visitante' in groq_result:
                    markets.append({'name': 'Gana Visitante', 'prob': groq_result['resultado_visitante'], 'category': '1X2'})
                
                # Totales
                if 'over_1_5' in groq_result:
                    markets.append({'name': 'Over 1.5 goles', 'prob': groq_result['over_1_5'], 'category': 'Totales'})
                if 'over_2_5' in groq_result:
                    markets.append({'name': 'Over 2.5 goles', 'prob': groq_result['over_2_5'], 'category': 'Totales'})
                if 'over_3_5' in groq_result:
                    markets.append({'name': 'Over 3.5 goles', 'prob': groq_result['over_3_5'], 'category': 'Totales'})
                
                # BTTS
                if 'btts' in groq_result:
                    markets.append({'name': 'Ambos anotan (BTTS)', 'prob': groq_result['btts'], 'category': 'BTTS'})
                
                # Ordenar por probabilidad
                markets.sort(key=lambda x: x['prob'], reverse=True)
                
                result['markets'] = markets
                result['home_found'] = True
                result['away_found'] = True
                result['source'] = f"Groq AI - {groq_result.get('liga', 'Análisis inteligente')}"
                result['probabilidades'] = {'goles_promedio': groq_result.get('over_2_5', 0.5) * 3}
                result['groq_analysis'] = groq_result
                
                return result
        
        # INTENTO 3: Fallback a genérico
        from modules.real_analyzer import RealAnalyzer
        real = RealAnalyzer()
        generic = real._generate_generic_analysis(home_name, away_name)
        generic['source'] = 'Estadísticas genéricas'
        return generic
