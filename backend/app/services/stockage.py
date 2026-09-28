"""Le « placard » à fichiers, compatible S3 : Garage sur le PC, stockage d'OVH en ligne.
Seul endroit du code qui parle au stockage (portabilité : on change d'hébergeur sans toucher au reste)."""

from uuid import uuid4

import boto3
from botocore.config import Config

from app import config

_client = boto3.client(
    "s3",
    endpoint_url=config.S3_ADRESSE,
    region_name=config.S3_REGION,
    aws_access_key_id=config.S3_CLE_ACCES,
    aws_secret_access_key=config.S3_CLE_SECRETE,
    config=Config(s3={"addressing_style": "path"}),
)


def deposer(contenu: bytes, type_mime: str) -> str:
    """Range le fichier sous un nom tiré au hasard et renvoie ce nom (la clé de stockage)."""
    cle = uuid4().hex
    _client.put_object(Bucket=config.S3_COMPARTIMENT, Key=cle, Body=contenu, ContentType=type_mime)
    return cle


def lire(cle: str) -> bytes:
    return _client.get_object(Bucket=config.S3_COMPARTIMENT, Key=cle)["Body"].read()


def supprimer(cle: str) -> None:
    _client.delete_object(Bucket=config.S3_COMPARTIMENT, Key=cle)


def lister_cles() -> list[str]:
    reponse = _client.list_objects_v2(Bucket=config.S3_COMPARTIMENT)
    return [objet["Key"] for objet in reponse.get("Contents", [])]
