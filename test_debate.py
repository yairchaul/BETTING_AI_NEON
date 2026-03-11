"""
PRUEBA RÁPIDA DEL DEBATE MULTI-AGENTE
"""
from multi_agent import MultiAgentDebate
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("🤖 PRUEBA DE DEBATE MULTI-AGENTE")
print("="*60)

# Verificar keys
print(f"\n🔑 CLAUDE Key: {'✅ Configurada' if os.getenv('ANTHROPIC_API_KEY') else '❌ No configurada'}")
print(f"🔑 GPT Key: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') else '❌ No configurada'}")

# Crear picks de prueba
picks_prueba = [
    {
        'partido': 'Real Madrid vs Manchester City',
        'liga': 'UEFA Champions League',
        'desc': 'Over 2.5 goles',
        'prob': 0.72,
        'cuota': 1.85,
        'value': 0.33,
        'nivel': 3,
        'gf_local': 2.4,
        'gf_visit': 2.1
    },
    {
        'partido': 'Liverpool vs Arsenal',
        'liga': 'Premier League',
        'desc': 'Ambos anotan',
        'prob': 0.68,
        'cuota': 1.90,
        'value': 0.29,
        'nivel': 2,
        'gf_local': 2.5,
        'gf_visit': 2.2
    },
    {
        'partido': 'Bayern Munich vs Atalanta',
        'liga': 'UEFA Champions League',
        'desc': 'Bayern gana',
        'prob': 0.75,
        'cuota': 1.35,
        'value': 0.01,
        'nivel': 5,
        'gf_local': 2.8,
        'gf_visit': 1.8
    }
]

# Iniciar debate
print("\n🤔 Iniciando debate entre agentes...")
debate = MultiAgentDebate()
print(f"📊 Agentes disponibles: {len(debate.agentes)}")

for agente in debate.agentes:
    print(f"  - {agente.nombre}")

print("\n" + "="*60)

# Debatir cada pick
for i, pick in enumerate(picks_prueba):
    print(f"\n🎯 DEBATE #{i+1}: {pick['partido']}")
    print(f"   Pick: {pick['desc']}")
    print(f"   Prob: {pick['prob']*100:.1f}% | Cuota: {pick['cuota']:.2f} | Value: {pick['value']*100:.1f}%")
    
    resultado = debate.debatir_pick(pick, {})
    
    print(f"\n   📢 RESULTADO DEL DEBATE:")
    print(f"      Decisión: {resultado['decision']}")
    print(f"      Confianza: {resultado['confianza']:.1f}%")
    print(f"      Votos: {resultado['votos_favor']} a favor, {resultado['votos_contra']} en contra")
    print(f"      Justificación: {resultado['justificacion']}")
    
    if 'opiniones' in resultado:
        print(f"\n      Opiniones individuales:")
        for o in resultado['opiniones']:
            emoji = "👍" if o['opinion'] == 'FAVORABLE' else "👎" if o['opinion'] == 'DESFAVORABLE' else "🤷"
            print(f"        {emoji} {o['agente']}: {o['justificacion']} ({o['confianza']}%)")
    
    print("-" * 40)

print("\n✅ PRUEBA COMPLETADA")
