#!/bin/bash
echo "🔧 Corrigiendo umbrales de probabilidad de 55% a 50%..."

# Archivos a revisar
FILES=(
    "modules/parlay_generator.py"
    "modules/smart_betting_ai.py"
    "modules/advanced_market_reasoning.py"
    "main_vision.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📝 Procesando $file..."
        # Crear backup
        cp "$file" "${file}.bak"
        # Reemplazar 55% por 50% en contexto de probabilidades
        sed -i 's/\(prob\|probability\).*55[^0-9]/50/g' "$file"
        sed -i 's/\([>=<]\s*\)55\s*\([^0-9]\)/\150\2/g' "$file"
        sed -i 's/\([0-9.]*\)55\([0-9.]*\)/\150\2/g' "$file"
        echo "✅ $file actualizado"
    fi
done

echo ""
echo "🔍 Verificando cambios en parlay_generator.py:"
grep -n "55\|50" modules/parlay_generator.py | head -10
