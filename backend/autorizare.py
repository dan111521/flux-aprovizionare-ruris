
import os
import jwt

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database import get_connection

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("Lipseste JWT_SECRET din .env")

securitate_token = HTTPBearer()


def utilizator_curent(
    credentials: HTTPAuthorizationCredentials = Depends(securitate_token)
):
    try:
        continut = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )
        utilizator_id = int(continut["sub"])

    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Token invalid sau expirat."
        )

    with get_connection() as conn:
        utilizator = conn.execute(
            """
            SELECT id, nume, username, rol, activ
            FROM utilizatori
            WHERE id = ?
            """,
            (utilizator_id,)
        ).fetchone()

    if not utilizator or not utilizator["activ"]:
        raise HTTPException(
            status_code=401,
            detail="Utilizator inexistent sau inactiv."
        )

    return dict(utilizator)


def permite_roluri(*roluri_permise):
    def verifica_rol(
        utilizator: dict = Depends(utilizator_curent)
    ):
        if utilizator["rol"] not in roluri_permise:
            raise HTTPException(
                status_code=403,
                detail="Nu ai permisiunea pentru aceasta operatiune."
            )

        return utilizator

    return verifica_rol
