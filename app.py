import math
import pandas as pd
import streamlit as st

# -------------------------------------------------------
# Configurações básicas da página
# -------------------------------------------------------
st.set_page_config(
    page_title="Calculadora de Funil Reverso",
    page_icon="📈",
    layout="centered"
)

# -------------------------------------------------------
# Cabeçalho
# -------------------------------------------------------
st.title("📈 Calculadora de Funil Reverso")

st.markdown("Preencha os dados e descubra quantos **leads** e qual **CPL máximo** você pode pagar na sua campanha.")


st.markdown("---")

# -------------------------------------------------------
# Inputs centrais (um abaixo do outro)
# -------------------------------------------------------
st.subheader("Parâmetros do funil")

faturamento_desejado = st.number_input(
    "Faturamento desejado (R$)",
    min_value=1000.0,
    step=1000.0,
    value=150_000.0,
    format="%.2f"
)

orcamento_midia = st.number_input(
    "Investimento em tráfego (R$)",
    min_value=0.0,
    step=1000.0,
    value=25_000.0,
    format="%.2f"
)

ticket_medio = st.number_input(
    "Ticket médio por venda (R$)",
    min_value=1.0,
    step=10.0,
    value=247.90,
    format="%.2f"
)

taxa_conv_realista = st.number_input(
    "Taxa de conversão realista (leads → vendas) (%)",
    min_value=0.1,
    max_value=100.0,
    step=0.1,
    value=4.0,
    format="%.2f"
)

st.markdown("---")

# -------------------------------------------------------
# Lógica de cálculo
# -------------------------------------------------------
if ticket_medio <= 0:
    st.error("Define um ticket médio maior que zero pra começar.")
elif faturamento_desejado <= 0:
    st.error("Define um faturamento desejado maior que zero.")
else:
    # Vendas necessárias (arredonda pra cima)
    vendas_necessarias = math.ceil(faturamento_desejado / ticket_medio)

    cenarios = {
        "Pessimista": 0.7,
        "Realista": 1.0,
        "Otimista": 1.3,
    }

    resultados = []

    for nome_cenario, fator in cenarios.items():
        taxa_conv = taxa_conv_realista * fator
        taxa_conv = max(min(taxa_conv, 100.0), 0.01)  # trava entre 0.01% e 100%

        taxa_conv_decimal = taxa_conv / 100
        leads_necessarios = math.ceil(vendas_necessarias / taxa_conv_decimal)

        # CPL máximo em função do investimento informado
        if orcamento_midia > 0 and leads_necessarios > 0:
            cpl_maximo = orcamento_midia / leads_necessarios
        else:
            cpl_maximo = 0.0

        resultados.append({
            "Cenário": nome_cenario,
            "Taxa de conversão (%)": round(taxa_conv, 2),
            "Vendas necessárias": vendas_necessarias,
            "Leads necessários": leads_necessarios,
            "CPL máximo (R$)": cpl_maximo,
        })

    df_resultados = pd.DataFrame(resultados).set_index("Cenário")

    # ---------------------------------------------------
    # Resumo do cenário realista (funil reverso "base")
    # ---------------------------------------------------
    st.subheader("Resumo do cenário realista")

    linha_realista = df_resultados.loc["Realista"]

    col_v, col_l, col_cpl, col_roas = st.columns(4)

    with col_v:
        st.metric(
            label="Vendas necessárias",
            value=f"{int(linha_realista['Vendas necessárias']):,}".replace(",", ".")
        )

    with col_l:
        st.metric(
            label="Leads necessários",
            value=f"{int(linha_realista['Leads necessários']):,}".replace(",", ".")
        )

    with col_cpl:
        st.metric(
            label="CPL máximo (realista)",
            value=(
                f"R$ {linha_realista['CPL máximo (R$)']:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
        )

    with col_roas:
        if orcamento_midia > 0:
            roas = faturamento_desejado / orcamento_midia
            st.metric(
                label="ROAS esperado",
                value=f"{roas:.2f}x"
            )
        else:
            st.metric(
                label="ROAS esperado",
                value="–"
            )

    # ---------------------------------------------------
    # Cenários comparativos
    # ---------------------------------------------------
    st.subheader("Cenários pessimista, realista e otimista")

    col_p, col_r, col_o = st.columns(3)

    for col, nome, emoji in zip(
        [col_p, col_r, col_o],
        ["Pessimista", "Realista", "Otimista"],
        ["🟥", "🟨", "🟩"]
    ):
        linha = df_resultados.loc[nome]
        with col:
            st.markdown(f"### {emoji} {nome}")
            st.metric(
                label="Leads necessários",
                value=f"{int(linha['Leads necessários']):,}".replace(",", ".")
            )
            st.metric(
                label="CPL máximo",
                value=(
                    f"R$ {linha['CPL máximo (R$)']:,.2f}"
                    .replace(",", "X").replace(".", ",").replace("X", ".")
                )
            )
            st.caption(
                f"Taxa de conversão: {linha['Taxa de conversão (%)']:.2f}%"
            )

    # ---------------------------------------------------
    # Tabela completa
    # ---------------------------------------------------
    st.subheader("Detalhamento dos cenários")

    df_exibicao = df_resultados.copy()

    # Formatações
    df_exibicao["Taxa de conversão (%)"] = df_exibicao["Taxa de conversão (%)"].map(
        lambda x: f"{x:.2f}%"
    )

    df_exibicao["Vendas necessárias"] = df_exibicao["Vendas necessárias"].map(
        lambda x: f"{int(x):,}".replace(",", ".")
    )

    df_exibicao["Leads necessários"] = df_exibicao["Leads necessários"].map(
        lambda x: f"{int(x):,}".replace(",", ".")
    )

    df_exibicao["CPL máximo (R$)"] = df_exibicao["CPL máximo (R$)"].map(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.dataframe(
        df_exibicao,
        use_container_width=True,
    )
