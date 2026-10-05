from pydantic import BaseModel, model_validator
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
    confirmado: bool | None = None
    confirmar: bool | None = None

    @model_validator(mode="after")
    def validate_confirmacao(self):
        if self.confirmado is None and self.confirmar is None:
            raise ValueError("O campo 'confirmado' é obrigatório.")
        if self.confirmado is None:
            self.confirmado = self.confirmar
        return self

    @property
    def is_confirmed(self) -> bool:
        return bool(self.confirmado)

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
