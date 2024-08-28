import datetime
import pandas as pd
import streamlit as st
import altair as alt

# Configurações iniciais do app
st.set_page_config(page_title="Gerenciador de Milhas", page_icon="✈️")
st.title("✈️ Gerenciador de Milhas")
st.write(
    """
    Este app permite gerenciar suas milhas de forma manual, registrando compras e vendas, 
    e analisando o lucro obtido por milha. 
    """
)

# Inicializa o DataFrame no estado da sessão
if "df" not in st.session_state:
    # Criação do DataFrame inicial com colunas básicas
    st.session_state.df = pd.DataFrame(columns=[
        "ID", "Tipo", "Quantidade", "Preço Total", "Preço por Milha", 
        "Data", "Lucro por Milha"
    ])

# Função para calcular o lucro por milha
def calcular_lucro_por_milha(preco_compra, preco_venda):
    return preco_venda - preco_compra

# Seção para adicionar transações
st.header("Adicionar Transação")

# Formulário para adicionar compras ou vendas
with st.form("form_transacao"):
    tipo = st.selectbox("Tipo de Transação", ["Compra", "Venda"])
    quantidade = st.number_input("Quantidade de Milhas", min_value=1, step=100)
    preco_total = st.number_input("Preço Total (R$)", min_value=0.0, step=0.01)
    data = st.date_input("Data da Transação", datetime.date.today())
    submit = st.form_submit_button("Registrar")

    if submit:
        # Cálculo do preço por milha
        preco_por_milha = preco_total / quantidade

        # Registro da transação no DataFrame
        novo_registro = {
            "ID": len(st.session_state.df) + 1,
            "Tipo": tipo,
            "Quantidade": quantidade,
            "Preço Total": preco_total,
            "Preço por Milha": preco_por_milha,
            "Data": data,
            "Lucro por Milha": None  # Lucro por milha é calculado na venda
        }

        # Adiciona o registro de compra ou venda
        st.session_state.df = pd.concat(
            [st.session_state.df, pd.DataFrame([novo_registro])],
            ignore_index=True
        )

        st.success(f"Transação de {tipo.lower()} registrada com sucesso!")

# Mostra o DataFrame de transações
st.header("Transações Registradas")
st.dataframe(st.session_state.df, use_container_width=True)

# Calcular lucro nas vendas registradas
st.header("Análise de Lucro")
if not st.session_state.df.empty:
    df_vendas = st.session_state.df[st.session_state.df["Tipo"] == "Venda"]

    for i, venda in df_vendas.iterrows():
        # Seleciona as compras anteriores à venda para calcular o lucro
        compras = st.session_state.df[
            (st.session_state.df["Tipo"] == "Compra") &
            (st.session_state.df["Data"] <= venda["Data"])
        ]

        if not compras.empty:
            preco_medio_compra = compras["Preço por Milha"].mean()
            lucro_por_milha = calcular_lucro_por_milha(preco_medio_compra, venda["Preço por Milha"])
            st.session_state.df.at[i, "Lucro por Milha"] = lucro_por_milha

    # Atualiza o DataFrame com o lucro calculado
    st.dataframe(st.session_state.df, use_container_width=True)

    # Gráfico de lucro por milha
    lucro_chart = alt.Chart(st.session_state.df).mark_bar().encode(
        x="Data:T",
        y="Lucro por Milha:Q",
        color="Tipo:N",
        tooltip=["ID", "Quantidade", "Preço Total", "Lucro por Milha"]
    ).properties(
        title="Lucro por Milha ao Longo do Tempo"
    )

    st.altair_chart(lucro_chart, use_container_width=True)
else:
    st.write("Nenhuma transação registrada ainda.")
