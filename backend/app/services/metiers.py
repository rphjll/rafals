"""Métiers et catégories. Règles : .doc/regles-metier/RM-METIERS.md."""

import re
import unicodedata
from datetime import datetime

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.metiers import CategorieMetier, Metier, PropositionMetier
from app.services import journal
from app.services.erreurs import ErreurRegle

NOM_LONGUEUR_MIN, NOM_LONGUEUR_MAX = 2, 60


def sans_accents(texte: str) -> str:
    """« Électricien » → « electricien » (même calcul que unaccent(lower()) dans la base)."""
    decompose = unicodedata.normalize("NFD", texte.strip().lower())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def _normalise(colonne):
    return func.unaccent(func.lower(colonne))


# ---------- Recherche ----------


def rechercher(db: Session, texte: str, limite: int = 10) -> list[tuple[Metier, CategorieMetier]]:
    """Métiers actifs dont le nom, un mot du nom ou un mot-clé commence par le texte tapé, sans accents.
    Ordre : nom qui commence par le texte, puis un mot du nom, puis un mot-clé ; ensuite par ordre alphabétique.
    Ex. « plom » → Plombier ; « fuite » → Plombier (mot-clé) ; « electricien » → Électricien."""
    # « % » et « _ » tapés par l'utilisateur sont cherchés tels quels (pas comme des jokers)
    q = sans_accents(texte).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    if not q:
        return []
    # « Plombier », « Menuisier / Ébéniste » : on cherche au début du nom ou au début d'un de ses mots
    nom = func.concat(" ", func.replace(func.replace(_normalise(Metier.nom), "/", " "), "(", " "))
    # Mots-clés mis bout à bout : « plomberie fuite chauffagiste … »
    mots = func.concat(" ", _normalise(func.array_to_string(Metier.mots_cles, " ")))
    debut_nom = _normalise(Metier.nom).like(q + "%", escape="\\")
    debut_mot = nom.like("% " + q + "%", escape="\\")
    mot_cle = mots.like("% " + q + "%", escape="\\")
    rang = case((debut_nom, 1), (debut_mot, 2), else_=3)
    requete = (
        select(Metier, CategorieMetier)
        .join(CategorieMetier, CategorieMetier.id == Metier.categorie_id)
        .where(Metier.est_active, CategorieMetier.est_active, or_(debut_nom, debut_mot, mot_cle))
        .order_by(rang, Metier.nom)
        .limit(limite)
    )
    return [(metier, categorie) for metier, categorie in db.execute(requete).all()]


def categories_avec_metiers(db: Session) -> list[tuple[CategorieMetier, list[Metier]]]:
    """Les dossiers actifs, dans leur ordre, chacun avec ses métiers actifs par ordre alphabétique."""
    categories = db.scalars(
        select(CategorieMetier).where(CategorieMetier.est_active).order_by(CategorieMetier.ordre)
    ).all()
    metiers = db.scalars(select(Metier).where(Metier.est_active).order_by(Metier.nom)).all()
    par_categorie: dict[int, list[Metier]] = {}
    for metier in metiers:
        par_categorie.setdefault(metier.categorie_id, []).append(metier)
    return [(c, par_categorie.get(c.id, [])) for c in categories if par_categorie.get(c.id)]


# ---------- Propositions ----------


def _metier_du_meme_nom(db: Session, nom: str) -> Metier | None:
    return db.scalar(select(Metier).where(_normalise(Metier.nom) == sans_accents(nom), Metier.est_active))


def proposer(db: Session, compte: Compte, nom_propose: str, maintenant: datetime) -> PropositionMetier:
    nom = " ".join(nom_propose.split())
    if not NOM_LONGUEUR_MIN <= len(nom) <= NOM_LONGUEUR_MAX:
        raise ErreurRegle(f"Le nom du métier doit faire entre {NOM_LONGUEUR_MIN} et {NOM_LONGUEUR_MAX} caractères.")
    existant = _metier_du_meme_nom(db, nom)
    if existant is not None:
        raise ErreurRegle(f"Ce métier existe déjà dans la liste : « {existant.nom} ».")
    deja = db.scalar(
        select(PropositionMetier.id).where(
            PropositionMetier.propose_par_id == compte.id,
            PropositionMetier.statut == "en_attente",
            _normalise(PropositionMetier.nom_propose) == sans_accents(nom),
        )
    )
    if deja is not None:
        raise ErreurRegle("Vous avez déjà proposé ce métier : il attend la décision de l'administrateur.")
    proposition = PropositionMetier(propose_par_id=compte.id, nom_propose=nom, statut="en_attente", propose_le=maintenant)
    db.add(proposition)
    db.flush()
    journal.noter(
        db, auteur_id=compte.id, action="proposer_metier", table_cible="proposition_metier",
        ligne_id=proposition.id, apres={"nom_propose": nom}, maintenant=maintenant,
    )
    return proposition


