
# 📊 Dashboard Reputacional Grupo Éxito

Este proyecto permite visualizar y explorar la reputación digital de Grupo Éxito a partir de datos procesados y menciones individuales.

## 🧩 ¿Qué incluye el dashboard?

- 🧭 Radar con puntuaciones por dimensión RepTrak
- 📈 Velas japonesas con la evolución diaria de la reputación
- 📋 Tabla de menciones con búsqueda y filtros
- 🔝 Menciones más influyentes positivas y negativas

## 🚀 ¿Cómo usarlo?

1. Sube los siguientes archivos desde tu equipo:
   - `Grupo Exito Limpieza v1.xlsx` → Menciones individuales con sentimiento y dimensión
   - `resultado_reputacional.xlsx` → Scores globales y por dimensión + OHLC

2. El dashboard calculará automáticamente:
   - Engagement, influencia y peso por fuente
   - Impacto Ponderado (IP_i) y Score individual

## ⚙️ Requisitos

Instala las dependencias:
```
pip install -r requirements.txt
```

## ▶️ Ejecutar localmente

```
streamlit run dashboard_reputacional_completo.py
```

---

Desarrollado por: *Monastery IA + ChatGPT*
