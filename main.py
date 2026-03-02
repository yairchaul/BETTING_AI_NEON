# main.py - Versión completa con análisis por imagen
import streamlit as st
import pandas as pd
import numpy as np
import re
import unicodedata
from difflib import SequenceMatcher
import requests
from PIL import Image
# Comenta la línea 10
# import easyocr

# Y reemplaza la clase ImageParser con una versión simulada:
class ImageParser:
    def __init__(self):
        pass
    
    def parse_image(self, uploaded_file):
        # Versión de prueba que devuelve partidos manualmente
        return [
            {'local': 'FC Kyrgyzaltyn', 'visitante': 'Oshmu-Aldiyer', 'liga': 'Kyrgyzstan League'},
            {'local': 'Rakhine United', 'visitante': 'Shan United', 'liga': 'Myanmar League'}
        ], "texto simulado"
import io
import json
from modules.cerebro import (
    buscar_equipos_v2,
    extraer_stats_avanzadas,
    simular_probabilidades,
    obtener_mejor_apuesta,
    obtener_forma_reciente
)

# Configuración de la página
st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

# ============================================================================
# MÓDULO 1: OCR Y PROCESAMIENTO DE IMÁGENES
# ============================================================================

class ImageParser:
    def __init__(self):
        # Inicializar EasyOCR (soporta español e inglés)
        self.reader = easyocr.Reader(['es', 'en'], gpu=False)
    
    def extract_matches_from_text(self, text):
        """Extrae partidos del formato específico de imagen"""
        lines = text.split('\n')
        matches = []
        current_league = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar liga (líneas con guiones)
            if ' - ' in line and len(line.split(' - ')) >= 2:
                current_league = line
            
            # Detectar partido (dos equipos)
            elif ' vs ' in line.lower():
                parts = re.split(r'\s+vs\s+', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    matches.append({
                        'local': parts[0].strip(),
                        'visitante': parts[1].strip(),
                        'liga': current_league
                    })
            else:
                # Posible formato de dos líneas
                if i + 1 < len(lines) and lines[i+1].strip():
                    next_line = lines[i+1].strip()
                    # Evitar capturar fechas o puntuaciones
                    if not any(x in next_line for x in ['Score', 'Points', ':', 'Mar']):
                        matches.append({
                            'local': line,
                            'visitante': next_line,
                            'liga': current_league
                        })
                        i += 1  # Saltar la siguiente línea
            i += 1
        
        return matches
    
    def parse_image(self, uploaded_file):
        """Procesa la imagen y extrae los partidos"""
        try:
            # Leer imagen
            image = Image.open(uploaded_file)
            
            # Convertir a array para EasyOCR
            img_array = np.array(image)
            
            # Detectar texto
            result = self.reader.readtext(img_array)
            
            # Unir todo el texto detectado
            full_text = ' '.join([item[1] for item in result])
            
            # Extraer partidos
            matches = self.extract_matches_from_text(full_text)
            
            return matches, full_text
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return [], ""

# ============================================================================
# MÓDULO 2: MATCHER DE EQUIPOS (SOLUCIÓN A TU PROBLEMA PRINCIPAL)
# ============================================================================

class TeamMatcher:
    def __init__(self):
        self.api_key = st.secrets.get("football_api_key", "")
        self.cache = {}
    
    def normalize_name(self, name):
        """Normaliza nombres: quita acentos, caracteres especiales"""
        # Convertir a minúsculas
        name = name.lower().strip()
        
        # Quitar acentos
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Quitar caracteres especiales
        name = re.sub(r'[^a-z0-9\s]', '', name)
        
        # Quitar palabras comunes que no ayudan en búsqueda
        common_words = ['fc', 'cf', 'sc', 'ac', 'us', 'as', 'cd', 'real', 
                       'united', 'city', 'athletic', 'deportivo', 'club', 
                       'team', 'de', 'del', 'la', 'el', 'los', 'las']
        for word in common_words:
            name = re.sub(r'\b' + word + r'\b', '', name)
        
        # Quitar espacios múltiples
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def similarity_score(self, name1, name2):
        """Calcula similitud entre dos nombres"""
        n1 = self.normalize_name(name1)
        n2 = self.normalize_name(name2)
        return SequenceMatcher(None, n1, n2).ratio()
    
    def search_football_api(self, team_name, league_hint=None):
        """Busca en API-Sports con estrategias múltiples"""
        if not self.api_key:
            return None
            
        headers = {'x-apisports-key': self.api_key}
        normalized = self.normalize_name(team_name)
        
        # Estrategia 1: Búsqueda directa
        try:
            url = f"https://v3.football.api-sports.io/teams?search={normalized}"
            response = requests.get(url, headers=headers).json()
            
            if response.get('results', 0) > 0:
                return response['response'][0]['team']
        except:
            pass
        
        # Estrategia 2: Si hay pista de liga
        if league_hint:
            try:
                league_norm = self.normalize_name(league_hint)
                league_url = f"https://v3.football.api-sports.io/leagues?search={league_norm}"
                league_resp = requests.get(league_url, headers=headers).json()
                
                if league_resp.get('results', 0) > 0:
                    league_id = league_resp['response'][0]['league']['id']
                    
                    # Obtener equipos de la liga
                    teams_url = f"https://v3.football.api-sports.io/teams?league={league_id}&season=2024"
                    teams_resp = requests.get(teams_url, headers=headers).json()
                    
                    best_match = None
                    best_score = 0
                    
                    for item in teams_resp.get('response', []):
                        team = item['team']
                        score = self.similarity_score(team_name, team['name'])
                        
                        if score > best_score and score > 0.5:
                            best_score = score
                            best_match = team
                    
                    if best_match:
                        return best_match
            except:
                pass
        
        return None
    
    def match_team(self, team_name, league_context=None):
        """Función principal para encontrar un equipo"""
        cache_key = f"{team_name}_{league_context}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        team = self.search_football_api(team_name, league_context)
        self.cache[cache_key] = team
        return team

# ============================================================================
# MÓDULO 3: SIMULADOR MONTE CARLO (VERSIÓN SIMPLIFICADA)
# ============================================================================

def run_monte_carlo_simulation(home_attack=1.2, home_defense=1.2, 
                                away_attack=1.2, away_defense=1.2, 
                                simulations=10000):
    """Simula partidos usando distribución de Poisson"""
    
    # Promedios de goles esperados
    league_avg = 1.35
    
    # Calcular lambdas (goles esperados)
    lambda_home = league_avg * (home_attack / 1.2) * (1.2 / away_defense) * 1.1  # ventaja local
    lambda_away = league_avg * (away_attack / 1.2) * (1.2 / home_defense)
    
    # Generar goles con ruido
    noise_home = np.random.normal(1, 0.1, simulations)
    noise_away = np.random.normal(1, 0.1, simulations)
    
    goals_home = np.random.poisson(lambda_home * noise_home)
    goals_away = np.random.poisson(lambda_away * noise_away)
    total_goals = goals_home + goals_away
    
    # Calcular probabilidades
    return {
        'local_gana': np.mean(goals_home > goals_away),
        'empate': np.mean(goals_home == goals_away),
        'visitante_gana': np.mean(goals_away > goals_home),
        'over_1.5': np.mean(total_goals > 1.5),
        'over_2.5': np.mean(total_goals > 2.5),
        'under_2.5': np.mean(total_goals < 2.5),
        'btts': np.mean((goals_home > 0) & (goals_away > 0)),
        'goles_promedio': np.mean(total_goals)
    }

# ============================================================================
# MÓDULO 4: ANALIZADOR DE PARTIDOS
# ============================================================================

class MatchAnalyzer:
    def __init__(self):
        self.matcher = TeamMatcher()
    
    def analyze_match(self, home_name, away_name, league_name=None):
        """Analiza un partido y devuelve todas las opciones"""
        
        # Buscar equipos
        home_team = self.matcher.match_team(home_name, league_name)
        away_team = self.matcher.match_team(away_name, league_name)
        
        # Si no se encuentran, usar valores por defecto
        if not home_team or not away_team:
            # Simulación con valores genéricos
            probs = run_monte_carlo_simulation()
            
            return {
                'home_team': home_name,
                'away_team': away_name,
                'home_found': home_team is not None,
                'away_found': away_team is not None,
                'probabilidades': probs,
                'es_simulado': True
            }
        
        # Simulación con stats específicos (simplificado)
        probs = run_monte_carlo_simulation(
            home_attack=1.3,  # Idealmente vendrían de stats reales
            home_defense=1.1,
            away_attack=1.2,
            away_defense=1.3
        )
        
        return {
            'home_team': home_team['name'],
            'away_team': away_team['name'],
            'home_id': home_team['id'],
            'away_id': away_team['id'],
            'home_found': True,
            'away_found': True,
            'probabilidades': probs,
            'es_simulado': False
        }
    
    def get_all_markets(self, probs):
        """Genera todos los mercados posibles con sus probabilidades"""
        
        markets = []
        
        # Resultado final
        markets.append({'nombre': 'Gana Local', 'prob': probs['local_gana'], 'tipo': '1X2'})
        markets.append({'nombre': 'Empate', 'prob': probs['empate'], 'tipo': '1X2'})
        markets.append({'nombre': 'Gana Visitante', 'prob': probs['visitante_gana'], 'tipo': '1X2'})
        
        # Doble oportunidad
        markets.append({'nombre': 'Local o Empate (1X)', 'prob': probs['local_gana'] + probs['empate'], 'tipo': 'Doble'})
        markets.append({'nombre': 'Visitante o Empate (X2)', 'prob': probs['visitante_gana'] + probs['empate'], 'tipo': 'Doble'})
        
        # Totales
        markets.append({'nombre': 'Over 1.5 goles', 'prob': probs['over_1.5'], 'tipo': 'Total'})
        markets.append({'nombre': 'Over 2.5 goles', 'prob': probs['over_2.5'], 'tipo': 'Total'})
        markets.append({'nombre': 'Under 2.5 goles', 'prob': probs['under_2.5'], 'tipo': 'Total'})
        
        # BTTS
        markets.append({'nombre': 'Ambos anotan (BTTS)', 'prob': probs['btts'], 'tipo': 'BTTS'})
        markets.append({'nombre': 'No anotan ambos', 'prob': 1 - probs['btts'], 'tipo': 'BTTS'})
        
        # Combinados
        markets.append({
            'nombre': 'Gana Local + Over 1.5', 
            'prob': probs['local_gana'] * probs['over_1.5'] * 1.1, 
            'tipo': 'Combinado'
        })
        markets.append({
            'nombre': 'Gana Visitante + Over 1.5', 
            'prob': probs['visitante_gana'] * probs['over_1.5'] * 1.1, 
            'tipo': 'Combinado'
        })
        
        # Ordenar por probabilidad
        markets.sort(key=lambda x: x['prob'], reverse=True)
        
        return markets

# ============================================================================
# MÓDULO 5: GENERADOR DE PARLAYS
# ============================================================================

def build_parlay(picks):
    """Construye un parlay a partir de picks seleccionados"""
    if not picks:
        return None
    
    total_prob = 1.0
    total_odd = 1.0
    matches_list = []
    
    for pick in picks:
        total_prob *= pick['prob']
        # Estimación de cuota (inversa de probabilidad con margen)
        odd = 1 / pick['prob'] * 0.95
        total_odd *= odd
        matches_list.append(f"{pick['match']}: {pick['selection']}")
    
    ev = (total_prob * total_odd) - 1
    
    return {
        'matches': matches_list,
        'total_odd': round(total_odd, 2),
        'total_prob': round(total_prob, 4),
        'ev': round(ev, 4)
    }

# ============================================================================
# INTERFAZ PRINCIPAL DE STREAMLIT
# ============================================================================

def main():
    st.title("🎯 Analizador Universal de Partidos")
    st.markdown("Sube una captura de cualquier liga y analizo **partido por partido**")
    
    # Inicializar componentes
    if 'parser' not in st.session_state:
        st.session_state.parser = ImageParser()
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = MatchAnalyzer()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        prob_minima = st.slider(
            "Probabilidad mínima para mostrar",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05
        )
        
        st.divider()
        
        # Estado de la API
        if st.secrets.get("football_api_key"):
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ Modo simulación (sin API)")
            st.caption("Las probabilidades son genéricas")
    
    # Área principal
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader(
            "Selecciona imagen (PNG, JPG, JPEG)",
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Captura subida", use_column_width=True)
    
    if uploaded_file:
        # Procesar imagen
        with st.spinner("🔍 Procesando imagen..."):
            matches, raw_text = st.session_state.parser.parse_image(uploaded_file)
            
            # Debug (opcional)
            with st.expander("🔬 Ver texto detectado"):
                st.text(raw_text[:500])
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                df = pd.DataFrame([
                    {
                        'Local': m['local'][:25],
                        'Visitante': m['visitante'][:25],
                        'Liga': m.get('liga', 'Desconocida')[:20]
                    }
                    for m in matches
                ])
                st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("3. Análisis partido por partido")
            
            # Analizar cada partido
            all_picks = []
            
            for i, match in enumerate(matches):
                with st.expander(f"📊 {match['local']} vs {match['visitante']}", expanded=i==0):
                    
                    # Analizar
                    analysis = st.session_state.analyzer.analyze_match(
                        match['local'],
                        match['visitante'],
                        match.get('liga')
                    )
                    
                    # Mostrar resultados de búsqueda
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ Local: {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ Local: {match['local']} (no encontrado)")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ Visitante: {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ Visitante: {match['visitante']} (no encontrado)")
                    
                    # Obtener todos los mercados
                    markets = st.session_state.analyzer.get_all_markets(analysis['probabilidades'])
                    
                    # Filtrar por probabilidad mínima
                    markets_filtered = [m for m in markets if m['prob'] >= prob_minima]
                    
                    if markets_filtered:
                        # Mostrar en tabla
                        market_data = []
                        for m in markets_filtered[:8]:  # Top 8
                            market_data.append({
                                'Mercado': m['nombre'],
                                'Probabilidad': f"{m['prob']:.1%}",
                                'Tipo': m['tipo']
                            })
                        
                        st.dataframe(pd.DataFrame(market_data), use_container_width=True)
                        
                        # Mejor opción
                        best = markets_filtered[0]
                        st.success(f"✨ **Mejor opción:** {best['nombre']} - {best['prob']:.1%}")
                        
                        # Guardar para parlays
                        all_picks.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['nombre'],
                            'prob': best['prob'],
                            'tipo': best['tipo']
                        })
                    else:
                        st.info("No hay mercados con probabilidad suficiente")
            
            # Generar parlays
            if all_picks:
                st.divider()
                st.subheader("🎯 Parlays recomendados")
                
                # Mostrar picks individuales
                st.markdown("**Selecciones disponibles:**")
                
                # CORREGIDO: Aquí estaba el error de indentación
                cols = st.columns(3)
                for idx, pick in enumerate(all_picks[:6]):  # Limitar a 6
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{pick['match']}**")
                            st.markdown(f"📌 {pick['selection']}")
                            st.metric("Probabilidad", f"{pick['prob']:.1%}")
                
                # Botón para generar combinaciones
                if st.button("🔄 Generar combinaciones de 2 selecciones"):
                    # Generar combinaciones simples
                    from itertools import combinations
                    
                    parlays = []
                    for combo in combinations(all_picks, 2):
                        parlay = build_parlay(list(combo))
                        if parlay and parlay['ev'] > 0:
                            parlays.append(parlay)
                    
                    if parlays:
                        st.markdown("**Top parlays encontrados:**")
                        
                        for i, p in enumerate(parlays[:5]):
                            with st.container(border=True):
                                st.markdown(f"**Parlay #{i+1}**")
                                st.markdown(f"Cuota: {p['total_odd']} | Prob: {p['total_prob']:.1%} | EV: {p['ev']:.2%}")
                                for m in p['matches']:
                                    st.markdown(f"• {m}")
                    else:
                        st.info("No se encontraron parlays con EV positivo")
        else:
            st.error("❌ No se detectaron partidos en la imagen")
            st.info("Intenta con una captura más clara o de diferente formato")
    else:
        # Mensaje inicial
        st.info("👆 Sube una imagen para comenzar el análisis")
        
        with st.expander("📋 Ver ejemplo de formato aceptado"):
            st.code("""
Asia - Kyrgyzstan - Pervaya Liga
FC Kyrgyzaltyn vs Oshmu-Aldiyer
02 Mar 03:00
Puntos: +17

Australia - Victoria Premier League 2
Bulleen Lions vs Eltham Redbacks FC
02 Mar 03:30
Puntos: +16
            """)
        
        with st.expander("ℹ️ Cómo funciona"):
            st.markdown("""
            1. **Subes una captura** de cualquier casa de apuestas
            2. **El OCR detecta** los nombres de equipos
            3. **Buscamos los equipos** en la base de datos (con matching inteligente)
            4. **Simulamos el partido** con Monte Carlo
            5. **Analizamos todos los mercados** posibles
            6. **Te mostramos la mejor opción** para cada partido
            7. **Generamos parlays** combinando las mejores selecciones
            """)

if __name__ == "__main__":
    main()
