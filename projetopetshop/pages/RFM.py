import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configurações da página
st.set_page_config(page_title="RFM - Clientes", layout="wide", page_icon="🧠")

# --- Carregar dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("vendas_petshop_6anos.csv")
    df["Data da Venda"] = pd.to_datetime(df["Data da Venda"])
    return df

df = carregar_dados()
data_ref = df["Data da Venda"].max()

# --- Calcular RFM ---
rfm = df.groupby("ID do Cliente").agg({
    "Data da Venda": lambda x: (data_ref - x.max()).days,
    "ID do Cliente": "count",
    "Valor Total": "sum"
}).rename(columns={
    "Data da Venda": "Recencia",
    "ID do Cliente": "Frequencia",
    "Valor Total": "Valor"
}).reset_index()

# Atribuir scores (1 a 5)
rfm["R_Score"] = pd.qcut(rfm["Recencia"], 5, labels=[5, 4, 3, 2, 1])
rfm["F_Score"] = pd.qcut(rfm["Frequencia"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["M_Score"] = pd.qcut(rfm["Valor"], 5, labels=[1, 2, 3, 4, 5])

# Converter para inteiro
rfm["R"] = rfm["R_Score"].astype(int)
rfm["F"] = rfm["F_Score"].astype(int)
rfm["M"] = rfm["M_Score"].astype(int)

# --- Criar segmentos claros ---
def segmentar_cliente(row):
    if row["R"] >= 4 and row["F"] >= 4 and row["M"] >= 4:
        return "Top Cliente 💎"
    elif row["R"] >= 4 and row["F"] >= 3:
        return "Cliente Frequente 🔁"
    elif row["R"] >= 4:
        return "Cliente Recente 🕒"
    elif row["F"] >= 4:
        return "Cliente Leal ❤️"
    elif row["M"] >= 4:
        return "Cliente Valioso 💰"
    else:
        return "Cliente em Risco ⚠️"

rfm["Segmento"] = rfm.apply(segmentar_cliente, axis=1)

# --- Layout da Página ---
st.title("Análise de Clientes - RFM")
st.markdown("Segmentação de clientes com base em **Recência**, **Frequência** e **Valor Monetário**.")

# --- KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total de Clientes", f"{rfm.shape[0]:,}")
col2.metric("Top Clientes 💎", rfm[rfm["Segmento"] == "Top Cliente 💎"].shape[0])
col3.metric("Clientes em Risco ⚠️", rfm[rfm["Segmento"] == "Cliente em Risco ⚠️"].shape[0])

# --- Gráfico de barras: Quantidade de clientes por segmento ---
st.markdown("### Quantidade de Clientes por Segmento")

segmentos = rfm["Segmento"].value_counts().reset_index()
segmentos.columns = ["Segmento", "Quantidade"]

fig_barras = px.bar(
    segmentos,
    x="Segmento",
    y="Quantidade",
    color="Segmento",
    text="Quantidade",
    title="Distribuição de Clientes por Segmento",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_barras.update_layout(
    xaxis_title="Segmento",
    yaxis_title="Número de Clientes",
    showlegend=False,
    template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"
)

st.plotly_chart(fig_barras, use_container_width=True)

# --- Gráfico de pizza (opcional) ---
st.markdown("### Proporção de Clientes por Segmento")

fig_pizza = px.pie(
    segmentos,
    values="Quantidade",
    names="Segmento",
    title="Proporção de Clientes por Segmento",
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4
)

st.plotly_chart(fig_pizza, use_container_width=True)

# --- Tabela interativa
st.markdown("### Tabela de Clientes Segmentados")
st.dataframe(rfm.sort_values(by="Segmento", ascending=False), use_container_width=True)