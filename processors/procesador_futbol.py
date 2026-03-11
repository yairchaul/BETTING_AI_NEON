"""
Procesador específico para fútbol - CON ESTADÍSTICAS
"""
import re
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evento import Evento

class ProcesadorFutbol:
    """Procesa capturas de fútbol con formato de 6 espacios"""
    
    def __init__(self):
        self.deporte = "FUTBOL"
        self.patron_partido = re.compile(
            r'([A-Za-zÀ-ÿ\s]+?)\s+'  # Equipo local
            r'([+-]?\d+)\s+'         # Cuota local
            r'Empate\s+'              # Palabra "Empate"
            r'([+-]?\d+)\s+'          # Cuota empate
            r'([A-Za-zÀ-ÿ\s]+?)\s+'   # Equipo visitante
            r'([+-]?\d+)'             # Cuota visitante
        )
    
    def procesar(self, texto: str, nombre_archivo: str = "") -> List[Evento]:
        eventos = []
        lineas = texto.split('\n')
        
        print(f"🔍 ProcesadorFutbol: Analizando {len(lineas)} líneas")
        
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if not linea:
                continue
                
            match = self.patron_partido.search(linea)
            if match:
                try:
                    evento = self._crear_evento(match, linea)
                    if evento:
                        # Añadir estadísticas por defecto
                        evento.stats = {
                            'gf_local': 1.5,
                            'gf_visitante': 1.3,
                            'posesion_local': 52,
                            'posesion_visitante': 48
                        }
                        eventos.append(evento)
                        print(f"  ✅ {evento.equipo_local} vs {evento.equipo_visitante}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        print(f"📊 Total eventos: {len(eventos)}")
        return eventos
    
    def _crear_evento(self, match, linea_original):
        try:
            local = match.group(1).strip()
            cuota_local = self._convertir_cuota(match.group(2))
            cuota_empate = self._convertir_cuota(match.group(3))
            visitante = match.group(4).strip()
            cuota_visitante = self._convertir_cuota(match.group(5))
            
            evento = Evento(
                deporte=self.deporte,
                competencia="UEFA Champions League",
                equipo_local=local,
                equipo_visitante=visitante,
                odds_local=cuota_local,
                odds_empate=cuota_empate,
                odds_visitante=cuota_visitante
            )
            
            evento.debug_info = {
                'linea_original': linea_original,
                'match_groups': [match.group(i) for i in range(1, 6)]
            }
            
            return evento
            
        except Exception as e:
            print(f"Error creando evento: {e}")
            return None
    
    def _convertir_cuota(self, cuota_str: str) -> float:
        """Convierte formato americano a decimal"""
        try:
            cuota_str = cuota_str.strip()
            
            if '.' in cuota_str:
                return float(cuota_str)
            
            if cuota_str.startswith('+'):
                valor = int(cuota_str[1:])
                return round((valor / 100) + 1, 2)
            elif cuota_str.startswith('-'):
                valor = int(cuota_str[1:])
                return round((100 / valor) + 1, 2)
            else:
                valor = int(cuota_str)
                if valor > 0:
                    return round((valor / 100) + 1, 2)
                else:
                    return round((100 / abs(valor)) + 1, 2)
                    
        except Exception as e:
            print(f"Error convirtiendo '{cuota_str}': {e}")
            return 0.0

def procesar_futbol(texto: str, nombre_archivo: str = "") -> List[Evento]:
    procesador = ProcesadorFutbol()
    return procesador.procesar(texto, nombre_archivo)

if __name__ == "__main__":
    # Prueba
    texto_prueba = """
    Bayer Leverkusen +490 Empate +320 Arsenal -186
    Real Madrid +260 Empate +265 Manchester City -104
    """
    eventos = procesar_futbol(texto_prueba)
    for e in eventos:
        print(f"{e.equipo_local} vs {e.equipo_visitante}")
