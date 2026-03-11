"""
Test de integración MCP - VERSIÓN CORREGIDA
"""
import asyncio
import os
import sys

async def main():
    print("="*50)
    print("🧪 TEST DE INTEGRACIÓN MCP")
    print("="*50)
    
    # Mostrar configuración
    print("\n📁 Configuración:")
    print(f"  ODDS_API_KEY: {os.getenv('ODDS_API_KEY', '❌ No configurada')}")
    print(f"  ODDS_API_REGIONS: {os.getenv('ODDS_API_REGIONS', '❌ No configurada')}")
    print(f"  ODDS_API_SPORT: {os.getenv('ODDS_API_SPORT', '❌ No configurada')}")
    
    # Probar cliente MCP
    print("\n🔍 Probando cliente MCP...")
    try:
        from mcp_client import probar_mcp
        await probar_mcp()
    except Exception as e:
        print(f"❌ Error importando mcp_client: {e}")
    
    # Probar motor estadístico
    print("\n📊 Probando motor estadístico...")
    try:
        from stats_engine_mcp import StatsEngineMCP, test_stats_mcp
        await test_stats_mcp()
    except Exception as e:
        print(f"❌ Error importando stats_engine_mcp: {e}")
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    asyncio.run(main())
