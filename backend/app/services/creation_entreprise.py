"""Créer une auto-entreprise depuis rafals (RM-CREATION-AUTO-ENTREPRISE.md, lot 7.1 ; maquette et MLD validés par
Raphael le 04/10/2026). La personne répond à 5 étapes, dépose ses papiers, donne pouvoir à rafals ; rafals envoie le
dossier au guichet de l'État (services/guichet.py), suit sa réponse et ajoute le SIRET reçu au profil.

Les données sensibles (numéro de sécurité sociale, noms des parents, papiers) sont effacées dès que le dossier est
accepté, refusé ou fermé ; un brouillon abandonné depuis 30 jours est effacé en entier."""

import base64
import re
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.comptes import Compte
from app.modeles.creation import DossierCreation, PieceDossier
from app.modeles.fichiers import Fichier
from app.modeles.journal import JournalAction
from app.modeles.metiers import CategorieMetier, Metier
from app.modeles.prestataires import Commune, Prestataire
from app.services import fichiers, guichet, journal, mails, pdf_pieces, stockage
from app.services import siret as service_siret
from app.services.communes import controler_adresse
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, profil_de

OUVERTS = ("brouillon", "envoye", "en_examen", "a_corriger")
MODIFIABLES = ("brouillon", "a_corriger")
SITE_DE_L_ETAT = "formalites.entreprises.gouv.fr"

# Les papiers : nom montré à la personne, et code du guichet (dictionnaire de données de l'INPI, feuille typeDocument)
PIECES = {
    "identite": ("la pièce d'identité", "PJ_11"),
    "titre_sejour": ("le titre de séjour", "PJ_14"),
    "diplome": ("le diplôme ou la preuve de 3 ans d'expérience", "PJ_31"),
    "autorisation_parents": ("l'autorisation des parents", "PJ_226"),
    "bail": ("le bail du local", "PJ_29"),
    "attestation": ("l'attestation sur l'honneur", "PJ_17"),
    "pouvoir": ("le pouvoir donné à rafals", "PJ_51"),
}
PIECES_DEPOSEES = ("identite", "titre_sejour", "diplome", "autorisation_parents", "bail")  # les autres : écrites par rafals

CIVILITES = {"monsieur": "1", "madame": "2"}
SITUATIONS = {"celibataire": "1", "divorce": "2", "veuf": "3", "marie": "4", "pacse": "5", "concubinage": "6"}
NATIONALITES = ("francaise", "union_europeenne", "autre")
LIEUX = ("chez_clients", "chez_moi", "local")
ACTIVITES = {"aucune": None, "salarie": "1", "retraite": "B"}


@dataclass
class Vous:
    civilite: str
    nom_naissance: str
    nom_usage: str | None
    prenoms: str
    naissance_le: date
    naissance_commune_id: int | None
    naissance_pays: str | None
    nationalite: str
    situation_famille: str
    conjoint_travaille: bool
    numero_secu: str
    adresse_rue: str
    commune_id: int
    code_postal: str
    mail: str
    telephone: str


@dataclass
class Activite:
    metier_id: int
    description: str
    debut_le: date
    lieu_travail: str
    local_adresse: str | None
    local_commune_id: int | None
    local_code_postal: str | None
    nom_commercial: str | None
    activite_en_meme_temps: str
    ancien_siren: str | None


@dataclass
class Choix:
    periodicite: str
    impot_avec_cotisations: bool
    acre_demandee: bool
    adresse_non_publique: bool


# ---------- Les métiers ----------


def _categorie(db: Session, metier: Metier) -> str:
    return db.get_one(CategorieMetier, metier.categorie_id).code


def metier_renvoye(db: Session, metier: Metier) -> bool:
    """Métier que rafals ne sait pas déclarer (santé, professions à agrément…) : la démarche se fait sur le site de l'État."""
    return metier.code in reglages.CREATION_METIERS_RENVOYES or _categorie(db, metier) in reglages.CREATION_CATEGORIES_RENVOYEES


def metier_reglemente(metier: Metier) -> bool:
    """Ex. plombier, coiffeur : il faut un diplôme ou 3 ans d'expérience."""
    return metier.code in reglages.CREATION_METIERS_REGLEMENTES


def forme_exercice(db: Session, metier: Metier) -> str:
    """Ex. plombier → ARTISANALE_REGLEMENTEE ; cours de langues → INDEPENDANTE (libérale non réglementée)."""
    forme = reglages.CREATION_FORME_PAR_CATEGORIE.get(_categorie(db, metier), "COMMERCIALE")
    return "ARTISANALE_REGLEMENTEE" if forme == "ARTISANALE" and metier_reglemente(metier) else forme


def regles_des_metiers(db: Session) -> tuple[list[int], list[int]]:
    """(métiers réglementés, métiers renvoyés vers le site de l'État), pour les écrans."""
    metiers = list(db.scalars(select(Metier).where(Metier.est_active)))
    return [m.id for m in metiers if metier_reglemente(m)], [m.id for m in metiers if metier_renvoye(db, m)]


# ---------- Trouver le dossier ----------


def dernier(db: Session, compte: Compte) -> DossierCreation | None:
    return db.scalar(select(DossierCreation).where(DossierCreation.compte_id == compte.id).order_by(DossierCreation.id.desc()).limit(1))


