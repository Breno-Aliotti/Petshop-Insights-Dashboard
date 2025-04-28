import pandas as pd
import streamlit as st
from prophet import Prophet
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Previsão de Vendas", layout="wide")
st.title("Previsão de Vendas")
st.markdown("Utilize os dados históricos para prever o volume de vendas nos próximos meses.")

# --- Carregar dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("vendas_petshop_6anos.csv")
    df["Data da Venda"] = pd.to_datetime(df["Data da Venda"])
    return df

df = carregar_dados()

# --- Filtros ---
st.sidebar.header("Filtros")

# Tipo de Pet
with st.sidebar.expander("Tipo de Pet", expanded=True):
    todos_pets = sorted(df["Tipo de Pet"].unique())
    selecionar_todos_pets = st.checkbox("Selecionar todos", value=True, key="todos_pets")
    if selecionar_todos_pets:
        tipo_pet = st.multiselect("Tipo de Pet", todos_pets, default=todos_pets, disabled=True)
    else:
        tipo_pet = st.multiselect("Tipo de Pet", todos_pets)

# Categoria
with st.sidebar.expander("Categoria", expanded=True):
    todas_categorias = sorted(df["Categoria"].unique())
    selecionar_todas_categorias = st.checkbox("Selecionar todas", value=True, key="todas_categorias")
    if selecionar_todas_categorias:
        categoria = st.multiselect("Categoria", todas_categorias, default=todas_categorias, disabled=True)
    else:
        categoria = st.multiselect("Categoria", todas_categorias)

# Período
periodos = st.sidebar.slider("Meses para prever", 1, 24, 6)

# --- Filtrar dados ---
df_filtrado = df[
    (df["Tipo de Pet"].isin(tipo_pet)) &
    (df["Categoria"].isin(categoria))
]

# Verificar se tem coluna Quantidade
if "Quantidade" not in df_filtrado.columns:
    st.error("❌ Coluna 'Quantidade' não encontrada no dataset. Não é possível calcular a quantidade estimada para estoque.")
else:
    # Calcular preço médio por item no filtro aplicado
    df_filtrado = df_filtrado.copy()  # para evitar warning do pandas
    df_filtrado['Preco_medio'] = df_filtrado['Valor Total'] / df_filtrado['Quantidade']
    preco_medio = df_filtrado['Preco_medio'].mean()

    # Agrupar por mês
    df_mensal = df_filtrado.resample("MS", on="Data da Venda").sum(numeric_only=True).reset_index()
    df_mensal = df_mensal[["Data da Venda", "Valor Total", "Quantidade"]]
    df_mensal = df_mensal.rename(columns={"Data da Venda": "ds", "Valor Total": "y"})

    # Verificar dados
    if len(df_mensal) < 12:
        st.warning("⚠️ Poucos dados para previsão. Tente selecionar mais categorias ou tipos de pet.")
    else:
        # Criar e treinar modelo
        modelo = Prophet()
        modelo.fit(df_mensal[["ds", "y"]])

        # Criar datas futuras e prever
        futuro = modelo.make_future_dataframe(periods=periodos, freq='MS')
        previsao = modelo.predict(futuro)

        # Calcular quantidade prevista para estoque
        previsao['quantidade_prevista'] = previsao['yhat'] / preco_medio

        # Gráfico interativo
        fig = go.Figure()

        # Histórico
        fig.add_trace(go.Scatter(
            x=df_mensal["ds"],
            y=df_mensal["y"],
            mode="lines",
            name="Histórico (R$)",
            line=dict(color="gray", width=2),
            hovertemplate='Data: %{x|%b %Y}<br>Vendas: R$ %{y:,.2f}'
        ))

        # Previsão
        fig.add_trace(go.Scatter(
            x=previsao["ds"],
            y=previsao["yhat"],
            mode="lines",
            name="Previsão (R$)",
            line=dict(color="blue", width=3, dash='dot'),
            hovertemplate='Data: %{x|%b %Y}<br>Previsão: R$ %{y:,.2f}'
        ))

        # Layout
        fig.update_layout(
            title="Previsão de Vendas Mensais",
            xaxis_title="Data",
            yaxis_title="Valor em R$",
            template="plotly_white",
            hovermode="x unified",
            legend_title="Legenda"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Mostrar tabela com quantidade prevista
        st.markdown("### Tabela de Previsão com Quantidade Estimada para Estoque")
        st.dataframe(previsao[["ds", "yhat", "quantidade_prevista", "yhat_lower", "yhat_upper"]].tail(periodos).rename(columns={
            "ds": "Data",
            "yhat": "Previsão (R$)",
            "quantidade_prevista": "Quantidade Estimada",
            "yhat_lower": "Limite Inferior (R$)",
            "yhat_upper": "Limite Superior (R$)"
        }), use_container_width=True)