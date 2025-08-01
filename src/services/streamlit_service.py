import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config.logger import logger
from src.services.openai_service import get_response
from src.utils.prompt import generate_prompt


# Carregar dados
@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    """
    Loads the ENEM 2023 data from a CSV file, optimizes data types by converting
    object columns to category, and caches the result for 3600 seconds.

    Returns:
        pd.DataFrame: The loaded and optimized data.
    """

    df = pd.read_csv("./data/output/enem_2023_tratado.csv")

    # Otimização de tipos de dados
    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].astype("category")

    return df


# Funções de visualização
@st.cache_data(ttl=600)
def generate_comparison_chart(_df, area_col, chart_type, selected_area):
    """
    Gera um gráfico comparativo para uma coluna específica do ENEM.

    Parameters
    ----------
    _df : pd.DataFrame
        DataFrame com os dados do ENEM.
    area_col : str
        Nome da coluna a ser analisada.
    chart_type : str
        Tipo de gráfico a ser gerado.
    selected_area : str
        Nome da área do conhecimento analisada.

    Returns
    -------
    fig : plotly.graph_objs.Figure
        Gráfico comparativo gerado.
    """
    if chart_type == "Boxplot Simplificado":
        # Amostra para melhor performance
        sample_df = _df.sample(min(5000, len(_df)), random_state=42)
        fig = px.box(
            sample_df,
            x="INTERNET",
            y=area_col,
            color="INTERNET",
            points=None,  # Remove pontos individuais para performance
            title=f"Distribuição de {selected_area}",
        )
        fig.update_layout(showlegend=False)

    elif chart_type == "Histograma Agregado":
        fig = px.histogram(
            _df,
            x=area_col,
            color="INTERNET",
            barmode="overlay",
            opacity=0.7,
            nbins=30,  # Menos bins para performance
            histnorm="percent",  # Normalizado para melhor comparação
            title=f"Distribuição Percentual de {selected_area}",
        )

    else:  # Médias Comparadas
        agg_df = (
            _df.groupby(["RENDA_SIMPLIFICADA", "INTERNET"], observed=True)[area_col]
            .mean()
            .reset_index()
        )
        fig = px.bar(
            agg_df,
            x="RENDA_SIMPLIFICADA",
            y=area_col,
            color="INTERNET",
            barmode="group",
            title=f"Médias de {selected_area} por Renda e Internet",
        )

    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


@st.cache_data(ttl=600)
def generate_area_comparison(_df, area_options):
    """
    Gera um gráfico comparativo entre as diferentes áreas do conhecimento, mostrando
    a média e o percentil 50% das notas em cada área para os alunos com e sem acesso
    à internet em casa.

    Parameters
    ----------
    _df : pd.DataFrame
        DataFrame com os dados do ENEM.
    area_options : dict
        Dicionário com as áreas do conhecimento como chaves e os respectivos nomes
        das colunas como valores.

    Returns
    -------
    fig : plotly.graph_objs.Figure
        Gráfico comparativo gerado.
    """

    # Pré-agregação para performance
    area_stats = []
    for area_name, area_col in area_options.items():
        if area_name == "Média Geral":
            continue
        stats = _df.groupby("INTERNET", observed=True)[area_col].describe()[
            ["mean", "50%"]
        ]
        stats["Área"] = area_name
        area_stats.append(stats.reset_index())

    stats_df = pd.concat(area_stats)

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "Ciências da Natureza",
            "Ciências Humanas",
            "Linguagens e Códigos",
            "Matemática",
        ],
    )

    # Adicionar apenas os gráficos principais
    for i, area in enumerate(
        ["Ciências da Natureza", "Ciências Humanas", "Linguagens", "Matemática"]
    ):
        row = (i // 2) + 1
        col = (i % 2) + 1

        area_df = stats_df[stats_df["Área"] == area]

        fig.add_trace(
            go.Bar(
                x=area_df["INTERNET"], y=area_df["mean"], name=area, showlegend=False
            ),
            row=row,
            col=col,
        )

    fig.update_layout(height=600, title_text="Comparação entre Áreas (Médias)")
    return fig


# Função para gerar sumário com IA
@st.cache_data(ttl=3600)
def generate_ai_summary(data_summary, selected_area, chart_type):
    """
    Gera um sumário automático baseado em uma análise de dados do ENEM.

    Parameters
    ----------
    data_summary : pandas.DataFrame
        Resumo estatístico dos dados em forma de DataFrame.
    selected_area : str
        Nome da área do conhecimento analisada.
    chart_type : str
        Tipo de visualização utilizada.

    Returns
    -------
    str
        Sumário gerado pela IA.
    """
    try:
        prompt = generate_prompt(data_summary, selected_area, chart_type)
        logger.info("Prompt gerado com sucesso.")
        logger.debug(f"Prompt gerado: {prompt}")

        response = get_response(prompt)
        logger.info("Sumário gerado com sucesso.")
        logger.debug(f"Sumário gerado: {response}")

        return response
    except Exception as e:
        logger.error(f"Erro ao gerar sumário: {e}")
        st.error(f"Erro ao gerar sumário: {e}")
        return "Não foi possível gerar o sumário automático."
