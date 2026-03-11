"""
Módulo de procesadores para BETTING_AI
"""
from .procesador_futbol import ProcesadorFutbol, procesar_futbol
from .vision_reader import VisionReader

__all__ = ['ProcesadorFutbol', 'procesar_futbol', 'VisionReader']
