import asyncio
from mcp_odds_api import MCPServer

async def main():
    # Configurar el servidor MCP con tu API key
    server = MCPServer(
        api_key="98ccdb7d4c28042caa8bc8fe7ff6cc62",
        regions=["mx", "us"],
        sport="soccer"
    )
    
    # Iniciar el servidor
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