def _ouvert(db: Session, compte: Compte) -> DossierCreation | None:
    return db.scalar(select(DossierCreation).where(DossierCreation.compte_id == compte.id, DossierCreation.statut.in_(OUVERTS)))


def empechement(db: Session, compte: Compte) -> str | None:
    """Pourquoi ce compte ne peut pas commencer de dossier (demande de Raphael : ne pas recréer une entreprise)."""
    profil = profil_de(db, compte)
    if profil is not None and profil.siret:
        return f"Vous avez déjà une entreprise (SIRET {profil.siret}) : il n'y a rien à créer."
    return None


def _modifiable(db: Session, compte: Compte) -> DossierCreation:
    dossier = _ouvert(db, compte)
    if dossier is None:
        raise ErreurRegle("Vous n'avez pas de dossier en cours.", 404)
    if dossier.statut not in MODIFIABLES:
        raise ErreurRegle("Votre dossier est envoyé : il ne se modifie plus, sauf si l'administration demande une correction.")
    return dossier


def pieces(db: Session, dossier: DossierCreation) -> dict[str, PieceDossier]:
    return {p.sorte: p for p in db.scalars(select(PieceDossier).where(PieceDossier.dossier_id == dossier.id))}


# ---------- Commencer ----------


def commencer(db: Session, compte: Compte, maintenant: datetime) -> DossierCreation:
    """Ouvre un brouillon, rempli d'avance avec ce que rafals sait déjà (nom, mail, téléphone, métier, ville)."""
    raison = empechement(db, compte)
    if raison:
        raise ErreurRegle(raison)
    dossier = _ouvert(db, compte)
    if dossier is not None:
        return dossier
    profil = profil_de(db, compte)
    dossier = DossierCreation(
        compte_id=compte.id, statut="brouillon", cree_le=maintenant, modifie_le=maintenant, statut_change_le=maintenant,
        nom_naissance=compte.nom.upper(), prenoms=compte.prenom, naissance_le=compte.date_naissance, mail=compte.email,
        telephone=compte.telephone, metier_id=profil.metier_principal_id if profil else None,
    )
    db.add(dossier)
    db.flush()
    journal.noter(db, auteur_id=compte.id, action="creation_commencer", table_cible="dossier_creation", ligne_id=dossier.id,
                  maintenant=maintenant)
    return dossier


def abandonner(db: Session, compte: Compte, maintenant: datetime) -> None:
    """La personne efface elle-même son brouillon (jamais un dossier déjà envoyé)."""
    dossier = _ouvert(db, compte)
    if dossier is None or dossier.statut != "brouillon":
        raise ErreurRegle("Seul un dossier pas encore envoyé peut être effacé.")
    _effacer_brouillon(db, dossier, compte.id, maintenant)


def _effacer_brouillon(db: Session, dossier: DossierCreation, auteur_id: int | None, maintenant: datetime) -> None:
    for piece in pieces(db, dossier).values():
        _effacer_fichier(db, piece, maintenant)
        db.delete(piece)
    db.flush()  # les papiers d'abord : la base refuse d'effacer un dossier qui en a encore
    journal.noter(db, auteur_id=auteur_id, action="creation_effacer_brouillon", table_cible="dossier_creation",
                  ligne_id=dossier.id, maintenant=maintenant)
    db.delete(dossier)
    db.flush()


# ---------- Étape 1 : vous ----------


def numero_secu_valide(numero: str) -> bool:
    """15 chiffres (2A ou 2B pour la Corse) ; les 2 derniers sont une clé calculée sur les 13 premiers.
    Ex. « 198033306312352 » : 97 − (1980333063123 modulo 97) = 52."""
    if not re.fullmatch(r"[0-9]{6}[0-9AB][0-9]{8}", numero):
        return False
    corps = numero[:5] + {"2A": "19", "2B": "18"}.get(numero[5:7], numero[5:7]) + numero[7:13]
    return corps.isdigit() and 97 - int(corps) % 97 == int(numero[13:])


def age(naissance: date, jour: date) -> int:
    return jour.year - naissance.year - ((jour.month, jour.day) < (naissance.month, naissance.day))


def _propre(texte: str | None, maxi: int) -> str | None:
    return " ".join((texte or "").split())[:maxi] or None


