import pandas as pd
import streamlit as st
from src.services.streamlit_service import (
    generate_ai_summary,
    generate_area_comparison,
    generate_comparison_chart,
    load_data,
)

# Configuração inicial da página
st.set_page_config(
    page_title="Análise ENEM: Internet e Desempenho",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título e introdução
st.title("📊 Impacto do Acesso à Internet no Desempenho do ENEM")
st.markdown(
    """
Esta análise investiga se estudantes sem acesso à internet em casa têm desempenho significativamente inferior no ENEM, mesmo quando consideramos o nível de renda familiar.
"""
)

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Sidebar com filtros
st.sidebar.header("⚙️ Configurações Rápidas")

# Controles
AREA_OPTIONS = {
    "Média Geral": "NU_NOTA_MEDIA",
    "Ciências da Natureza": "NU_NOTA_CN",
    "Ciências Humanas": "NU_NOTA_CH",
    "Linguagens": "NU_NOTA_LC",
    "Matemática": "NU_NOTA_MT",
    "Redação": "NU_NOTA_REDACAO",
}

selected_area = st.sidebar.selectbox(
    "Área de Análise:", list(AREA_OPTIONS.keys()), index=0
)

chart_type = st.sidebar.radio(
    "Tipo de Gráfico:",
    ("Boxplot Simplificado", "Histograma Agregado", "Médias Comparadas"),
    index=0,
)


# Layout principal
tab1, tab2, tab3 = st.tabs(
    ["📊 Análise Principal", "📈 Comparação entre Áreas", "ℹ️ Sobre o Projeto"]
)

with tab1:
    st.header(f"Análise de {selected_area}")

    # Gráfico principal com loader
    with st.spinner("Gerando visualização..."):
        chart = generate_comparison_chart(
            df, AREA_OPTIONS[selected_area], chart_type, selected_area
        )
        st.plotly_chart(chart, use_container_width=True)

    # Métricas rápidas
    st.subheader("Principais Estatísticas")

    col1, col2, col3 = st.columns(3)
    with col1:
        mean_with = df[df["INTERNET"] == "Tem internet em casa"][
            AREA_OPTIONS[selected_area]
        ].mean()
        st.metric("Média com Internet", f"{mean_with:.1f}")

    with col2:
        mean_without = df[df["INTERNET"] == "Não tem internet em casa"][
            AREA_OPTIONS[selected_area]
        ].mean()
        st.metric("Média sem Internet", f"{mean_without:.1f}")

    with col3:
        diff = mean_with - mean_without
        st.metric("Diferença", f"{diff:.1f}", f"{(diff/mean_without*100):.1f}%")

    # Seção de sumário por IA
    st.subheader("📝 Sumário Analítico (IA Generativa)")

    # Pré-agrega os dados para o sumário
    summary_data = df.groupby("INTERNET", observed=True)[
        AREA_OPTIONS[selected_area]
    ].describe()

    if st.button("Gerar Sumário Automático"):
        with st.spinner("Gerando sumário com IA..."):
            ai_summary = generate_ai_summary(summary_data, selected_area, chart_type)
            st.markdown(f"**Sumário:**\n\n{ai_summary}")

            # Opção para copiar o sumário
            if st.button("Copiar Análise"):
                st.clipboard(ai_summary)


with tab2:
    st.header("Comparação entre Áreas do Conhecimento")

    with st.spinner("Gerando comparação entre áreas..."):
        area_chart = generate_area_comparison(df, AREA_OPTIONS)
        st.plotly_chart(area_chart, use_container_width=True)

    # Tabela resumida otimizada
    st.subheader("Dados Resumidos por Área")

    summary_data = []
    for area_name, area_col in AREA_OPTIONS.items():
        if area_name == "Média Geral":
            continue
        group_stats = df.groupby("INTERNET", observed=True)[area_col].agg(
            ["mean", "median", "std"]
        )
        group_stats["Área"] = area_name
        summary_data.append(group_stats.reset_index())

    summary_df = pd.concat(summary_data)
    st.dataframe(
        summary_df.pivot(index="Área", columns="INTERNET", values=["mean", "median"]),
        use_container_width=True,
    )

    # Sumário por IA para comparação entre áreas
    st.subheader("📝 Análise Comparativa (IA Generativa)")

    if st.button("Gerar Análise Comparativa"):
        with st.spinner("Gerando análise com IA..."):
            # Pré-agrega dados comparativos
            comparison_data = summary_df.groupby("Área").agg(
                {"mean": ["max", "min", "mean"], "median": ["max", "min"]}
            )

            ai_comparison = generate_ai_summary(
                comparison_data, "Comparação entre Áreas", "Tabela Comparativa"
            )
            st.markdown(f"**Análise Comparativa:**\n\n{ai_comparison}")

            # Opção para copiar a análise
            if st.button("Copiar Análise"):
                st.clipboard(ai_comparison)


with tab3:
    st.header("Sobre o Projeto")

    st.markdown(
        """
    ### Objetivo
    Esta análise investiga se estudantes sem acesso à internet em casa têm desempenho significativamente inferior 
    no ENEM, mesmo quando consideramos o nível de renda familiar.
    
    ### Metodologia
    - **Fonte de dados**: Microdados do ENEM (INEP)
    - **Amostra**: 100.000 participantes (exemplo)
    - **Variáveis analisadas**:
      - Notas por área do conhecimento
      - Acesso à internet em casa (Q025)
      - Renda familiar (Q006)
    
    ### Limitações
    - Análise correlacional, não causal
    - Não controla por todas as variáveis de confusão
    - Dados são ilustrativos (substitua pelo seu dataframe real)
    
    ### Próximos Passos
    - Adicionar mais variáveis de controle
    - Analisar dados de múltiplos anos
    - Implementar modelos estatísticos mais sofisticados
    """
    )

    st.markdown(
        """
    **Desenvolvido por**: [Matheus Fabião](https://github.com/matheusfabiao)  
    **Fonte dos dados**: [INEP/MEC](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) 
    **Tecnologias utilizadas**: Python, Pandas, Plotly, Streamlit, OpenAI API
    """
    )

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**Dicas de Uso**:
- Comece pela análise geral
- Experimente diferentes tipos de gráfico
- Compare entre áreas do conhecimento
"""
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**Feito por:** [Matheus Fabião](https://github.com/matheusfabiao)  
**Fonte dos dados:** [INEP/MEC](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)
"""
)
