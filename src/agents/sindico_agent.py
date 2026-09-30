from google.adk import Agent
from src.tools.sindico_tools import consultar_regulamento

sindico_specialist = Agent(
    name="sindico_specialist",
    model="gemini-2.5-flash",
    description="Especialista em regras e regulamentos do condomínio. Acione para responder dúvidas sobre regras.",
    instruction="""Você é o Síndico (Especialista em Regras) do Residencial Aurora.
Sua única função é tirar dúvidas sobre o regulamento interno.
Use a tool `consultar_regulamento` passando o tema da pergunta para encontrar as regras aplicáveis.
Responda com base estrita no que a tool retornar, sendo educado e direto.
""",
    tools=[consultar_regulamento]
)
