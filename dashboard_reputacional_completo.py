
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Monitor Reputacional 360°", layout="wide")

st.title("🧭 Monitor Reputacional 360°")

# Subida de archivos
file_menciones = st.sidebar.file_uploader("📄 Archivo de menciones individuales (.xlsx)", type=["xlsx"])
file_scores = st.sidebar.file_uploader("📈 Archivo de puntuaciones agregadas (.xlsx)", type=["xlsx"])

if file_menciones and file_scores:
    df = pd.read_excel(file_menciones)
    score_df = pd.read_excel(file_scores)

    # Preprocesamiento
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sentiment"] = df["Sentiment"].str.lower()

    # Sentimiento numérico
    sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
    df["s_i"] = df["Sentiment"].map(sentiment_map).fillna(0)

    # Calcular distribución de sentimiento
    sentimiento_dist = df["Sentiment"].value_counts(normalize=True).reindex(["negative", "neutral", "positive"]).fillna(0) * 100

    # Último registro de score
    latest = score_df.sort_values("Fecha").iloc[-1]

    # Dimensiones esperadas
    dimensiones = [
        "Productos/Servicios", "Innovación", "Lugar de trabajo",
        "Gobernanza", "Ciudadanía", "Liderazgo", "Resultados financieros"
    ]

    scores = [latest.get(f"Score_{dim}", 50) for dim in dimensiones]
    max_score_idx = scores.index(max(scores))
    dimension_top = dimensiones[max_score_idx]
    dimension_val = scores[max_score_idx]
    global_score = latest.get("Close", 50)

    # === LAYOUT EN COLUMNA ===
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("🗂️ Comentarios Analizados", len(df))

    with c2:
        st.metric(f"📌 Dimensión destacada", f"{dimension_top}", delta=f"{dimension_val:.1f}")

    with c3:
        st.markdown("**🎯 Impacto del Sentimiento**")
        fig_dist = go.Figure(go.Bar(
            x=["Negativo", "Neutral", "Positivo"],
            y=[sentimiento_dist["negative"], sentimiento_dist["neutral"], sentimiento_dist["positive"]],
            marker_color=["#FF6B6B", "#F4D03F", "#00C49F"]
        ))
        fig_dist.update_layout(height=200, margin=dict(t=10, b=10), yaxis_title="%", showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)

    # === RUEDA REPUTACIONAL ===
    st.subheader("🌐 Rueda de Reputación RepTrak")
    colors = ["#F5A623", "#50E3C2", "#4A90E2", "#BD10E0", "#7ED321", "#F8E71C", "#D0021B"]

    fig_sunburst = go.Figure(go.Sunburst(
        labels=["Reputación Score"] + dimensiones,
        parents=[""] + ["Reputación Score"] * len(dimensiones),
        values=[1] + [1] * len(dimensiones),
        branchvalues="total",
        marker=dict(colors=["#00C49F"] + colors),
        hovertemplate='<b>%{label}</b><br>Score: %{customdata}<extra></extra>',
        customdata=[f"{global_score:.1f}"] + [f"{s:.1f}" for s in scores],
        textinfo="label",
        insidetextorientation='radial'
    ))

    fig_sunburst.add_trace(go.Scatterpolar(
        r=[0],
        theta=[0],
        mode='text',
        text=[f"<b>{global_score:.1f}</b><br>Strong" if global_score >= 60 else "<b>{global_score:.1f}</b><br>Weak"],
        textfont=dict(size=18),
        hoverinfo='skip',
        showlegend=False
    ))

    fig_sunburst.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=500)
    st.plotly_chart(fig_sunburst, use_container_width=True)

else:
    st.warning("Por favor, sube los dos archivos para continuar.")
