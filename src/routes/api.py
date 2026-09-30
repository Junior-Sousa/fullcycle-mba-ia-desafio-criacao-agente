import uuid
import json
from fastapi import APIRouter, HTTPException
from google.genai import types
from src.services.adk_runner import runner
from src.services.session_service import SessionService
from src.repositories.reserva_repository import ReservaRepository
from src.repositories.visitante_repository import VisitanteRepository
from src.routes.schemas import (
    CriarSessaoReq, CriarSessaoRes,
    EnviarMensagemReq, ResponderConfirmacaoReq,
    RespostaRes, ConfirmacaoPendente,
    ReservaModel, VisitanteModel,
    EventoRes, EventosRes,
    AcaoConfirmacao,
)

router = APIRouter()


async def _get_or_404_user_id(session_id: str) -> str:
    user_id = await SessionService.get_user_id(session_id)
    if not user_id:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return user_id


async def _process_adk_events(session_id: str, user_id: str, adk_run_coro) -> RespostaRes:
    response_text = ""
    pendentes = []

    try:
        async for event in adk_run_coro:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                    elif part.function_call and part.function_call.name == "adk_request_confirmation":
                        args = part.function_call.args or {}
                        tool_conf = args.get('toolConfirmation', {})
                        payload = tool_conf.get('payload', {})
                        if isinstance(payload, str):
                            payload = json.loads(payload)

                        acao = AcaoConfirmacao.RESERVAR if "area" in payload else AcaoConfirmacao.AUTORIZAR

                        pendentes.append(ConfirmacaoPendente(
                            id=part.function_call.id,
                            acao=acao.value,
                            detalhes=payload
                        ))
                        response_text = ""
    except Exception as e:
        error_str = str(e).lower()
        if "invalid" in error_str and "confirmation" in error_str or "not expected" in error_str:
            raise HTTPException(status_code=409, detail="Confirmação inválida")
        raise HTTPException(status_code=500, detail=str(e))

    if pendentes:
        response_text = ""

    return RespostaRes(
        resposta=response_text,
        confirmacoes_pendentes=pendentes
    )


@router.post("/sessoes", response_model=CriarSessaoRes, status_code=201)
async def criar_sessao(req: CriarSessaoReq):
    session_id = str(uuid.uuid4())
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=req.apartamento,
        session_id=session_id
    )
    return CriarSessaoRes(session_id=session_id)


@router.post("/sessoes/{session_id}/mensagens", response_model=RespostaRes)
async def enviar_mensagem(session_id: str, req: EnviarMensagemReq):
    user_id = await _get_or_404_user_id(session_id)

    msg = types.Content(role="user", parts=[types.Part.from_text(text=req.texto)])

    return await _process_adk_events(
        session_id,
        user_id,
        runner.run_async(user_id=user_id, session_id=session_id, new_message=msg)
    )


@router.post("/sessoes/{session_id}/confirmacoes", response_model=RespostaRes)
async def responder_confirmacao(session_id: str, req: ResponderConfirmacaoReq):
    user_id = await _get_or_404_user_id(session_id)

    msg = types.Content(role="user", parts=[
        types.Part(
            function_response=types.FunctionResponse(
                name="adk_request_confirmation",
                id=req.id,
                response={"confirmed": req.confirmar}
            )
        )
    ])

    return await _process_adk_events(
        session_id,
        user_id,
        runner.run_async(user_id=user_id, session_id=session_id, new_message=msg)
    )


@router.get("/sessoes/{session_id}/eventos", response_model=EventosRes)
async def listar_eventos(session_id: str):
    user_id = await _get_or_404_user_id(session_id)

    session_data = await runner.session_service.get_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
    )
    if not session_data or not session_data.events:
        return EventosRes(eventos=[])

    eventos = []
    for event in session_data.events:
        msg = event.content
        if not msg:
            continue
        for part in (msg.parts or []):
            if part.text:
                eventos.append(EventoRes(role=event.author, texto=part.text))
            elif part.function_call:
                eventos.append(EventoRes(role=event.author, acao=part.function_call.name))
            elif part.function_response:
                eventos.append(EventoRes(role=event.author, acao=f"resposta_confirmacao: {part.function_response.name}"))

    return EventosRes(eventos=eventos)


@router.get("/apartamentos/{id}/reservas", response_model=list[ReservaModel])
async def listar_reservas_apartamento(id: str):
    reservas = ReservaRepository.listar_reservas_por_apartamento(id)
    return [ReservaModel(codigo=str(r.codigo), area=str(r.area), data=str(r.data)) for r in reservas]


@router.get("/apartamentos/{id}/visitantes", response_model=list[VisitanteModel])
async def listar_visitantes_apartamento(id: str):
    visitantes = VisitanteRepository.listar_visitantes_por_apartamento(id)
    return [VisitanteModel(nome=str(v.nome), data=str(v.data)) for v in visitantes]
