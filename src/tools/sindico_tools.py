import os
import re
import unicodedata

def _normalizar(texto: str) -> str:
    """Normaliza o texto removendo acentos e pontuações para facilitar buscas."""
    return re.sub(
        r'[^a-z0-9\s]',
        ' ',
        unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()
    )

STOPWORDS = {
    'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na', 'nos', 'nas',
    'para', 'com', 'por', 'sobre', 'qual', 'quais', 'como', 'quando',
    'onde', 'este', 'esta', 'esse', 'essa', 'aquele', 'aquela', 'que',
    'uma', 'um', 'umas', 'uns', 'ao', 'aos', 'regras', 'regra', 'sobre',
    'fim', 'fins'
}

def consultar_regulamento(topico: str) -> str:
    """
    Pesquisa e extrai regras do Regulamento Interno (dados/regulamento.md) do condomínio.
    Localiza o capítulo referente ao assunto e devolve o texto integral do capítulo
    (do título ## até o próximo ##), evitando vazamento de regras de outros capítulos.
    
    Args:
        topico: Tema ou assunto da consulta (ex: 'piscina', 'silêncio', 'animais de estimação', 'mudanças', 'obras', 'garagem', 'salão de festas', etc.).
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    caminho = os.path.join(BASE_DIR, "dados", "regulamento.md")
    
    if not os.path.exists(caminho):
        return "Erro: Arquivo do regulamento interno não localizado."
        
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Recorta o documento por capítulos (iniciados por '## ') até o próximo '## ' ou fim do texto
    blocos = [
        m.group(1).strip()
        for m in re.finditer(r'(^##\s+.*?)(?=(?:^##\s+)|\Z)', conteudo, re.MULTILINE | re.DOTALL)
    ]
    
    if not blocos:
        return "Nenhuma regra encontrada sobre este tópico no regulamento."

    topico_norm = _normalizar(topico)
    termos_busca = [t for t in topico_norm.split() if len(t) > 2 and t not in STOPWORDS]
    if not termos_busca:
        termos_busca = [topico_norm]

    melhor_capitulo = None
    maior_score = 0

    for bloco in blocos:
        linhas = bloco.splitlines()
        titulo = linhas[0] if linhas else ""
        titulo_norm = _normalizar(titulo)
        conteudo_norm = _normalizar(bloco)

        score = 0
        # 1. Correspondência direta no título dinâmico do capítulo (peso máximo)
        for t in termos_busca:
            if t in titulo_norm:
                score += 50

        # 2. Frequência dos termos no corpo do capítulo
        for t in termos_busca:
            ocorrencias = conteudo_norm.count(t)
            score += min(ocorrencias, 15)

        if score > maior_score:
            maior_score = score
            melhor_capitulo = bloco

    if not melhor_capitulo or maior_score == 0:
        return "Nenhuma regra encontrada sobre este tópico no regulamento."

    return melhor_capitulo
