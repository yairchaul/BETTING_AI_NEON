"""
Clase universal para eventos deportivos
"""
from typing import Dict, Any, Optional
from datetime import datetime

class Evento:
    """Representa un evento deportivo (partido, combate, etc.)"""
    
    def __init__(
        self,
        deporte: str,
        competencia: str = "",
        equipo_local: str = "",
        equipo_visitante: str = "",
        odds_local: float = 0.0,
        odds_empate: Optional[float] = None,
        odds_visitante: float = 0.0,
        **kwargs
    ):
        self.deporte = deporte.upper()
        self.competencia = competencia
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
        self.odds_local = odds_local
        self.odds_empate = odds_empate
        self.odds_visitante = odds_visitante
        self.timestamp = kwargs.get('timestamp', datetime.now())
        
        # Atributos adicionales
        self.mercados = {}
        self.stats = {}
        self.probabilidades = {}
        self.value_bets = []
        self.debug_info = {}
        
        # Guardar kwargs adicionales
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        if self.deporte == "FUTBOL":
            return f"<Evento FUTBOL: {self.equipo_local} vs {self.equipo_visitante}>"
        return f"<Evento {self.deporte}>"
    
    def to_dict(self) -> Dict:
        return {
            'deporte': self.deporte,
            'competencia': self.competencia,
            'equipo_local': self.equipo_local,
            'equipo_visitante': self.equipo_visitante,
            'odds_local': self.odds_local,
            'odds_empate': self.odds_empate,
            'odds_visitante': self.odds_visitante,
            'mercados': self.mercados,
            'probabilidades': self.probabilidades,
            'value_bets': self.value_bets
        }
