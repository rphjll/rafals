"""Erreur « règle non respectée » : porte le message montré tel quel à l'utilisateur."""


class ErreurRegle(Exception):
    def __init__(self, message: str, code_http: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code_http = code_http