def enregistrer_vous(db: Session, compte: Compte, v: Vous, maintenant: datetime) -> DossierCreation:
    dossier = _modifiable(db, compte)
    nom, prenoms = _propre(v.nom_naissance, 100), _propre(v.prenoms, 150)
    if v.civilite not in CIVILITES or v.nationalite not in NATIONALITES or v.situation_famille not in SITUATIONS:
        raise ErreurRegle("Répondez à toutes les questions de cette étape.")
    if not nom or not prenoms:
        raise ErreurRegle("Écrivez votre nom de naissance et vos prénoms, comme sur votre pièce d'identité.")
    ans = age(v.naissance_le, aujourd_hui(maintenant))
    if not 16 <= ans <= 110:
        raise ErreurRegle("Vérifiez votre date de naissance : il faut avoir au moins 16 ans.")
    pays = _propre(v.naissance_pays, 60)
    if (v.naissance_commune_id is None) == (pays is None):
        raise ErreurRegle("Choisissez votre ville de naissance dans la liste (ou votre pays si vous êtes né à l'étranger).")
    if v.naissance_commune_id is not None and db.get(Commune, v.naissance_commune_id) is None:
        raise ErreurRegle("Choisissez votre ville de naissance dans la liste.")
    if v.situation_famille in ("marie", "pacse") and v.conjoint_travaille:
        raise ErreurRegle(f"Quand le conjoint travaille dans l'entreprise, la démarche se fait sur le site de l'État : {SITE_DE_L_ETAT}")
    numero = "".join(v.numero_secu.split()).upper()
    if not numero_secu_valide(numero):
        raise ErreurRegle("Ce numéro de sécurité sociale n'est pas correct : recopiez les 15 chiffres de votre carte Vitale.")
    adresse = controler_adresse(db, ligne=v.adresse_rue, complement=None, commune_id=v.commune_id, code_postal=v.code_postal)
    mail = (v.mail or "").strip().lower()
    telephone = "".join(c for c in v.telephone or "" if c.isdigit() or c == "+")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail):
        raise ErreurRegle("Écrivez une adresse mail correcte (ex. karim.benali@example.com).")
    if len(telephone) < 10:
        raise ErreurRegle("Écrivez un numéro de téléphone correct (ex. 06 12 34 56 78).")
    dossier.civilite, dossier.nom_naissance, dossier.nom_usage, dossier.prenoms = v.civilite, nom.upper(), _propre(v.nom_usage, 100), prenoms
    dossier.naissance_le, dossier.naissance_commune_id, dossier.naissance_pays = v.naissance_le, v.naissance_commune_id, pays
    dossier.nationalite, dossier.situation_famille, dossier.numero_secu = v.nationalite, v.situation_famille, numero
    dossier.adresse_rue, dossier.commune_id, dossier.code_postal = adresse.ligne, adresse.commune.id, adresse.code_postal
    dossier.mail, dossier.telephone, dossier.modifie_le = mail, telephone, maintenant
    return dossier


# ---------- Étape 2 : votre activité ----------


def _entreprise_encore_ouverte(siren: str) -> bool:
    """D'après le répertoire de l'État ; s'il ne répond pas, on ne bloque pas (le guichet vérifiera)."""
    try:
        entreprises = service_siret.interroger(siren)
    except service_siret.ServiceIndisponible:
        return False
    return any(e.get("siren") == siren and e.get("etat_administratif") == "A" for e in entreprises)


def enregistrer_activite(db: Session, compte: Compte, a: Activite, maintenant: datetime) -> DossierCreation:
    dossier = _modifiable(db, compte)
    metier = db.get(Metier, a.metier_id)
    if metier is None or not metier.est_active:
        raise ErreurRegle("Choisissez votre métier dans la liste.")
    if metier_renvoye(db, metier):
        raise ErreurRegle(f"Pour le métier « {metier.nom} », la démarche se fait sur le site de l'État : {SITE_DE_L_ETAT}")
    description = _propre(a.description, 10_000) or ""
    mini, maxi = reglages.CREATION_DESCRIPTION
    if not mini <= len(description) <= maxi:
        raise ErreurRegle(f"Décrivez ce que vous faites en {mini} à {maxi} caractères (ex. « Dépannage et installation de plomberie »).")
    jour = aujourd_hui(maintenant)
    if not jour <= a.debut_le <= jour + reglages.CREATION_DEBUT_MAX:
        raise ErreurRegle(f"La date de début va d'aujourd'hui au {jour + reglages.CREATION_DEBUT_MAX:%d/%m/%Y}.")
    if a.lieu_travail not in LIEUX or a.activite_en_meme_temps not in ACTIVITES:
        raise ErreurRegle("Répondez à toutes les questions de cette étape.")
    local = None
    if a.lieu_travail == "local":
        if a.local_commune_id is None:
            raise ErreurRegle("Écrivez l'adresse de votre local et choisissez sa ville dans la liste.")
        local = controler_adresse(db, ligne=a.local_adresse or "", complement=None, commune_id=a.local_commune_id,
                                  code_postal=a.local_code_postal or "")
    ancien = "".join((a.ancien_siren or "").split()) or None
    if ancien is not None:
        if not re.fullmatch(r"[0-9]{9}", ancien):
            raise ErreurRegle("L'ancien numéro SIREN fait 9 chiffres (les 9 premiers d'un SIRET).")
        if _entreprise_encore_ouverte(ancien):
            raise ErreurRegle("Cette entreprise existe encore : ne la recréez pas, ajoutez son SIRET à votre profil.")
    dossier.metier_id, dossier.description, dossier.debut_le, dossier.lieu_travail = metier.id, description, a.debut_le, a.lieu_travail
    dossier.local_adresse = local.ligne if local else None
    dossier.local_commune_id = local.commune.id if local else None
    dossier.local_code_postal = local.code_postal if local else None
    dossier.nom_commercial, dossier.activite_en_meme_temps = _propre(a.nom_commercial, 100), a.activite_en_meme_temps
    dossier.ancien_siren, dossier.modifie_le = ancien, maintenant
    return dossier


# ---------- Étape 3 : vos choix ----------


