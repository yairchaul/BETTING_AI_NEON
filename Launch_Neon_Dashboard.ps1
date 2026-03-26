# Script para lanzar el Dashboard de Betting AI Neon Edition
Write-Host "🚀 INICIANDO BETTING AI: NEON EDITION..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar que existe el archivo principal
if (Test-Path "main_vision_completo.py") {
    Write-Host "✅ Archivo principal encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ No se encuentra main_vision_completo.py" -ForegroundColor Red
    exit
}

# Verificar base de datos
if (Test-Path "data/betting_stats.db") {
    Write-Host "✅ Base de datos encontrada" -ForegroundColor Green
} else {
    Write-Host "⚠️ Base de datos no encontrada. Ejecuta primero el scraper." -ForegroundColor Yellow
}

# Ejecutar Streamlit
Write-Host "🎨 Cargando interfaz visual neón..." -ForegroundColor Magenta
streamlit run main_vision_completo.py
