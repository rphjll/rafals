"""Journal des actions : qui a fait quoi, quand, avant / après. On y écrit, on n'y efface jamais."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.modeles.journal import JournalAction


def noter(
    db: Session,
    *,
    auteur_id: int | None,
    action: str,
    table_cible: str,
    ligne_id: int | None,
    maintenant: datetime,
    avant: dict[str, Any] | None = None,
    apres: dict[str, Any] | None = None,
) -> None:
    db.add(
        JournalAction(
            auteur_id=auteur_id,
            action=action,
            table_cible=table_cible,
            ligne_id=ligne_id,
            avant=avant,
            apres=apres,
            fait_le=maintenant,
        )
    )