def enregistrer_choix(db: Session, compte: Compte, c: Choix, maintenant: datetime) -> DossierCreation:
    dossier = _modifiable(db, compte)
    if c.periodicite not in ("mois", "trimestre"):
        raise ErreurRegle("Choisissez « chaque mois » ou « chaque trimestre ».")
    dossier.periodicite, dossier.impot_avec_cotisations = c.periodicite, c.impot_avec_cotisations
    dossier.acre_demandee, dossier.adresse_non_publique, dossier.modifie_le = c.acre_demandee, c.adresse_non_publique, maintenant
    return dossier


# ---------- Étape 4 : vos papiers ----------


def pieces_attendues(db: Session, dossier: DossierCreation, jour: date) -> list[str]:
    """Les papiers que la personne doit déposer, selon ses réponses. Ex. Karim, plombier : identité + diplôme."""
    attendues = ["identite"]
    if dossier.nationalite == "autre":
        attendues.append("titre_sejour")
    if dossier.metier_id is not None and metier_reglemente(db.get_one(Metier, dossier.metier_id)):
        attendues.append("diplome")
    if dossier.naissance_le is not None and age(dossier.naissance_le, jour) < 18:
        attendues.append("autorisation_parents")
    if dossier.lieu_travail == "local":
        attendues.append("bail")
    return attendues


def enregistrer_parents(db: Session, compte: Compte, pere: str, mere: str, maintenant: datetime) -> DossierCreation:
    """Les noms des parents figurent dans l'attestation sur l'honneur (demandé par l'administration)."""
    dossier = _modifiable(db, compte)
    pere_nom, mere_nom = _propre(pere, 100), _propre(mere, 100)
    if not pere_nom or not mere_nom or len(pere_nom) < 2 or len(mere_nom) < 2:
        raise ErreurRegle("Écrivez le nom et le prénom de votre père et de votre mère (ou « inconnu »).")
    dossier.pere_nom, dossier.mere_nom, dossier.modifie_le = pere_nom, mere_nom, maintenant
    return dossier


def _effacer_fichier(db: Session, piece: PieceDossier, maintenant: datetime) -> None:
    """Efface le papier du placard à fichiers ; la ligne PIECE_DOSSIER reste, sans fichier."""
    if piece.fichier_id is None:
        return
    fichier = db.get_one(Fichier, piece.fichier_id)
    stockage.supprimer(fichier.cle_stockage)
    piece.fichier_id, piece.efface_le = None, maintenant
    db.flush()
    db.delete(fichier)
    db.flush()


def _ranger(db: Session, compte: Compte, dossier: DossierCreation, sorte: str, pdf: bytes, maintenant: datetime) -> PieceDossier:
    """Range un PDF comme papier du dossier ; remplace celui de la même sorte s'il y en a un."""
    piece = pieces(db, dossier).get(sorte)
    if piece is not None:
        _effacer_fichier(db, piece, maintenant)
    fichier = fichiers.enregistrer(db, compte, nom_fichier=f"{sorte}.pdf", type_mime="application/pdf", contenu=pdf, maintenant=maintenant)
    if piece is None:
        piece = PieceDossier(dossier_id=dossier.id, sorte=sorte)
        db.add(piece)
    piece.fichier_id, piece.depose_le, piece.a_refaire, piece.efface_le = fichier.id, maintenant, False, None
    db.flush()
    return piece


def deposer_piece(db: Session, compte: Compte, sorte: str, *, type_mime: str, contenu: bytes, maintenant: datetime) -> DossierCreation:
    """PDF ou photo JPG ; la photo est rangée dans un PDF (le guichet n'accepte que des PDF)."""
    dossier = _modifiable(db, compte)
    if sorte not in PIECES_DEPOSEES or sorte not in pieces_attendues(db, dossier, aujourd_hui(maintenant)):
        raise ErreurRegle("Ce papier n'est pas demandé pour votre dossier.")
    fichiers.verifier(contenu, type_mime, types_acceptes=reglages.CREATION_PIECE_TYPES,
                      taille_max_octets=reglages.CREATION_PIECE_TAILLE_MAX_OCTETS)
    pdf = pdf_pieces.jpeg_en_pdf(contenu) if type_mime == "image/jpeg" else contenu
    _ranger(db, compte, dossier, sorte, pdf, maintenant)
    dossier.modifie_le = maintenant
    return dossier


def lire_piece(db: Session, compte: Compte, sorte: str) -> bytes:
    """Seule la personne relit ses papiers."""
    dossier = dernier(db, compte)
    piece = pieces(db, dossier).get(sorte) if dossier else None
    if piece is None or piece.fichier_id is None:
        raise ErreurRegle("Ce papier n'existe pas (ou il a été effacé à la fin du dossier).", 404)
    return stockage.lire(db.get_one(Fichier, piece.fichier_id).cle_stockage)


# ---------- Ce qui manque ----------


