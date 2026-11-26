import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, SQLAlchemyError

log = logging.getLogger("petshop")


class RegraNegocioError(Exception):
   

    def __init__(self, mensagem: str, status_code: int = 409):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


def _resposta(status: int, detalhe: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": detalhe})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RegraNegocioError)
    async def _regra(_: Request, exc: RegraNegocioError):
        return _resposta(exc.status_code, exc.mensagem)

    @app.exception_handler(IntegrityError)
    async def _integrity(_: Request, exc: IntegrityError):
        log.warning("IntegrityError: %s", exc.orig)
        return _resposta(409, "Conflito: dado duplicado ou referência inválida.")

    @app.exception_handler(DataError)
    async def _data(_: Request, exc: DataError):
        log.warning("DataError: %s", exc.orig)
        return _resposta(422, "Dados inválidos para persistência.")

    @app.exception_handler(OperationalError)
    async def _operational(_: Request, exc: OperationalError):
        log.error("OperationalError: %s", exc.orig)
        return _resposta(503, "Banco de dados indisponível.")

    @app.exception_handler(SQLAlchemyError)
    async def _sqlalchemy(_: Request, exc: SQLAlchemyError):
        log.error("Erro de persistência", exc_info=exc)
        return _resposta(500, "Erro ao persistir os dados.")

    @app.exception_handler(Exception)
    async def _inesperado(_: Request, exc: Exception):
        log.error("Erro inesperado", exc_info=exc)
        return _resposta(500, "Erro interno inesperado.")