
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

    # Engagement combinado y normalizado
    df["Engagement"] = df[[
        "Instagram Likes", "Instagram Comments", "Instagram Shares",
        "Tiktok Likes", "Tiktok Comments", "Tiktok Shares"
    ]].fillna(0).sum(axis=1)

    df["Engagement"] = df["Engagement"] / df["Engagement"].max()

    # Influencia y fuente (si faltan columnas)
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

    # Radar de dimensiones
    radar_cols = [col for col in score_df.columns if col.startswith("Score_")]
    radar_df = score_df[["Fecha"] + radar_cols].copy()
    latest = radar_df.sort_values("Fecha").iloc[-1]
    radar_data = pd.DataFrame({
        "Dimensión": [col.replace("Score_", "") for col in radar_cols],
        "Score": [latest[col] for col in radar_cols]
    })

    fig_radar = px.line_polar(radar_data, r="Score", theta="Dimensión", line_close=True,
                              template="plotly_white", title="🧭 Reputación por Dimensión")
    fig_radar.update_traces(fill='toself', line_color="#00C49F")
    st.plotly_chart(fig_radar, use_container_width=True)

    # Velas japonesas
    fig_candle = go.Figure(data=[go.Candlestick(
        x=score_df["Fecha"],
        open=score_df["Open"],
        high=score_df["High"],
        low=score_df["Low"],
        close=score_df["Close"],
        increasing_line_color='#00C49F',
        decreasing_line_color='#FF6B6B'
    )])
    fig_candle.update_layout(title="📈 Evolución Reputacional (Velas OHLC)",
                             xaxis_title="Fecha", yaxis_title="GlobalScore")
    st.plotly_chart(fig_candle, use_container_width=True)

    # Tabla de menciones
    st.subheader("📋 Menciones filtrables")
    with st.expander("Ver todas las menciones"):
        st.dataframe(df[["Date", "Title", "Snippet", "Dimensión", "Sentiment", "Score_i"]])
else:
    st.info("Por favor, sube ambos archivos para iniciar el análisis.")
