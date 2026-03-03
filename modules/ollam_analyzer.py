# modules/ollama_analyzer.py
import requests
import json
import streamlit as st
import re

class OllamaAnalyzer:
    """
    Analizador local con Llama 3.1 vía Ollama
    Basado en neural-odds [citation:2] y CrewAI [citation:5]
    """
    
    def __init__(self, model="llama3.1:8b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.is_available = self._check_connection()
        
        if self.is_available:
            st.success(f"✅ Ollama conectado con modelo {model}")
        else:
            st.warning("⚠️ Ollama no disponible - El análisis local estará desactivado")
    
    def _check_connection(self):
        """Verifica si Ollama está corriendo"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def analyze_match(self, home_team, away_team, stats=None, context=None):
        """
        Analiza un partido usando Llama 3.1
        """
        if not self.is_available:
            return None
        
        # Construir prompt
        prompt = self._build_prompt(home_team, away_team, stats, context)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result['response'])
            else:
                return None
                
        except Exception as e:
            st.error(f"Error en Ollama: {e}")
            return None
    
    def _build_prompt(self, home, away, stats, context):
        """Construye el prompt para Llama"""
        prompt = f"""
        Eres un analista experto en apuestas deportivas. Analiza este partido:
        
        EQUIPO LOCAL: {home}
        EQUIPO VISITANTE: {away}
        
        """
        
        if stats:
            prompt += f"""
            ESTADÍSTICAS:
            - Promedio goles local: {stats.get('home_goals_avg', 'N/A')}
            - Promedio goles visitante: {stats.get('away_goals_avg', 'N/A')}
            - BTTS últimos partidos: {stats.get('btts_pct', 'N/A')}%
            """
        
        prompt += """
        Por favor, proporciona:
        1. PREDICCIÓN DEL RESULTADO (Local/Empate/Visitante) con probabilidad
        2. PROBABILIDAD DE AMBOS ANOTAN (BTTS)
        3. PROBABILIDAD DE OVER 2.5 GOLES
        4. MEJOR APUESTA RECOMENDADA con breve explicación
        
        Responde en formato JSON:
        {
            "local_win_prob": 0.XX,
            "draw_prob": 0.XX,
            "away_win_prob": 0.XX,
            "btts_prob": 0.XX,
            "over_2_5_prob": 0.XX,
            "best_bet": "nombre del mercado",
            "explanation": "explicación breve"
        }
        """
        
        return prompt
    
    def _parse_response(self, response_text):
        """Extrae JSON de la respuesta"""
        try:
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return None
        except:
            return None
    
    def get_team_context(self, team_name):
        """
        Obtiene contexto de un equipo usando el conocimiento de Llama
        """
        if not self.is_available:
            return None
        
        prompt = f"""
        Dame información sobre el equipo de fútbol {team_name}:
        - País y liga donde juega
        - Nivel del equipo (grande/medio/pequeño)
        - Estilo de juego (ofensivo/defensivo/equilibrado)
        - Algún dato curioso o relevante
        
        Responde en formato JSON:
        {{
            "country": "país",
            "league": "liga",
            "level": "grande/medio/pequeño",
            "style": "ofensivo/defensivo/equilibrado",
            "trivia": "dato curioso"
        }}
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result['response'])
        except:
            pass
        
        return None