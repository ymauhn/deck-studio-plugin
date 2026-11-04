"""JSON API helpers for every router: errors as {error, message} (the UI shows `message`) and JSON bodies."""
import json


class ApiError(Exception):
    """raise ApiError(409, "busy", "Outro pedido está em andamento.") -> that status and {error, message}."""

    def __init__(self, status, error, message):
        super().__init__(message)
        self.status, self.error, self.message = status, error, message


async def json_body(request, limit=1_000_000):
    """The request's JSON object ({} when empty); a bad or oversized body is a 400 or 413 ApiError."""
    raw = await request.body()
    if len(raw) > limit:
        raise ApiError(413, "too-large", "Corpo da requisição grande demais.")
    try:
        body = json.loads(raw or b"{}")
    except ValueError:
        body = None
    if not isinstance(body, dict):
        raise ApiError(400, "bad-json", "Corpo JSON inválido.")
    return body
