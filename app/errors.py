"""Tratamento global de erros (F18).
Nunca expor mensagens internas do SGBD ao cliente."""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

log = logging.getLogger("petshop")

class RegraNegocioError(Exception):
    """Violação de regra de negócio (retorna 409 ou 400)."""

    def __init__(self, mensagem: str, status_code: int = 409):
        self.mensagem = mensagem
        self.status_code = status_code


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RegraNegocioError)
    async def _regra(_: Request, exc: RegraNegocioError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensagem})

    @app.exception_handler(IntegrityError)
    async def _integrity(_: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=409,
            content={"detail": "Conflito: dado duplicado ou referência inválida."},
        )

    @app.exception_handler(OperationalError)
    async def _operational(_: Request, exc: OperationalError):
        return JSONResponse(status_code=503, content={"detail": "Banco de dados indisponível."})

    @app.exception_handler(SQLAlchemyError)
    async def _sqlalchemy(_: Request,   exc: SQLAlchemyError):
        return JSONResponse(status_code=500, content={"detail": "Erro ao persistir os dados."})