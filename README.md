# Residencial Aurora - Assistente Virtual

Este projeto implementa o Assistente Virtual para o aplicativo dos moradores do Residencial Aurora. O assistente é capaz de agendar áreas comuns, liberar visitantes na portaria, cancelar reservas e tirar dúvidas sobre o regulamento interno.

O projeto foi construído utilizando:
- **Google Agent Development Kit (ADK) 2.2.0**
- **FastAPI** para a API de chat.
- **SQLite** e **SQLAlchemy** para persistência e integridade dos dados.

## Arquitetura (Um assistente, vários especialistas)

Para manter as responsabilidades separadas e evitar que o modelo se confunda com diferentes domínios, o projeto adota o padrão de **Roteamento Multi-agentes**:

- **`main_agent`**: Agente principal responsável apenas por receber a intenção inicial do morador e rotear a requisição para o especialista adequado, sem possuir acesso direto a ferramentas de manipulação de dados.
- **`reserva_agent`**: Especialista encarregado da agenda do condomínio. Possui acesso às ferramentas (`reserva_tools.py`) para listar, criar e cancelar reservas.
- **`visitante_agent`**: Especialista encarregado da portaria. Possui acesso às ferramentas (`visitante_tools.py`) para registrar e listar visitantes.
- **`sindico_agent`**: Especialista no regulamento interno. Possui acesso à ferramenta de leitura de arquivos (`sindico_tools.py`) para fazer buscas no regulamento.

## Garantias

1. **Garantia 1: cobrança ou acesso só com confirmação**
   * **Onde:** `src/tools/reserva_tools.py` (função `reservar_area`) e `src/tools/visitante_tools.py` (função `autorizar_visitante`).
   * **Como:** A liberação de acesso e cobrança de taxa utilizam o mecanismo `tool_context.request_confirmation` do ADK. A operação fica pausada na API esperando o endpoint de confirmação explícita do usuário (`/sessoes/{id}/confirmacoes`), tornando impossível para o modelo criar essas entidades inventando uma confirmação ou burlando o fluxo na conversa.

2. **Garantia 2: cada sessão pertence a um apartamento**
   * **Onde:** Nas ferramentas (`reserva_tools.py` e `visitante_tools.py`) e rotas (`api.py`).
   * **Como:** As rotas inserem o `apartamento` apenas no `user_id` da Sessão do ADK no momento de criação. Todas as ferramentas acessam explicitamente `tool_context.session.user_id` para agir no banco de dados. O modelo LLM não tem poder de preencher ou alterar o número do apartamento nos argumentos das funções (o argumento `apartamento` nem sequer existe nas declarações das ferramentas).

3. **Garantia 3: nada se perde no reinício**
   * **Onde:** `src/services/adk_runner.py` e `src/database/session.py`.
   * **Como:** Foi implementada a persistência em dois níveis: o histórico da conversa e sessões do ADK ficam armazenados via `SqliteSessionService` no arquivo `adk_session.db`, enquanto a aplicação possui seu próprio banco `condominio.db`. Nenhum estado vive apenas em memória RAM.

4. **Garantia 4: o regulamento é consultado, não carregado**
   * **Onde:** `src/tools/sindico_tools.py`.
   * **Como:** O agente não recebe o regulamento inteiro no prompt. Ele utiliza a ferramenta `consultar_regulamento(topico: str)` que abre o arquivo `dados/regulamento.md`, filtra contextualmente o arquivo por tópicos e devolve apenas os parágrafos relevantes, economizando tokens e isolando o contexto.

5. **Garantia 5: dois moradores, uma reserva**
   * **Onde:** `src/models/reserva.py` (model `Reserva`).
   * **Como:** Criada uma `UniqueConstraint('area', 'data')` no banco de dados. Qualquer tentativa de double-booking é barrada por Integridade Relacional, impedindo concorrência mesmo no milissegundo de confirmação, lançando um `IntegrityError` gerenciado em código.

## Como Rodar

**Pré-requisitos:**
Ter o Python 3.12+ e o gerenciador de pacotes `uv` instalados.

**1. Variáveis de Ambiente:**
Crie o arquivo `.env` na raiz do projeto (como o `.env.example`) com a sua chave do Gemini:
```env
GEMINI_API_KEY=sua-chave-aqui
```

**2. Instalar dependências:**
```bash
uv sync
```

**3. Restaurar dados iniciais:**
O comando abaixo reseta o banco de dados e carrega o estado original dos arquivos JSON na pasta `dados/`:
```bash
uv run python scripts/setup.py
```

**4. Subir a API:**
```bash
uv run uvicorn api.main:app --reload
```
A API estará respondendo em `http://localhost:8000`.