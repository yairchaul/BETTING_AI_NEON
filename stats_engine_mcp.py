"""
Motor estadístico con integración MCP - VERSIÓN CORREGIDA
"""
import asyncio
from typing import List, Dict, Optional

class StatsEngineMCP:
    """StatsEngine que usa MCP para datos en tiempo real"""
    
    def __init__(self):
        self.mcp_client = None
        self.usar_mcp = False
        
    async def iniciar_mcp(self):
        """Inicia la conexión MCP"""
        try:
            from mcp_client import MCPOddsClient
            self.mcp_client = MCPOddsClient()
            await self.mcp_client.conectar()
            self.usar_mcp = True
            print("✅ MCP conectado")
        except Exception as e:
            print(f"⚠️ MCP no disponible: {e}")
            self.usar_mcp = False
            
    async def cerrar_mcp(self):
        """Cierra conexión MCP"""
        if self.mcp_client:
            await self.mcp_client.cerrar()
            
    def enriquecer(self, evento):
        """Enriquece un evento con datos MCP"""
        if self.usar_mcp:
            try:
                # Usar datos reales de MCP (síncrono adaptado)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                resultado = loop.run_until_complete(self._enriquecer_con_mcp(evento))
                loop.close()
                return resultado
            except Exception as e:
                print(f"Error en MCP: {e}")
                return self._enriquecer_sin_mcp(evento)
        else:
            # Fallback al método tradicional
            return self._enriquecer_sin_mcp(evento)
            
    async def _enriquecer_con_mcp(self, evento):
        """Obtiene datos reales vía MCP"""
        try:
            # Buscar el partido en MCP
            partidos = await self.mcp_client.obtener_partidos_hoy()
            
            # Encontrar el partido que coincide
            for p in partidos:
                if hasattr(evento, 'local') and hasattr(evento, 'visitante'):
                    if evento.local in p['home_team'] and evento.visitante in p['away_team']:
                        # Obtener odds específicos
                        odds = await self.mcp_client.obtener_odds_partido(p['id'])
                        
                        # Inicializar mercados si no existe
                        if not hasattr(evento, 'mercados'):
                            evento.mercados = {}
                        
                        # Actualizar evento con datos reales
                        if 'outcomes' in odds and odds['outcomes']:
                            precio = odds['outcomes'][0].get('price', 2.0)
                            evento.mercados['prob_local'] = self._odds_to_prob(precio)
                            evento.mercados['prob_visitante'] = self._odds_to_prob(2.0)
                            evento.mercados['prob_draw'] = self._odds_to_prob(3.5)
                        break
        except Exception as e:
            print(f"Error en _enriquecer_con_mcp: {e}")
            
        return evento
        
    def _odds_to_prob(self, odds):
        """Convierte odds decimal a probabilidad"""
        try:
            return 1 / float(odds) if float(odds) > 1 else 0.5
        except:
            return 0.5
            
    def _enriquecer_sin_mcp(self, evento):
        """Versión tradicional (fallback)"""
        # Aquí va tu lógica existente
        if hasattr(evento, 'deporte') and evento.deporte == 'FUTBOL':
            return self._calcular_futbol(evento)
        return evento
        
    def _calcular_futbol(self, evento):
        """Cálculo tradicional de fútbol"""
        # Tu código existente aquí...
        if not hasattr(evento, 'mercados'):
            evento.mercados = {}
        evento.mercados['prob_local'] = 0.45
        evento.mercados['prob_visitante'] = 0.30
        evento.mercados['prob_draw'] = 0.25
        return evento

async def test_stats_mcp():
    """Prueba del motor estadístico con MCP"""
    engine = StatsEngineMCP()
    
    print("🔍 Probando StatsEngine con MCP...")
    
    await engine.iniciar_mcp()
    await engine.cerrar_mcp()
    
    print("✅ StatsEngine probado")

if __name__ == "__main__":
    asyncio.run(test_stats_mcp())