def manque(db: Session, dossier: DossierCreation, jour: date) -> dict[str, list[str]]:
    """Par étape, ce qu'il reste à faire avant de pouvoir envoyer. Ex. {"papiers": ["le diplôme…"]}."""
    d = dossier
    resultat: dict[str, list[str]] = {"vous": [], "activite": [], "choix": [], "papiers": []}
    if None in (d.civilite, d.nom_naissance, d.prenoms, d.naissance_le, d.nationalite, d.situation_famille, d.numero_secu,
                d.adresse_rue, d.commune_id, d.code_postal, d.mail, d.telephone) or (d.naissance_commune_id is None and not d.naissance_pays):
        resultat["vous"].append("vos informations (étape 1)")
    if None in (d.metier_id, d.description, d.debut_le, d.lieu_travail, d.activite_en_meme_temps):
        resultat["activite"].append("votre activité (étape 2)")
    elif d.debut_le < jour and d.statut == "brouillon":
        resultat["activite"].append("la date de début, qui est passée (étape 2)")
    if None in (d.periodicite, d.impot_avec_cotisations, d.acre_demandee, d.adresse_non_publique):
        resultat["choix"].append("vos choix (étape 3)")
    deposees = pieces(db, d)
    for sorte in pieces_attendues(db, d, jour):
        piece = deposees.get(sorte)
        if piece is None or piece.fichier_id is None or piece.a_refaire:
            resultat["papiers"].append(PIECES[sorte][0])
    if not d.pere_nom or not d.mere_nom:
        resultat["papiers"].append("les noms de vos parents")
    return resultat


# ---------- Le pouvoir et l'attestation, écrits par rafals ----------


def _lieu_naissance(db: Session, d: DossierCreation) -> str:
    return db.get_one(Commune, d.naissance_commune_id).nom if d.naissance_commune_id else (d.naissance_pays or "")


def _identite(db: Session, d: DossierCreation) -> str:
    """« Karim Youssef BENALI, né le 14/03/1998 à Bordeaux, demeurant 12 rue des Lilas, 33700 Mérignac »."""
    ne = "née" if d.civilite == "madame" else "né"
    ville = db.get_one(Commune, d.commune_id).nom
    prenoms = " ".join(p.strip() for p in (d.prenoms or "").split(","))
    return (f"{prenoms} {d.nom_naissance}, {ne} le {d.naissance_le:%d/%m/%Y} à {_lieu_naissance(db, d)}, "
            f"demeurant {d.adresse_rue}, {d.code_postal} {ville}")


def texte_pouvoir(db: Session, dossier: DossierCreation, maintenant: datetime) -> str:
    soussigne = "Je soussignée" if dossier.civilite == "madame" else "Je soussigné"
    quand = maintenant.astimezone(reglages.FUSEAU_AFFICHAGE)
    return (f"{soussigne} {_identite(db, dossier)}, donne pouvoir à rafals pour effectuer en mon nom la déclaration de création "
            "de mon entreprise individuelle auprès du guichet des formalités des entreprises, et pour répondre aux demandes de "
            f"correction de ce dossier. Fait sur rafals le {quand:%d/%m/%Y} à {quand.hour} h {quand:%M}. "
            "Ce pouvoir vaut pour ce dossier seulement.")


def texte_attestation(db: Session, dossier: DossierCreation, maintenant: datetime) -> str:
    soussigne = "Je soussignée" if dossier.civilite == "madame" else "Je soussigné"
    enfant = "fille" if dossier.civilite == "madame" else "fils"
    quand = maintenant.astimezone(reglages.FUSEAU_AFFICHAGE)
    return (f"{soussigne} {_identite(db, dossier)}, {enfant} de {dossier.pere_nom} et de {dossier.mere_nom}, déclare sur "
            "l'honneur, conformément à l'article A. 123-51 du code de commerce, n'avoir fait l'objet d'aucune condamnation pénale "
            "ni de sanction civile ou administrative de nature à m'interdire de gérer, d'administrer ou de diriger une personne "
            f"morale, ou d'exercer une activité commerciale ou artisanale. Fait sur rafals le {quand:%d/%m/%Y}, signé en ligne.")


# ---------- Le dossier tel que le guichet l'attend ----------


def _adresse_guichet(commune: Commune, rue: str, code_postal: str) -> dict:
    return {"pays": "FRANCE", "codePays": "FRA", "codePostal": code_postal, "commune": commune.nom,
            "codeInseeCommune": commune.code_insee, "voie": rue}


