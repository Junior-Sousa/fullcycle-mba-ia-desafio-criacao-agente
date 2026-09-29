from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from google.genai import types

from google.adk.runners import InMemoryRunner
from agents.bot import agent

app = FastAPI(title="Residencial Aurora API")

# Inicializando o runner do Google ADK em memória
runner = InMemoryRunner(agent=agent)

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # Retorna um emoji de prédio comercial/condomínio em formato SVG
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🏢</text></svg>'
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/")
def read_root():
    return {"message": "API do Assistente Virtual do Residencial Aurora está online!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal para interagir com o Agente assistente_aurora.
    """
    sess = await runner.session_service.get_session(
        app_name=runner.app_name,
        user_id=request.user_id,
        session_id=request.session_id
    )
    
    if sess is None:
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=request.user_id,
            session_id=request.session_id
        )

    # Formata a mensagem do usuário no padrão exigido pelo ADK
    msg = types.Content(role="user", parts=[types.Part.from_text(text=request.message)])
    
    response_text = ""
    # Executa o runner em modo assíncrono para colher os eventos de resposta
    try:
        async for event in runner.run_async(
            user_id=request.user_id, 
            session_id=request.session_id, 
            new_message=msg
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do agente: {str(e)}")

    if not response_text:
        response_text = "Desculpe, não consegui processar sua solicitação."

    return ChatResponse(
        response=response_text,
        session_id=request.session_id
    )
