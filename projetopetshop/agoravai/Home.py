import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Configurações da página
st.set_page_config(page_title="Dashboard Petshop", layout="wide")

# --- Carregar dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("vendas_petshop_6anos.csv")
    df["Data da Venda"] = pd.to_datetime(df["Data da Venda"])
    df["Ano"] = df["Data da Venda"].dt.year
    df["Mês"] = df["Data da Venda"].dt.month
    return df

df = carregar_dados()

# --- Sidebar ---
st.sidebar.title("Filtros")
modo_visualizacao = st.sidebar.radio("Modo de visualização", ["Todos os anos", "Ano específico"])

anos_disponiveis = sorted(df["Ano"].unique())
ano_selecionado = st.sidebar.selectbox("Selecione o ano", anos_disponiveis, index=len(anos_disponiveis)-1)

# Aplicar filtros
if modo_visualizacao == "Ano específico":
    df = df[df["Ano"] == ano_selecionado]

# --- KPIs ---
receita_total = df["Valor Total"].sum()
ticket_medio = df["Valor Total"].mean()
total_vendas = df.shape[0]

# --- Título ---
st.title("Dashboard de Vendas - Petshop")
st.markdown("Análise interativa das vendas dos últimos 6 anos.\n")

# --- KPIs em colunas ---
col1, col2, col3 = st.columns(3)
col1.metric("Receita Total", f"R$ {receita_total:,.2f}")
col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("Total de Vendas", f"{total_vendas:,}")

# --- Gráficos ---

st.markdown("### Receita por Mês")
receita_mes = df.groupby("Mês")["Valor Total"].sum().reset_index()
fig_receita_mes = px.bar(
    receita_mes,
    x="Mês",
    y="Valor Total",
    labels={"Valor Total": "Receita (R$)", "Mês": "Mês"},
    color="Valor Total",
    color_continuous_scale="Blues",
)
st.plotly_chart(fig_receita_mes, use_container_width=True)

st.markdown("### Top 10 Produtos Mais Vendidos")
top_produtos = df.groupby("Produto")["Quantidade"].sum().sort_values(ascending=False).head(10).reset_index()
fig_top_produtos = px.bar(
    top_produtos,
    x="Quantidade",
    y="Produto",
    orientation="h",
    color="Quantidade",
    color_continuous_scale="Oranges",
)
fig_top_produtos.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_top_produtos, use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown("### Receita por Categoria")
    receita_categoria = df.groupby("Categoria")["Valor Total"].sum().reset_index()
    fig_categoria = px.pie(
        receita_categoria,
        values="Valor Total",
        names="Categoria",
        color_discrete_sequence=px.colors.sequential.RdBu,
        hole=0.4
    )
    st.plotly_chart(fig_categoria, use_container_width=True)

with col5:
    st.markdown("### Receita por Tipo de Pet")
    receita_pet = df.groupby("Tipo de Pet")["Valor Total"].sum().reset_index()
    fig_pet = px.bar(
        receita_pet,
        x="Tipo de Pet",
        y="Valor Total",
        color="Tipo de Pet",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_pet, use_container_width=True)

# --- Tabela final ---
with st.expander("Ver dados brutos"):
    st.dataframe(df)