def contenu_guichet(db: Session, dossier: DossierCreation, *, avec_fichiers: bool = True) -> dict:
    """Le dossier dans la forme du dictionnaire de données de l'INPI (création, personne physique, micro-entrepreneur).
    ⚠️ À essayer dans l'espace d'essai de l'INPI avant la mise en ligne."""
    d = dossier
    metier = db.get_one(Metier, d.metier_id)
    forme = forme_exercice(db, metier)
    domicile = _adresse_guichet(db.get_one(Commune, d.commune_id), d.adresse_rue or "", d.code_postal or "")
    etablissement = (_adresse_guichet(db.get_one(Commune, d.local_commune_id), d.local_adresse or "", d.local_code_postal or "")
                     if d.lieu_travail == "local" else domicile)
    naissance = db.get(Commune, d.naissance_commune_id) if d.naissance_commune_id else None
    simultanee = ACTIVITES[d.activite_en_meme_temps or "aucune"]
    jointes = []
    for sorte, piece in pieces(db, d).items():
        if piece.fichier_id is None:
            continue
        jointe = {"nomDocument": f"{sorte}.pdf", "typeDocument": PIECES[sorte][1], "langueDocument": "Français",
                  "documentExtension": "pdf", "path": ".personnePhysique.identite.entrepreneur.piecesJointes"}
        if avec_fichiers:
            jointe["documentBase64"] = base64.b64encode(stockage.lire(db.get_one(Fichier, piece.fichier_id).cle_stockage)).decode()
        jointes.append(jointe)
    personne = {
        "genre": CIVILITES[d.civilite or "monsieur"], "nom": d.nom_naissance, "nomUsage": d.nom_usage,
        "prenoms": [p.strip() for p in (d.prenoms or "").split(",") if p.strip()],
        "dateDeNaissance": f"{d.naissance_le:%Y-%m-%d}",
        "codeInseeGeographique": naissance.code_insee if naissance else None,
        "paysNaissance": "FRANCE" if naissance else d.naissance_pays,
        "lieuDeNaissance": None if naissance else d.naissance_pays,
        "situationMatrimoniale": SITUATIONS[d.situation_famille or "celibataire"], "numeroSecu": d.numero_secu, "formeSociale": "2",
    }
    return {
        "typeFormalite": "C", "typePersonne": "P", "referenceMandataire": f"rafals-{d.id}",
        "nomDossier": f"Création {d.nom_naissance} {d.prenoms}"[:100],
        "diffusionINSEE": "N" if d.adresse_non_publique else "O", "diffusionCommerciale": "N" if d.adresse_non_publique else "O",
        "content": {
            "natureCreation": {"dateCreation": f"{d.debut_le:%Y-%m-%d}", "microEntreprise": True, "etablieEnFrance": True,
                               "formeJuridique": "1000"},
            "personnePhysique": {
                "identite": {"entrepreneur": {
                    "descriptionEntrepreneur": personne, "adresseDomicile": domicile,
                    "contact": {"mail": d.mail, "telephone": d.telephone},
                    "regimeMicroSocial": {"optionMicroSocial": True, "periodiciteVersement": "M" if d.periodicite == "mois" else "T"},
                    "voletSocial": {"natureVoletSocial": "TNS", "demandeAcre": bool(d.acre_demandee),
                                    "activiteSimultanee": simultanee is not None, "statutExerciceActiviteSimultanee": simultanee,
                                    "indicateurActiviteAnterieure": d.ancien_siren is not None, "ancienNumeroSiren": d.ancien_siren},
                }},
                "adresseEntreprise": {"caracteristiques": {"indicateurDomicileEntrepreneur": d.lieu_travail != "local",
                                                           "ambulant": False, "domiciliataire": False},
                                      "adresse": etablissement},
                "etablissementPrincipal": {
                    "descriptionEtablissement": {"rolePourEntreprise": "2", "indicateurEtablissementPrincipal": True,
                                                 "nomCommercial": d.nom_commercial, "statutPourFormalite": "1"},
                    "adresse": etablissement, "effectifSalarie": {"emploiPremierSalarie": False},
                    "activites": [{"indicateurPrincipal": True, "rolePrincipalPourEntreprise": True, "formeExercice": forme,
                                   "descriptionDetaillee": d.description, "dateDebut": f"{d.debut_le:%Y-%m-%d}",
                                   "exerciceActivite": "P", "indicateurNonSedentaire": d.lieu_travail == "chez_clients",
                                   "origine": {"typeOrigine": "1"}}],
                },
                "optionsFiscales": {"regimeImpositionBenefices": "110" if forme == "INDEPENDANTE" else "116",
                                    "regimeImpositionTVA": "310", "optionVersementLiberatoire": bool(d.impot_avec_cotisations)},
            },
            "declarant": {"entrepriseMandataire": {"denomination": "rafals"}},
            "piecesJointes": jointes,
        },
    }


# ---------- Étape 5 : envoyer ----------


def _passer(dossier: DossierCreation, statut: str, maintenant: datetime) -> None:
    dossier.statut, dossier.statut_change_le = statut, maintenant


def _ecrire(email: str | None, sujet: str, texte: str) -> None:
    if email:
        mails.envoyer_mail(email, sujet, f"{texte}\n\nVotre dossier : {config.ADRESSE_SITE}/creer-mon-auto-entreprise")


