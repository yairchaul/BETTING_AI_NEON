"""
Configuración para Claude Desktop MCP (Model Context Protocol)
Permite que Claude acceda directamente a The Odds API
"""
import json
import os

# ============================================
# CONFIGURACIÓN PARA CLAUDE DESKTOP
# ============================================
MCP_CONFIG = {
    "mcpServers": {
        "odds-api": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-odds-api"
            ],
            "env": {
                "ODDS_API_KEY": "98ccdb7d4c28042caa8bc8fe7ff6cc62"
            }
        },
        "football-data": {
            "command": "python",
            "args": [
                "C:\\Users\\Yair\\Desktop\\BETTING_AI\\mcp_football_server.py"
            ],
            "env": {
                "FOOTBALL_API_KEY": "98ccdb7d4c28042caa8bc8fe7ff6cc62"
            }
        }
    }
}

# ============================================
# SERVIDOR MCP PERSONALIZADO PARA FÚTBOL
# ============================================
MCP_FOOTBALL_SERVER = """
#!/usr/bin/env python
\"\"\"
Servidor MCP personalizado para datos de fútbol
Permite que Claude consulte estadísticas en tiempo real
\"\"\"
import asyncio
import json
import sys
from typing import Any, Dict, List
from api_client import OddsAPIClient, FootballStatsAPI

class FootballMCPServer:
    \"\"\"Servidor MCP para datos de fútbol\"\"\"
    
    def __init__(self):
        self.odds_client = OddsAPIClient()
        self.stats_client = FootballStatsAPI()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Maneja requests de Claude\"\"\"
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "get_odds":
            sport = params.get("sport", "soccer")
            partidos = self.odds_client.get_partidos_futbol()
            return {"result": partidos}
        
        elif method == "get_team_stats":
            team = params.get("team")
            stats = self.stats_client.get_team_stats(team)
            return {"result": stats}
        
        elif method == "analyze_match":
            home = params.get("home")
            away = params.get("away")
            # Aquí iría el análisis completo
            return {"result": {"message": "Análisis completado"}}
        
        elif method == "list_tools":
            return {
                "result": {
                    "tools": [
                        {
                            "name": "get_odds",
                            "description": "Obtiene odds de partidos de fútbol",
                            "parameters": {
                                "sport": {"type": "string", "default": "soccer"}
                            }
                        },
                        {
                            "name": "get_team_stats",
                            "description": "Obtiene estadísticas de un equipo",
                            "parameters": {
                                "team": {"type": "string", "required": True}
                            }
                        },
                        {
                            "name": "analyze_match",
                            "description": "Analiza un partido y da recomendaciones",
                            "parameters": {
                                "home": {"type": "string", "required": True},
                                "away": {"type": "string", "required": True}
                            }
                        }
                    ]
                }
            }
        
        return {"error": f"Unknown method: {method}"}
    
    async def run(self):
        \"\"\"Ejecuta el servidor MCP\"\"\"
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line)
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                error_response = {"error": str(e)}
                print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    server = FootballMCPServer()
    asyncio.run(server.run())
"""

# ============================================
# INSTRUCCIONES PARA CONFIGURAR CLAUDE
# ============================================
INSTRUCCIONES = """
🔧 CÓMO CONFIGURAR CLAUDE CON MCP:

1. Instalar MCP CLI:
   npm install -g @modelcontextprotocol/cli

2. Configurar Claude Desktop:
   - Archivo: %APPDATA%/Claude/claude_desktop_config.json
   - Pegar el contenido de MCP_CONFIG

3. Probar conexión:
   mcp-cli connect odds-api

4. En Claude, ahora puedes preguntar:
   - "¿Qué partidos hay hoy?"
   - "Analiza el Real Madrid vs Manchester City"
   - "Dame estadísticas del Liverpool"

5. Para nuestro servidor personalizado:
   python mcp_football_server.py
"""

# ============================================
# GUARDAR ARCHIVOS
# ============================================
if __name__ == "__main__":
    # Guardar configuración para Claude
    with open("claude_mcp_config.json", "w") as f:
        json.dump(MCP_CONFIG, f, indent=2)
    
    # Guardar servidor MCP
    with open("mcp_football_server.py", "w") as f:
        f.write(MCP_FOOTBALL_SERVER)
    
    # Guardar instrucciones
    with open("MCP_INSTRUCCIONES.txt", "w") as f:
        f.write(INSTRUCCIONES)
    
    print("✅ Archivos MCP generados:")
    print("  - claude_mcp_config.json")
    print("  - mcp_football_server.py")
    print("  - MCP_INSTRUCCIONES.txt")
