
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Reputacional - Grupo Éxito", layout="wide")

st.title("📊 Monitor Reputacional con Análisis de Menciones")

# Subir archivos
st.sidebar.header("Sube tus archivos")
file_menciones = st.sidebar.file_uploader("📄 Archivo de menciones individuales (.xlsx)", type=["xlsx"])
file_scores = st.sidebar.file_uploader("📈 Archivo de puntuaciones agregadas (.xlsx)", type=["xlsx"])

if file_menciones and file_scores:
    df = pd.read_excel(file_menciones)
    score_df = pd.read_excel(file_scores)

    st.success("Archivos cargados correctamente.")

    # Preprocesamiento menciones
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sentiment"] = df["Sentiment"].str.lower()

    # Sentimiento numérico
    sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
    df["s_i"] = df["Sentiment"].map(sentiment_map).fillna(0)

    # Engagement combinado y normalizado (robusto)
    engagement_cols = [
        "Instagram Likes", "Instagram Comments", "Instagram Shares",
        "Tiktok Likes", "Tiktok Comments", "Tiktok Shares"
    ]
    engagement_cols = [col for col in engagement_cols if col in df.columns]

    if engagement_cols:
        df["Engagement"] = df[engagement_cols].fillna(0).sum(axis=1)
        df["Engagement"] = df["Engagement"] / df["Engagement"].max()
    else:
        df["Engagement"] = 1

    # Influencia y fuente
    if "Impact" in df.columns:
        df["inf_i"] = df["Impact"] / df["Impact"].max()
    else:
        df["inf_i"] = 1

    fuente_pesos = {
        "news": 1.0,
        "blog": 0.7,
        "forum": 0.5,
        "twitter": 0.6,
        "instagram": 0.8,
        "tiktok": 0.9
    }

    df["w_f_i"] = df["Page Type"].str.lower().map(fuente_pesos).fillna(0.5)

    # Calcular IP_i y Score_i
    df["IP_i"] = (1 + df["s_i"].abs()) * df["inf_i"] * df["Engagement"] * df["w_f_i"]
    df["Score_i"] = df["s_i"] * df["IP_i"]

    # Menciones destacadas
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔝 Mención más positiva e influyente")
        top_pos = df[df["s_i"] > 0].sort_values(by="IP_i", ascending=False).head(1)
        st.write(top_pos[["Date", "Title", "Snippet", "Dimensión", "Sentiment", "IP_i"]])

    with col2:
        st.subheader("🔻 Mención más negativa e influyente")
        top_neg = df[df["s_i"] < 0].sort_values(by="IP_i", ascending=False).head(1)
        st.write(top_neg[["Date", "Title", "Snippet", "Dimensión", "Sentiment", "IP_i"]])

    st.markdown("---")

    # Rueda reputacional estilo sunburst
    st.subheader("🧭 Rueda de Reputación RepTrak")
    dimensiones = [
        "Productos/Servicios", "Innovación", "Lugar de trabajo",
        "Gobernanza", "Ciudadanía", "Liderazgo", "Resultados financieros"
    ]
    colors = ["#F5A623", "#50E3C2", "#4A90E2", "#BD10E0", "#7ED321", "#F8E71C", "#D0021B"]
    latest_row = score_df.sort_values("Fecha").iloc[-1]
    scores = [latest_row.get(f"Score_{dim}", 50) for dim in dimensiones]

    fig_sunburst = go.Figure(go.Sunburst(
        labels=["Reputación Global"] + dimensiones,
        parents=[""] + ["Reputación Global"] * len(dimensiones),
        values=[sum(scores)] + scores,
        branchvalues="total",
        marker=dict(colors=["#00C49F"] + colors),
        hovertemplate='<b>%{label}</b><br>Score: %{value}<extra></extra>',
        textinfo="label+value",
        insidetextorientation='radial'
    ))
    fig_sunburst.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=500)
    st.plotly_chart(fig_sunburst, use_container_width=True)

    st.subheader("📈 Evolución Reputacional (Velas OHLC)")
    selected_date = st.selectbox("Selecciona una fecha para ver menciones:", score_df["Fecha"].dt.date.unique())
    fig_candle = go.Figure(data=[go.Candlestick(
        x=score_df["Fecha"],
        open=score_df["Open"],
        high=score_df["High"],
        low=score_df["Low"],
        close=score_df["Close"],
        increasing_line_color='#00C49F',
        decreasing_line_color='#FF6B6B'
    )])
    fig_candle.update_layout(xaxis_title="Fecha", yaxis_title="GlobalScore")
    st.plotly_chart(fig_candle, use_container_width=True)

    # Menciones de la fecha seleccionada
    st.subheader("💬 Menciones que afectan la fecha seleccionada")
    menciones_dia = df[df["Date"].dt.date == selected_date]
    st.dataframe(menciones_dia[["Date", "Title", "Snippet", "Dimensión", "Sentiment", "Score_i"]])
else:
    st.info("Por favor, sube ambos archivos para iniciar el análisis.")
