
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Monitor Reputacional 360°", layout="wide")
st.title("🧭 Monitor Reputacional 360°")

file_menciones = st.sidebar.file_uploader("📄 Archivo de menciones individuales (.xlsx)", type=["xlsx"])
file_scores = st.sidebar.file_uploader("📈 Archivo de puntuaciones agregadas (.xlsx)", type=["xlsx"])

if file_menciones and file_scores:
    df = pd.read_excel(file_menciones)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sentiment"] = df["Sentiment"].str.lower()
    df["s_i"] = df["Sentiment"].map({"positive": 1, "neutral": 0, "negative": -1}).fillna(0)

    score_df = pd.read_excel(file_scores)
    score_df["Fecha"] = pd.to_datetime(score_df["Fecha"])

    # Últimos datos
    latest = score_df.sort_values("Fecha").iloc[-1]
    dimensiones = [
        "Productos/Servicios", "Innovación", "Lugar de trabajo",
        "Gobernanza", "Ciudadanía", "Liderazgo", "Resultados financieros"
    ]
    scores = [latest.get(f"Score_{dim}", 50) for dim in dimensiones]
    global_score = latest.get("Close", 50)

    # Tarjetas
    max_score_idx = scores.index(max(scores))
    dimension_top = dimensiones[max_score_idx]
    dimension_val = scores[max_score_idx]
    dist_sent = df["Sentiment"].value_counts(normalize=True).reindex(["negative", "neutral", "positive"]).fillna(0) * 100

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🗂️ Comentarios Analizados", len(df))
    with col2:
        st.metric("📌 Dimensión destacada", dimension_top, delta=f"{dimension_val:.1f}")
    with col3:
        st.markdown("**🎯 Impacto del Sentimiento**")
        fig_dist = go.Figure(go.Bar(
            x=["Negativo", "Neutral", "Positivo"],
            y=[dist_sent["negative"], dist_sent["neutral"], dist_sent["positive"]],
            marker_color=["#FF6B6B", "#F4D03F", "#00C49F"]
        ))
        fig_dist.update_layout(height=200, margin=dict(t=10, b=10), yaxis_title="%", showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)

    # Rueda reputacional
    st.subheader("🌐 Rueda de Reputación RepTrak")
    labels = ["Reputación Global"] + dimensiones
    parents = [""] + ["Reputación Global"] * len(dimensiones)
    values = [sum(scores)] + scores
    colors = ["#00C49F", "#F5A623", "#50E3C2", "#4A90E2", "#BD10E0", "#7ED321", "#F8E71C", "#D0021B"][:len(scores)+1]
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="remainder",
        marker=dict(colors=colors),
        hovertemplate='<b>%{label}</b><br>Score: %{value}<extra></extra>',
        textinfo="label+percent entry",
        insidetextorientation="radial"
    ))
    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        height=500,
        annotations=[
            dict(
                text=f"<b>{global_score:.1f}</b><br><span style='font-size:14px'>{'Strong' if global_score >= 60 else 'Weak'}</span>",
                showarrow=False,
                font=dict(size=20, color="white"),
                align="center",
                x=0.5, y=0.5, xanchor="center", yanchor="middle",
                xref="paper", yref="paper",
                bgcolor="#00C49F",
                borderpad=4
            )
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

    # Evolución reputacional con velas
    st.subheader("📉 Evolución Reputacional (Velas OHLC)")
    fig_ohlc = go.Figure(go.Candlestick(
        x=score_df["Fecha"],
        open=score_df["Open"],
        high=score_df["High"],
        low=score_df["Low"],
        close=score_df["Close"],
        increasing_line_color="#00C49F", decreasing_line_color="#FF6B6B"
    ))
    fig_ohlc.update_layout(
        height=400,
        margin=dict(t=30),
        xaxis_title="Fecha",
        yaxis_title="Puntaje",
        showlegend=False
    )
    st.plotly_chart(fig_ohlc, use_container_width=True)

    # Menciones filtradas por fecha
    st.subheader("📆 Menciones que impactaron la reputación")
    fechas_disponibles = sorted(df["Date"].dt.date.unique())
    fecha_seleccionada = st.selectbox("Selecciona una fecha para ver menciones", fechas_disponibles)
    menciones_dia = df[df["Date"].dt.date == fecha_seleccionada]
    st.dataframe(menciones_dia[["Date", "Title", "Sentiment", "s_i"]].sort_values("s_i", ascending=True))
else:
    st.warning("Por favor, sube ambos archivos para iniciar el análisis.")
