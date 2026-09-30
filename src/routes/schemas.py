from pydantic import BaseModel
from enum import Enum


class CriarSessaoReq(BaseModel):
    apartamento: str

class CriarSessaoRes(BaseModel):
    session_id: str

class EnviarMensagemReq(BaseModel):
    texto: str

class ConfirmacaoPendente(BaseModel):
    id: str
    acao: str
    detalhes: dict

class RespostaRes(BaseModel):
    resposta: str
    confirmacoes_pendentes: list[ConfirmacaoPendente]

class ResponderConfirmacaoReq(BaseModel):
    id: str
    confirmar: bool

class ReservaModel(BaseModel):
    codigo: str
    area: str
    data: str

class VisitanteModel(BaseModel):
    nome: str
    data: str

class EventoRes(BaseModel):
    role: str
    texto: str | None = None
    acao: str | None = None

class EventosRes(BaseModel):
    eventos: list[EventoRes]

class AcaoConfirmacao(str, Enum):
    RESERVAR = "reservar"
    AUTORIZAR = "autorizar"