def envoyer(db: Session, compte: Compte, *, certifie: bool, pouvoir: bool, maintenant: datetime) -> DossierCreation:
    """Karim coche les 2 cases et envoie : rafals écrit le pouvoir et l'attestation, dépose le dossier et le signe."""
    dossier = _modifiable(db, compte)
    if dossier.statut != "brouillon":
        raise ErreurRegle("Ce dossier est déjà envoyé : utilisez « Envoyer la correction ».")
    raison = empechement(db, compte)
    if raison:
        raise ErreurRegle(raison)
    restant = [m for liste in manque(db, dossier, aujourd_hui(maintenant)).values() for m in liste]
    if restant:
        raise ErreurRegle("Il manque : " + ", ".join(restant) + ".")
    if not certifie or not pouvoir:
        raise ErreurRegle("Cochez les deux cases : vous certifiez vos réponses, et vous donnez pouvoir à rafals.")
    dossier.pouvoir_texte = texte_pouvoir(db, dossier, maintenant)
    _ranger(db, compte, dossier, "pouvoir", pdf_pieces.texte_en_pdf("Pouvoir", [dossier.pouvoir_texte]), maintenant)
    _ranger(db, compte, dossier, "attestation",
            pdf_pieces.texte_en_pdf("Attestation sur l'honneur", [texte_attestation(db, dossier, maintenant)]), maintenant)
    try:
        dossier.guichet_id, dossier.guichet_numero = guichet.deposer(contenu_guichet(db, dossier))
    except guichet.GuichetIndisponible as erreur:
        for sorte in ("pouvoir", "attestation"):  # la base revient en arrière toute seule ; le placard à fichiers, non
            _effacer_fichier(db, pieces(db, dossier)[sorte], maintenant)
        raise ErreurRegle("Le guichet de l'État ne répond pas : votre dossier est gardé, réessayez dans quelques minutes.", 503) from erreur
    dossier.certifie_le = dossier.pouvoir_le = dossier.envoye_le = dossier.modifie_le = maintenant
    _passer(dossier, "envoye", maintenant)
    try:
        guichet.signer(dossier.guichet_id)
    except guichet.GuichetIndisponible:
        pass  # la tâche de fond signera au prochain passage
    journal.noter(db, auteur_id=compte.id, action="creation_envoyer", table_cible="dossier_creation", ligne_id=dossier.id,
                  apres={"guichet_id": dossier.guichet_id}, maintenant=maintenant)
    _ecrire(dossier.mail, "Votre dossier de création d'entreprise est envoyé",
            f"Bonjour,\n\nrafals a envoyé votre dossier au guichet de l'État (numéro {dossier.guichet_numero}). L'administration "
            "l'examine, en général en 1 à 4 semaines. rafals vous écrit dès qu'il y a du nouveau.")
    return dossier


def envoyer_correction(db: Session, compte: Compte, maintenant: datetime) -> DossierCreation:
    """Après une demande de l'administration : la personne a refait un papier ou corrigé une réponse."""
    dossier = _modifiable(db, compte)
    if dossier.statut != "a_corriger":
        raise ErreurRegle("L'administration n'a pas demandé de correction.")
    restant = [m for liste in manque(db, dossier, aujourd_hui(maintenant)).values() for m in liste]
    if restant:
        raise ErreurRegle("Il manque : " + ", ".join(restant) + ".")
    _ranger(db, compte, dossier, "attestation",
            pdf_pieces.texte_en_pdf("Attestation sur l'honneur", [texte_attestation(db, dossier, maintenant)]), maintenant)
    try:
        guichet.corriger(dossier.guichet_id or "", contenu_guichet(db, dossier))
    except guichet.GuichetIndisponible as erreur:
        raise ErreurRegle("Le guichet de l'État ne répond pas : votre correction est gardée, réessayez dans quelques minutes.", 503) from erreur
    dossier.motif, dossier.corriger_avant_le, dossier.modifie_le = None, None, maintenant
    _passer(dossier, "en_examen", maintenant)
    journal.noter(db, auteur_id=compte.id, action="creation_corriger", table_cible="dossier_creation", ligne_id=dossier.id,
                  maintenant=maintenant)
    return dossier


# ---------- Suivi (tâche de fond, et bouton [Actualiser]) ----------


def effacer_sensible(db: Session, dossier: DossierCreation, maintenant: datetime) -> None:
    """Numéro de sécurité sociale, noms des parents et papiers : effacés à la fin du dossier. Le reste est gardé."""
    for piece in pieces(db, dossier).values():
        _effacer_fichier(db, piece, maintenant)
    dossier.numero_secu = dossier.pere_nom = dossier.mere_nom = None
    dossier.sensible_efface_le = maintenant


def _siret_du_siren(siren: str) -> str | None:
    """Le guichet donne parfois seulement le SIREN (9 chiffres) : le SIRET du siège est dans le répertoire de l'État."""
    try:
        entreprises = service_siret.interroger(siren)
    except service_siret.ServiceIndisponible:
        return None
    return next(((e.get("siege") or {}).get("siret") for e in entreprises if e.get("siren") == siren), None)


def _accepter(db: Session, dossier: DossierCreation, siret: str, maintenant: datetime) -> None:
    compte = db.get_one(Compte, dossier.compte_id)
    dossier.siret_recu = siret
    _passer(dossier, "accepte", maintenant)
    profil = profil_de(db, compte)
    demonstration = guichet.en_demonstration(dossier.guichet_id)
    if profil is not None and not profil.siret and not demonstration:
        # Le SIRET vient de l'État lui-même : il est vérifié d'office
        profil.siret, profil.siret_statut, profil.siret_verifie_le = siret, "verifie", maintenant
        if profil.declaration_periodicite is None:
            profil.declaration_periodicite = dossier.periodicite  # les rappels URSSAF partent tout seuls (lot 6.3)
    journal.noter(db, auteur_id=None, action="creation_acceptee", table_cible="dossier_creation", ligne_id=dossier.id,
                  apres={"siret": siret, "profil_id": profil.id if profil else None}, maintenant=maintenant)
    effacer_sensible(db, dossier, maintenant)
    suite = ("Il est ajouté à votre profil : vous pouvez activer le paiement par carte." if profil is not None and not demonstration
             else "Gardez-le : vous le donnerez en créant votre profil de prestataire.")
    _ecrire(dossier.mail, "Votre auto-entreprise est créée",
            f"Bonjour,\n\nVotre auto-entreprise est créée. Votre numéro SIRET : {siret}. {suite}\n\n"
            "Pensez à créer votre espace sur autoentrepreneur.urssaf.fr pour déclarer votre chiffre d'affaires.")