def decider_proposition(
    db: Session,
    administrateur: Compte,
    proposition_id: int,
    *,
    decision: str,
    categorie_id: int | None,
    metier_id: int | None,
    maintenant: datetime,
) -> PropositionMetier:
    """decision : « acceptee » (crée le métier dans categorie_id), « remplacee » (métier existant metier_id,
    le nom proposé devient un de ses mots-clés) ou « refusee »."""
    proposition = db.get(PropositionMetier, proposition_id)
    if proposition is None:
        raise ErreurRegle("Cette proposition n'existe pas.", 404)
    if proposition.statut != "en_attente":
        raise ErreurRegle("Cette proposition a déjà été décidée.")

    if decision == "acceptee":
        if categorie_id is None or db.get(CategorieMetier, categorie_id) is None:
            raise ErreurRegle("Choisissez le dossier où ranger ce nouveau métier.")
        existant = _metier_du_meme_nom(db, proposition.nom_propose)
        if existant is not None:
            raise ErreurRegle(f"Ce métier existe déjà : « {existant.nom} ». Choisissez plutôt « Remplacer ».")
        metier = creer_metier(db, administrateur, nom=proposition.nom_propose, categorie_id=categorie_id, maintenant=maintenant)
        proposition.metier_retenu_id = metier.id
    elif decision == "remplacee":
        metier = db.get(Metier, metier_id) if metier_id is not None else None
        if metier is None:
            raise ErreurRegle("Choisissez le métier existant qui convient.")
        mot = sans_accents(proposition.nom_propose)
        if mot not in [sans_accents(m) for m in metier.mots_cles]:
            metier.mots_cles = [*metier.mots_cles, mot]
        proposition.metier_retenu_id = metier.id
    elif decision != "refusee":
        raise ErreurRegle("Décision inconnue.")

    proposition.statut = decision
    proposition.decide_par_id = administrateur.id
    proposition.decide_le = maintenant
    journal.noter(
        db, auteur_id=administrateur.id, action="decider_proposition_metier", table_cible="proposition_metier",
        ligne_id=proposition.id, avant={"statut": "en_attente"},
        apres={"statut": decision, "metier_retenu_id": proposition.metier_retenu_id}, maintenant=maintenant,
    )
    return proposition


# ---------- Gestion par l'administrateur ----------


def _code_libre(db: Session, nom: str, modele) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", sans_accents(nom)).strip("-") or "metier"
    code, numero = base, 2
    while db.scalar(select(modele.id).where(modele.code == code)) is not None:
        code, numero = f"{base}-{numero}", numero + 1
    return code


def creer_metier(db: Session, auteur: Compte, *, nom: str, categorie_id: int, maintenant: datetime) -> Metier:
    nom = " ".join(nom.split())
    if not NOM_LONGUEUR_MIN <= len(nom) <= NOM_LONGUEUR_MAX:
        raise ErreurRegle(f"Le nom du métier doit faire entre {NOM_LONGUEUR_MIN} et {NOM_LONGUEUR_MAX} caractères.")
    if db.get(CategorieMetier, categorie_id) is None:
        raise ErreurRegle("Ce dossier n'existe pas.", 404)
    if _metier_du_meme_nom(db, nom) is not None:
        raise ErreurRegle("Ce métier existe déjà dans la liste.")
    metier = Metier(categorie_id=categorie_id, code=_code_libre(db, nom, Metier), nom=nom, mots_cles=[])
    db.add(metier)
    db.flush()
    journal.noter(
        db, auteur_id=auteur.id, action="creer_metier", table_cible="metier", ligne_id=metier.id,
        apres={"nom": nom, "categorie_id": categorie_id}, maintenant=maintenant,
    )
    return metier


def modifier_metier(
    db: Session, auteur: Compte, metier_id: int, *, nom: str, categorie_id: int, mots_cles: list[str],
    est_active: bool, maintenant: datetime,
) -> Metier:
    metier = db.get(Metier, metier_id)
    if metier is None:
        raise ErreurRegle("Ce métier n'existe pas.", 404)
    if db.get(CategorieMetier, categorie_id) is None:
        raise ErreurRegle("Ce dossier n'existe pas.", 404)
    nom = " ".join(nom.split())
    if not NOM_LONGUEUR_MIN <= len(nom) <= NOM_LONGUEUR_MAX:
        raise ErreurRegle(f"Le nom du métier doit faire entre {NOM_LONGUEUR_MIN} et {NOM_LONGUEUR_MAX} caractères.")
    avant = {"nom": metier.nom, "categorie_id": metier.categorie_id, "mots_cles": metier.mots_cles, "est_active": metier.est_active}
    metier.nom, metier.categorie_id, metier.est_active = nom, categorie_id, est_active
    metier.mots_cles = sorted({sans_accents(m) for m in mots_cles if m.strip()})
    journal.noter(
        db, auteur_id=auteur.id, action="modifier_metier", table_cible="metier", ligne_id=metier.id, avant=avant,
        apres={"nom": nom, "categorie_id": categorie_id, "mots_cles": metier.mots_cles, "est_active": est_active},
        maintenant=maintenant,
    )
    return metier
