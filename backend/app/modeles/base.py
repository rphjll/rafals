"""Base commune des modèles. Les tables sont créées par les scripts db/schema_v*.sql,
JAMAIS par le code : ne jamais appeler Base.metadata.create_all()."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
