import os

def consultar_regulamento(topico: str) -> str:
    """
    Pesquisa e extrai regras do Regulamento Interno (dados/regulamento.md) do condomínio.
    Requer o nome do tópico ou a pergunta relacionada para fazer a busca textual.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    caminho = os.path.join(BASE_DIR, "dados", "regulamento.md")
    
    if not os.path.exists(caminho):
        return "Erro: Arquivo do regulamento interno não localizado."
        
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
    termos_busca = [t.lower() for t in topico.split() if len(t) > 3]
    if not termos_busca:
        termos_busca = [topico.lower()]
        
    conteudo_relevante = []
    capitulo_atual = ""
    for linha in linhas:
        if linha.startswith("#"):
            capitulo_atual = linha.strip()
        
        linha_low = linha.lower()
        if any(termo in linha_low for termo in termos_busca):
            if capitulo_atual not in conteudo_relevante:
                conteudo_relevante.append(capitulo_atual)
            conteudo_relevante.append(linha.strip())
            
    if not conteudo_relevante:
        return "Nenhuma regra encontrada sobre este tópico no regulamento."
        
    return "Trecho extraído do regulamento: \n" + "\n".join(conteudo_relevante[:15])