def _pieces_a_refaire(db: Session, dossier: DossierCreation, codes: tuple[str, ...]) -> None:
    for sorte, piece in pieces(db, dossier).items():
        piece.a_refaire = PIECES[sorte][1] in codes


def _deja_note(db: Session, dossier: DossierCreation, action: str, depuis: datetime) -> bool:
    return db.scalar(select(JournalAction.id).where(
        JournalAction.table_cible == "dossier_creation", JournalAction.ligne_id == dossier.id, JournalAction.action == action,
        JournalAction.fait_le >= depuis).limit(1)) is not None


def actualiser(db: Session, dossier: DossierCreation, maintenant: datetime) -> bool:
    """Demande au guichet où en est le dossier et applique sa réponse. Renvoie True si quelque chose a changé."""
    if dossier.statut not in ("envoye", "en_examen", "a_corriger") or not dossier.guichet_id:
        return False
    etat = guichet.etat(dossier.guichet_id)
    if etat.a_signer:
        guichet.signer(dossier.guichet_id)
    if etat.statut == "accepte":
        siret = etat.siret or (_siret_du_siren(etat.siren) if etat.siren else None)
        if siret is None:  # accepté, mais le SIRET n'est pas encore publié : on repassera
            return False
        _accepter(db, dossier, siret, maintenant)
        return True
    if etat.statut == dossier.statut:
        return False
    if etat.statut == "a_corriger":
        dossier.motif = etat.motif or "L'administration demande une correction."
        dossier.corriger_avant_le = aujourd_hui(maintenant) + reglages.CREATION_DELAI_CORRECTION
        _pieces_a_refaire(db, dossier, etat.pieces_refusees)
        _passer(dossier, "a_corriger", maintenant)
        _ecrire(dossier.mail, "Votre dossier de création : une correction est demandée",
                f"Bonjour,\n\nL'administration demande une correction avant le {dossier.corriger_avant_le:%d/%m/%Y} :\n"
                f"« {dossier.motif} »\n\nOuvrez votre dossier sur rafals pour corriger.")
    elif etat.statut in ("refuse", "ferme"):
        dossier.motif = etat.motif or ("Dossier refusé par l'administration." if etat.statut == "refuse"
                                       else "Dossier fermé : la correction n'a pas été faite à temps.")
        dossier.corriger_avant_le = None
        _passer(dossier, etat.statut, maintenant)
        effacer_sensible(db, dossier, maintenant)
        _ecrire(dossier.mail, "Votre dossier de création est " + ("refusé" if etat.statut == "refuse" else "fermé"),
                f"Bonjour,\n\n{dossier.motif}\n\nVous pouvez recommencer un dossier sur rafals quand vous voulez.")
    else:
        _passer(dossier, etat.statut, maintenant)
    journal.noter(db, auteur_id=None, action="creation_suivi", table_cible="dossier_creation", ligne_id=dossier.id,
                  apres={"statut": dossier.statut}, maintenant=maintenant)
    return True


def suivre(db: Session, maintenant: datetime) -> dict[str, int]:
    """Toutes les heures : suit chaque dossier envoyé, rappelle les corrections à faire, efface les brouillons abandonnés.
    Une erreur sur un dossier n'arrête pas les autres."""
    bilan = {"changes": 0, "rappels": 0, "brouillons_effaces": 0, "erreurs": 0}
    jour = aujourd_hui(maintenant)
    for dossier in db.scalars(select(DossierCreation).where(DossierCreation.statut.in_(("envoye", "en_examen", "a_corriger")))).all():
        try:
            with db.begin_nested():
                bilan["changes"] += actualiser(db, dossier, maintenant)
        except Exception:
            bilan["erreurs"] += 1
            continue
        limite = dossier.corriger_avant_le
        if (dossier.statut == "a_corriger" and limite is not None and jour <= limite <= jour + reglages.CREATION_RAPPEL_CORRECTION
                and not _deja_note(db, dossier, "creation_rappel_correction", dossier.statut_change_le)):
            _ecrire(dossier.mail, "Votre dossier de création : correction à faire avant le " + f"{limite:%d/%m/%Y}",
                    f"Bonjour,\n\nIl vous reste jusqu'au {limite:%d/%m/%Y} pour corriger votre dossier :\n« {dossier.motif} »\n\n"
                    "Passé cette date, l'administration ferme le dossier.")
            journal.noter(db, auteur_id=None, action="creation_rappel_correction", table_cible="dossier_creation",
                          ligne_id=dossier.id, maintenant=maintenant)
            bilan["rappels"] += 1
    abandonnes = db.scalars(select(DossierCreation).where(
        DossierCreation.statut == "brouillon", DossierCreation.modifie_le < maintenant - reglages.CREATION_BROUILLON_ABANDONNE)).all()
    for dossier in abandonnes:
        _effacer_brouillon(db, dossier, None, maintenant)
        bilan["brouillons_effaces"] += 1
    return bilan
