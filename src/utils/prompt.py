def generate_prompt(data_summary, selected_area, chart_type) -> str:
    """
    Gera um texto de prompt para uma tarefa de redação sobre análise de dados do ENEM.

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
        Texto de prompt para a tarefa de redação.
    """
    return f"""
        Você é um analista educacional especializado no ENEM. 
        Gere um sumário conciso (máximo 150 palavras) em português sobre os seguintes dados:
        
        Área analisada: {selected_area}
        Tipo de visualização: {chart_type}
        
        Dados estatísticos:
        {data_summary.to_string()}
        
        Inclua:
        1. Principais insights
        2. Diferenças notáveis entre grupos
        3. Possíveis implicações educacionais
    """
